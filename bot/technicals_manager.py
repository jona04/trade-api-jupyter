import pandas as pd
from models.trade_decision import TradeDecision

from technicals.indicators import BollingerBands

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)


from api.fxopen_api import FxOpenApi
from models.trade_settings import TradeSettings
import constants.defs as defs

ADDROWS = 20

def apply_signal_short1(row, trade_settings: TradeSettings):
    if row.SPREAD < trade_settings.maxspread and row.DELTA1 >= 0 and row.DELTA1_PREV < 0:
        return defs.BUY
    elif row.SPREAD < trade_settings.maxspread and row.DELTA1 < 0 and row.DELTA1_PREV >= 0:
        return defs.SELL
    return defs.NONE

def apply_signal_short2(row, trade_settings: TradeSettings):
    if row.SPREAD < trade_settings.maxspread and row.DELTA2 >= 0 and row.DELTA2_PREV < 0:
        return defs.BUY
    elif row.SPREAD < trade_settings.maxspread and row.DELTA2 < 0 and row.DELTA2_PREV >= 0:
        return defs.SELL
    return defs.NONE

# def apply_signal_short3(row, trade_settings: TradeSettings):
#     if row.SPREAD < trade_settings.maxspread and row.DELTA3 >= 0 and row.DELTA3_PREV < 0:
#         return defs.BUY
#     elif row.SPREAD < trade_settings.maxspread and row.DELTA3 < 0 and row.DELTA3_PREV >= 0:
#         return defs.SELL
#     return defs.NONE

def apply_signal_short4(row, trade_settings: TradeSettings):
    if row.SPREAD < trade_settings.maxspread and row.DIRECTION > 0 and row.DELTA1 >= 0 and row.DELTA1_PREV < 0:
        return defs.BUY
    elif row.SPREAD < trade_settings.maxspread and row.DIRECTION < 0 and row.DELTA1 < 0 and row.DELTA1_PREV >= 0:
        return defs.SELL
    return defs.NONE

def apply_take_profit(row, trade_settings: TradeSettings):
    
    if row.SIGNAL != defs.NONE:
        if row.SIGNAL == defs.BUY:
            return row.ask_c + (trade_settings.pip_value*trade_settings.TP)
        else:
            return row.bid_c - (trade_settings.pip_value*trade_settings.TP)
    else:
        return 0.0
    
def apply_stop_loss_fixed(row, trade_settings: TradeSettings):
    
    if row.SIGNAL != defs.NONE:
        if row.SIGNAL == defs.BUY:
            return row.ask_c - (trade_settings.pip_value*trade_settings.SL)
        elif row.SIGNAL == defs.SELL:
            return row.bid_c + (trade_settings.pip_value*trade_settings.SL)
    else:
        return 0.0

def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):

    df.reset_index(drop=True, inplace=True)
    df['PAIR'] = pair
    df['SPREAD'] = (df.ask_c - df.bid_c) / trade_settings.pip_value

    ema_1 = trade_settings.ema1
    ema_2 = trade_settings.ema2
    ema_3 = trade_settings.ema3

    df[f'EMA_{ema_1}'] = df.mid_c.ewm(span=ema_1, min_periods=ema_1).mean()
    df[f'EMA_{ema_2}'] = df.mid_c.ewm(span=ema_2, min_periods=ema_2).mean()
    df[f'EMA_{ema_3}'] = df.mid_c.ewm(span=ema_3, min_periods=ema_3).mean()
    df['DIRECTION'] = df[f'EMA_{ema_2}'] - df[f'EMA_{ema_3}']
    
    df['DELTA1'] = df[f'EMA_{ema_1}'] - df[f'EMA_{ema_2}']
    df['DELTA1_PREV'] = df.DELTA1.shift(1)
    
    df['DELTA2'] = df[f'EMA_{ema_1}'] - df[f'EMA_{ema_3}']
    df['DELTA2_PREV'] = df.DELTA2.shift(1)
    
    # df['donchian_high'] = df['mid_c'].rolling(window=400).max()
    # df['donchian_low'] = df['mid_c'].rolling(window=400).min()
    # df['donchian_mid'] = (df['donchian_high'] + df['donchian_low']) / 2
    # df['DELTA3'] = df[f'EMA_{ema_1}'] - df[f'donchian_mid']
    # df['DELTA3_PREV'] = df.DELTA3.shift(1)

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    df['SIGNAL'] = df.apply(apply_signal_short4, axis=1, trade_settings=trade_settings)
    df['TP'] = df.apply(apply_take_profit, axis=1, trade_settings=trade_settings)
    df['SL'] = df.apply(apply_stop_loss_fixed, axis=1, trade_settings=trade_settings)

    log_cols = ['PAIR', 'time', 'mid_c', 'ask_c','bid_c', 'SPREAD', 'SIGNAL', 
                'DIRECTION', 'DELTA1', 'DELTA1_PREV', 'DELTA2', 'DELTA2_PREV']
    log_message(f"process_candles:\n{df[log_cols].tail()}", pair)

    return df[log_cols].iloc[-1]


def fetch_candles(pair, row_count, candle_time, granularity,
                    api: FxOpenApi, log_message):

    df = api.get_candles_df(pair, count=row_count, granularity=granularity)
    
    if df is None or df.shape[0] == 0:
        log_message("tech_manager fetch_candles failed to get candles", pair)
        return None
    
    if df.iloc[-1].time != candle_time:
        log_message(f"tech_manager fetch_candles {df.iloc[-1].time} not correct", pair)
        return None

    return df

def get_trade_decision(candle_time, pair, granularity, api: FxOpenApi, 
                            trade_settings: TradeSettings, log_message):

    max_rows = (trade_settings.ema3 + ADDROWS) * -1

    log_message(f"tech_manager: max_rows:{max_rows} candle_time:{candle_time} granularity:{granularity}", pair)

    df = fetch_candles(pair, max_rows, candle_time,  granularity, api, log_message)

    if df is not None:
        last_row = process_candles(df, pair, trade_settings, log_message)
        return TradeDecision(last_row)

    return None


