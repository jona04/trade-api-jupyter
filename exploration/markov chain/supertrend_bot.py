import os
from dotenv import load_dotenv 
import ta
import time
import pandas as pd
from binance.client import Client
from telegram import Bot
import asyncio

# Configurar pandas para exibir células de DataFrame sem quebra de linha
pd.set_option('display.max_colwidth', None)  # Mostra o conteúdo completo das colunas
pd.set_option('display.expand_frame_repr', False)  # Evita quebra horizontal

load_dotenv("../../constants/.env")
api_key = os.environ.get('BINANCE_KEY')
secret_key = os.environ.get('BINANCE_SECRET')

TELEGRAM_BOT_TOKEN = '7890593693:AAHTOAtCWnuLMT-fAF1qRw2ZW2yOTvrxF-Q'
CHAT_ID = '-4585946319'

#Define bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Inicializa o cliente da Binance para futuros
client = Client(api_key, secret_key)

last_trend = 1

async def send_message(text, chat_id):
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)

async def run_bot(messages, chat_id):
    text = '\n'.join(messages)
    await send_message(text, chat_id)


def calculate_supertrend(df, atr_multiplier=3, atr_period=15):
    """
    Cálculo básico do SuperTrend para um DataFrame já consolidado.

    Args:
        df (pd.DataFrame): DataFrame contendo 'High', 'Low', e 'Close'.
        atr_multiplier (float): Multiplicador para o cálculo das bandas.
        atr_period (int): Período para o cálculo do ATR.

    Returns:
        pd.DataFrame: DataFrame com colunas adicionais para SuperTrend, Upperband e Lowerband.
    """
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=atr_period)

    # Cálculo das bandas básicas
    avg_high_low = (df['High'] + df['Low']) / 2
    df['BasicUpperband'] = avg_high_low + (atr_multiplier * df['ATR'])
    df['BasicLowerband'] = avg_high_low - (atr_multiplier * df['ATR'])

    basic_upperband = df['BasicUpperband'].values
    basic_lowerband = df['BasicLowerband'].values
    
    # Inicializar listas para bandas superiores e inferiores ajustadas
    upper_band = [df['BasicUpperband'].iloc[0]]
    lower_band = [df['BasicLowerband'].iloc[0]]
    
    # Ajustar bandas com base nas condições de cruzamento
    for i in range(1, len(df)):
        # Ajuste da banda superior
        if (basic_upperband[i] < upper_band[i - 1]) or (df['Close'].iloc[i - 1] > upper_band[i - 1]):
            upper_band.append(basic_upperband[i])
        else:
            upper_band.append(upper_band[i - 1])

        # Ajuste da banda inferior
        if (basic_lowerband[i] > lower_band[i - 1]) or (df['Close'].iloc[i - 1] < lower_band[i - 1]):
            lower_band.append(basic_lowerband[i])
        else:
            lower_band.append(lower_band[i - 1])

    # Adicionar bandas ajustadas ao DataFrame
    df['Upperband'] = upper_band
    df['Lowerband'] = lower_band

    # Determinar a tendência e o SuperTrend
    trend = [1]  # Inicializando tendência: 1 = Alta, -1 = Baixa
    supertrend = [df['Upperband'].iloc[0]]  # Inicializando SuperTrend

    close = df['Close'].values
    
    for i in range(1, len(df)):
        # Atualizar tendência
        if trend[i - 1] == 1 and close[i] < lower_band[i]:
            trend.append(-1)
        elif trend[i - 1] == -1 and close[i] > upper_band[i]:
            trend.append(1)
        else:
            trend.append(trend[i - 1])

        # Atualizar SuperTrend
        if trend[i] == -1:
            supertrend.append(upper_band[i])
        else:
            supertrend.append(lower_band[i])

    df['Trend'] = trend
    df['SuperTrend'] = supertrend

    # Remover colunas temporárias
    df.drop(['BasicUpperband', 'BasicLowerband'], axis=1, inplace=True)

    return df

def supertrend(df, atr_multiplier=3, atr_period=15, new_timeframe=1):
    """
    Método principal para calcular o SuperTrend com suporte a timeframes maiores.

    Args:
        df (pd.DataFrame): DataFrame contendo 'High', 'Low', e 'Close'.
        atr_multiplier (float): Multiplicador para o cálculo das bandas.
        atr_period (int): Período para o cálculo do ATR.
        new_timeframe (int): Número de candles para consolidar (ex: 60 para 1 hora em candles de 1 minuto).

    Returns:
        pd.DataFrame: DataFrame original com colunas adicionais para SuperTrend.
    """
    if new_timeframe > 1:
        # Agrupar os dados
        df_grouped = df.copy()
        df_grouped['group'] = (df_grouped.index // new_timeframe)
        
        grouped = df_grouped.groupby('group').agg({
            'High': 'max',
            'Low': 'min',
            'Close': 'last'
        }).reset_index(drop=True)
        
        # Calcular o SuperTrend no timeframe agrupado
        grouped = calculate_supertrend(grouped, atr_multiplier=atr_multiplier, atr_period=atr_period)
        
        # Interpolar os valores calculados para o dataframe original
        df[f'Upperband_{new_timeframe}'] = grouped['Upperband'].repeat(new_timeframe).iloc[:len(df)].values
        df[f'Lowerband_{new_timeframe}'] = grouped['Lowerband'].repeat(new_timeframe).iloc[:len(df)].values
        df[f'Trend_{new_timeframe}'] = grouped['Trend'].repeat(new_timeframe).iloc[:len(df)].values
        df[f'SuperTrend_{new_timeframe}'] = grouped['SuperTrend'].repeat(new_timeframe).iloc[:len(df)].values
    else:
        # Calcular o SuperTrend no timeframe original
        df = calculate_supertrend(df, atr_multiplier=atr_multiplier, atr_period=atr_period)

    return df

def get_one_minute_candles(symbol: str, limit: int) -> pd.DataFrame:
    """
    Obtém candles de 1 minuto do mercado futuro da Binance.
    
    Args:
        symbol (str): O símbolo do par de moedas (ex.: "BTCUSDT").
        limit (int): A quantidade de candles completos a retornar.
        
    Returns:
        pd.DataFrame: DataFrame contendo os candles completos, com colunas:
                      ['time', 'open', 'high', 'low', 'close', 'volume']
    """
    # Obtém os candles de 1 minuto (Klines) do mercado futuro
    candles = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=limit)
    
    # Processa os candles e retorna apenas os completos
    df = pd.DataFrame(candles, columns=[
        'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
        'Close time', 'Quote asset volume', 'Number of trades', 
        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
    ])
    
    # Filtra os dados necessários
    df = df[["Time", 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    # Converte o tempo para datetime e os valores numéricos para float
    df["Time"] = pd.to_datetime(df["Time"], unit="ms")
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    
    return df

def on_candle_closed(candle: dict):
    """
    Método chamado quando um candle é fechado.
    
    Args:
        candle (dict): Dicionário contendo os dados do candle fechado.
    """
    global df_candles
    global last_trend
    
    # Converte o candle em DataFrame e adiciona ao DataFrame global
    new_row = pd.DataFrame([candle])
    df_candles = pd.concat([df_candles, new_row], ignore_index=True)
    df_supertrend = supertrend(df_candles, atr_multiplier=3, atr_period=15, new_timeframe=10)
    
    print(df_supertrend.tail(1))

    if df_supertrend.Trend_10.values[-1] != last_trend:
        last_trend = df_supertrend.Trend_10.values[-1]

        if last_trend == 1:
            messages = ['Alerta de compra']
        else:
            messages = ['Alerta de venda']

        asyncio.run(run_bot(messages, CHAT_ID))

def stream_one_minute_candles(symbol: str):
    """
    Obtém candles de 1 minuto a cada 2 segundos e chama um método
    quando um candle é fechado.
    
    Args:
        symbol (str): O símbolo do par de moedas (ex.: "BTCUSDT").
    """
    last_candle_time = None
    
    while True:
        # Obtém o último candle
        candles = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)
        latest_candle = candles[-1]
        
        # Extrai dados do candle
        candle = {
            "Time": pd.to_datetime(latest_candle[0], unit="ms"),
            "Open": float(latest_candle[1]),
            "High": float(latest_candle[2]),
            "Low": float(latest_candle[3]),
            "Close": float(latest_candle[4]),
            "Volume": float(latest_candle[5]),
            "is_closed": latest_candle[11]  # Verifica diretamente o indicador da Binance
        }
        
        # Se o candle foi fechado e ainda não foi processado, chama o método
        if candle["is_closed"] and (last_candle_time != candle["Time"]):
            last_candle_time = candle["Time"]
            on_candle_closed({k: v for k, v in candle.items() if k != "is_closed"})
        
        # Espera 2 segundos antes de consultar novamente
        time.sleep(2)

df_candles = get_one_minute_candles("BTCUSDT", 1000)
stream_one_minute_candles("BTCUSDT")


























