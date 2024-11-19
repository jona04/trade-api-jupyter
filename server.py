from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import http
import pandas as pd

from technicals.indicators import Donchian
from api.web_options import get_options
from db.db import DataDB

import asyncio
from binance import BinanceSocketManager, AsyncClient
from trader import LongShortTrader
from contextlib import asynccontextmanager


class TraderManager:
    """Class to manage active trader instances and background tasks."""
    def __init__(self):
        self.active_trader_instances = {}
        self.background_tasks = []
        self.client = None
        self.bm = None

    async def init_binance_client(self):
        """Initialize Binance client and socket manager."""
        self.client = await AsyncClient.create()
        self.bm = BinanceSocketManager(self.client)

    async def close_binance_client(self):
        """Close Binance client and cancel background tasks."""
        for task in self.background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Remover todos os registros de "active_traders" do MongoDB
        db = DataDB
        db.delete_many("active_traders")
    
        await self.client.close_connection()


trader_manager = TraderManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await trader_manager.init_binance_client()
    yield
    await trader_manager.close_binance_client()

app = FastAPI(lifespan=lifespan)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def add_timestr(df):
    """Add formatted time string to DataFrame."""
    df['sTime'] = df['time'].dt.strftime("s%y-%m-%d %H:%M")
    return df
        
def get_response(data, message="Error getting data", status_code=404):
    """Return JSON response or raise HTTP exception if data is None."""
    if data is None:
        raise HTTPException(status_code=status_code, detail=message)
    return data

@app.get("/api/options")
def get_account():
    """Get account options."""
    return get_response(get_options(), message="Options not found")

@app.get("/api/prices-candle-db/{pair}/{granularity}/{count}")
def get_prices_candle_db(pair: str, granularity: str, count: int):
    """Fetch historical candle data from database."""
    db = DataDB()
    data = db.query_all_list(f'{pair}_{granularity}', count)
    return get_response(add_timestr(data), message="Candle data not found")

@app.get("/api/technicals/indicator/donchian/{pair}/{granularity}/{count}/{window}")
def indicator_donchian(pair: str, granularity: str, count: int, window: int):
    """Calculate Donchian indicator for specified pair and timeframe."""
    db = DataDB()
    df = pd.DataFrame(db.query_all(f'{pair}_{granularity}', count))
    df = Donchian(df, window).dropna().reset_index(drop=True)
    return get_response(add_timestr(df).to_dict("list"), message="Donchian data not found")

@app.post("/start_trading/{symbol}")
async def start_trading(symbol: str, bar_length: str, ema_s: int, units: float, quote_units: float, historical_days: int):
    """Start a trading session for a specific symbol."""
    db = DataDB()
    if db.query_single("active_traders", symbol=symbol) is None:
        trader = LongShortTrader(symbol, bar_length, ema_s, units, quote_units)
        trader.get_most_recent(symbol=symbol, interval=bar_length, days=historical_days)
        trader_manager.active_trader_instances[symbol] = trader
        
        db.add_one("active_traders", {
            "symbol": symbol,
            "bar_length": bar_length,
            "units": units,
            "quote_units": quote_units,
            "start_time": datetime.now()
        })
        
        task = asyncio.create_task(stream_data(symbol))
        trader_manager.background_tasks.append(task)
        return get_response({"message": f"Trading started for {symbol} with interval {bar_length}"})
    
    return get_response({"message": f"Trading is already running for {symbol}"}, status_code=400)

async def stream_data(symbol: str):
    """Stream data from Binance for the specified symbol."""
    trader = trader_manager.active_trader_instances[symbol]
    async with trader_manager.bm.kline_socket(symbol=symbol, interval=trader.bar_length) as tscm:
        while True:
            msg = await tscm.recv()
            trader.stream_candles(msg)

@app.post("/stop_trading/{symbol}")
async def stop_trading(symbol: str):
    """Stop trading session for a specific symbol."""
    db = DataDB()
    if db.query_single("active_traders", symbol=symbol):
        db.delete_single("active_traders", symbol=symbol)
        trader_manager.active_trader_instances.pop(symbol, None)
        return get_response({"message": f"Trading stopped for {symbol}"})
    
    return get_response({"message": f"No active trading session for {symbol}"}, status_code=404)

@app.get("/active_traders")
async def get_active_traders():
    """List all active traders."""
    db = DataDB()
    active_traders = list(db.query_all("active_traders"))
    return get_response({"active_traders": active_traders}, message="No active traders found")
