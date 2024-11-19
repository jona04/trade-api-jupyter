from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

import http
import pandas as pd
import datetime as dt

from simulation.donchian_trend import DonchianTrend
from technicals.indicators import Donchian
from infrastructure.quotehistory_collection import quotehistoryCollection
from api.fxopen_api import FxOpenApi
from api.web_options import get_options
from dateutil import parser

from db.db import DataDB

import asyncio
from binance import BinanceSocketManager, AsyncClient
from trader import LongShortTrader
from contextlib import asynccontextmanager


# Dicionário para armazenar instâncias de LongShortTrader em memória
active_trader_instances = {}

# Lista de tasks em execução para que possamos cancelá-las no encerramento
background_tasks = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização: abrir conexão com o cliente da Binance
    global client, bm
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)

    yield  # Permite a execução do app enquanto a conexão permanece ativa

    # Finalização: Cancelar todas as tarefas em execução
    for task in background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    # Remover todos os registros de "active_traders" do MongoDB
    db = DataDB()
    db.delete_many("active_traders")
    
    # Fechar a conexão com o cliente da Binance
    await client.close_connection()

app = FastAPI(lifespan=lifespan)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def add_timestr(df):
    df['sTime'] = [dt.datetime.strftime(x, "s%y-%m-%d %H:%M") 
                    for x in df['time']]
    return df
        
def get_response(data):
    if data is None:
        return dict(message="error getting data"), http.HTTPStatus.NOT_FOUND
    else:
        return data


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/quotehistory-collection")
def get_quotehistory_collection():
    quotehistoryCollection.LoadQuotehistoryDBFiltered()
    return get_response(quotehistoryCollection.quotehistory_dict)


@app.get("/api/account")
def get_account():
    api = FxOpenApi()
    return get_response(api.get_account())


@app.get("/api/options")
def get_account():
    return get_response(get_options())


@app.get("/api/quotehistory")
def get_quotehistory():
    api = FxOpenApi()
    return get_response(api.get_quotehistory())


@app.get("/api/prices-candle-db/{pair}/{granularity}/{count}")
def get_prices_candle_db(pair: str, granularity: str, count:int):
    db = DataDB()
    data = db.query_all_list(f'{pair}_{granularity}', count)
    data = add_timestr(data)
    return get_response(data)

@app.get("/api/prices-candle/{pair}/{granularity}/{count}")
def get_prices_candle(pair: str, granularity: str, count:int):
    api = FxOpenApi()
    df = api.get_candles_df(
        pair=pair, count=count*-1, granularity=granularity
    )
    df = add_timestr(df)
    return get_response(df.to_dict("list"))

@app.get("/api/prices-candle/{pair}/{granularity}/{date_f}")
def get_prices_candle(pair: str, granularity: str, date_f: str):
    api = FxOpenApi()
    dfr = parser.parse(date_f)
    # dfr = parser.parse("2024-08-12T04:00:00Z")
    df = api.get_candles_df(
        pair=pair, count=-10, granularity=granularity, date_f=dfr
    )
    df = add_timestr(df)
    return get_response(df.to_dict("list"))

@app.get("/api/last-complete-candle/{pair}/{granularity}")
def last_complete_candle(pair: str, granularity: str):
    api = FxOpenApi()
    df_candle = api.last_complete_candle(pair=pair, granularity=granularity)

    return get_response(df_candle)


@app.get("/api/technicals/indicator/donchian/{pair}/{granularity}/{count}/{window}")
def indicator_donchian(pair: str, granularity: str, count:int, window: int):
    db = DataDB()
    df = db.query_all(f'{pair}_{granularity}', count)
    df = pd.DataFrame(df)

    df = Donchian(df, window)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    df = add_timestr(df)
    
    return get_response(df.to_dict("list"))


@app.post("/start_trading/{symbol}")
async def start_trading(symbol: str, bar_length: str, ema_s: int, units: float, quote_units: float, historical_days: int):
    db = DataDB()
    
    # Verificar se o ativo já está sendo processado
    if db.query_single("active_traders", symbol=symbol) is None:
        # Criar instância do trader e armazená-la no dicionário de instâncias ativas
        trader = LongShortTrader(symbol, bar_length, ema_s, units, quote_units)
        trader.get_most_recent(symbol=symbol, interval=bar_length, days=historical_days)
        active_trader_instances[symbol] = trader
        
        db.add_one(
            "active_traders",
            {
                "symbol": symbol,
                "bar_length": bar_length,
                "units": units,
                "quote_units": quote_units,
                "start_time": datetime.now()
            }
        )
        
        # Iniciar o stream de dados em segundo plano
        task = asyncio.create_task(stream_data(symbol))
        background_tasks.append(task)  # Adiciona a task à lista de tarefas em execução

        return {"message": f"Trading started for {symbol} with interval {bar_length}"}
    else:
        return {"message": f"Trading is already running for {symbol}"}


async def stream_data(symbol: str):
    # Usar a instância existente de LongShortTrader do dicionário
    trader = active_trader_instances[symbol]
    ts = bm.kline_socket(symbol=symbol, interval=trader.bar_length)

    async with ts as tscm:
        while True:
            msg = await tscm.recv()
            trader.stream_candles(msg)


@app.post("/stop_trading/{symbol}")
async def stop_trading(symbol: str):
    db = DataDB()
    
    # Verificar se o ativo está sendo processado
    trader_info = db.query_single("active_traders", symbol=symbol)
    if trader_info:
        # Remover o ativo do MongoDB e encerrar a instância
        db.delete_single("active_traders", symbol=symbol)
        # Remover a instância do dicionário em memória
        if symbol in active_trader_instances:
            del active_trader_instances[symbol]
        return {"message": f"Trading stopped for {symbol}"}
    else:
        return {"message": f"No active trading session for {symbol}"}


@app.get("/active_traders")
async def get_active_traders():
    db = DataDB()
    
    # Retornar lista de ativos sendo processados
    active_traders = list(db.query_all("active_traders"))
    return {"active_traders": active_traders}