from datetime import datetime, timedelta
from collections import deque
import pandas as pd
from db.db import DataDB
from binance.client import Client

from pytz import UTC

import os
from dotenv import load_dotenv 
print(load_dotenv("./constants/.env"))

api_key = os.environ.get('BINANCE_KEY')
secret_key = os.environ.get('BINANCE_SECRET')

# Conexão com o MongoDB
db = DataDB()

class LongShortTrader:
    def __init__(self, symbol, bar_length, ema_s, units, quote_units, position=0):
        self.symbol = symbol
        self.bar_length = bar_length
        self.available_intervals = [
            "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"
        ]
        self.units = units
        self.quote_units = quote_units
        self.position = position
        self.trades = 0
        self.trade_values = []
        self.opened_trades = deque()
        self.closed_trades = deque()
        self.NONE = 0
        self.data = pd.DataFrame()

    def get_most_recent(self, symbol, interval, days):
        now = datetime.now(UTC)
        past = str(now - timedelta(days=days))

        client = Client(api_key = api_key, api_secret = secret_key, tld = "com")
        bars = client.get_historical_klines(
            symbol=symbol, interval=interval, start_str=past, end_str=None, limit=1000
        )
        df = pd.DataFrame(bars)
        df["Date"] = pd.to_datetime(df.iloc[:, 0], unit="ms")
        df.columns = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time",
                      "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume",
                      "Taker Buy Quote Asset Volume", "Ignore", "Date"]
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        df["Time"] = df["Date"]
        df.set_index("Date", inplace=True)
        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df["Complete"] = [True for _ in range(len(df) - 1)] + [False]
        
        self.data = df

    def stream_candles(self, msg):
        event_time = pd.to_datetime(msg["E"], unit="ms")
        start_time = pd.to_datetime(msg["k"]["t"], unit="ms")
        first = float(msg["k"]["o"])
        high = float(msg["k"]["h"])
        low = float(msg["k"]["l"])
        close = float(msg["k"]["c"])
        volume = float(msg["k"]["v"])
        complete = msg["k"]["x"]

        # Atualizar o DataFrame com o novo candle
        self.data.loc[start_time] = [first, high, low, close, volume, start_time, complete]

        # Salvar no MongoDB e processar estratégia ao final do candle
        if complete:
            self.save_candle_to_db()
            self.define_strategy()
            self.execute_trades()

    def save_candle_to_db(self):
        candle_data = self.data.iloc[-1].to_dict()
        db.add_one(f"bot_{self.symbol}",candle_data)
        print(f"Candle salvo para {self.symbol}: {candle_data}")

    def define_strategy(self):
        # Implementar lógica da estratégia
        pass

    def execute_trades(self):
        # Implementar lógica de execução de trades
        pass
