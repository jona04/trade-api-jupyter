import pandas as pd
import plotly.graph_objects as go
from technicals.indicators import RSI
from technicals.patterns import apply_patterns
from exploration.plotting import CandlePlot

from infrastructure.quotehistory_collection import quotehistoryCollection as qc
from simulation.ema_cross_multi_temporal_tester import EmaCrossMultiTemporalTester

BUY = 1
SELL = -1
NONE = 0

def apply_signal_short(row):
    if row.SIGNAL > 0 and row.DELTA_SHORT >= 0 and row.DELTA_SHORT_PREV < 0:
        return BUY
    elif row.SIGNAL < 0 and row.DELTA_SHORT < 0 and row.DELTA_SHORT_PREV >= 0:
        return SELL
    return NONE

def apply_signal_long(row):
    if row.DELTA >= 0 and row.DELTA_PREV < 0:
        return BUY
    elif row.DELTA < 0 and row.DELTA_PREV >= 0:
        return SELL
    return NONE


def run_pair(pair,pip_value,use_spread=True,stop_loss = 1000, take_profit = 200, fixed_tp_sl=True):
    df_an = pd.read_pickle(f"./data/H4/{pair}_H4.pkl")
    df_m5 = pd.read_pickle(f"./data/M5/{pair}_M5.pkl")
    df_an.reset_index(drop=True, inplace=True)
    df_m5.reset_index(drop=True, inplace=True)
    ema_1 = 10
    ema_2 = 30
    df_an[f'EMA_{ema_1}'] = df_an.mid_c.ewm(span=ema_1, min_periods=ema_1).mean()
    df_an[f'EMA_{ema_2}'] = df_an.mid_c.ewm(span=ema_2, min_periods=ema_2).mean()
    df_an['donchian_high'] = df_an['mid_c'].rolling(window=20).max()
    df_an['donchian_low'] = df_an['mid_c'].rolling(window=20).min()
    df_an['DELTA'] = df_an[f'EMA_{ema_1}'] - df_an[f'EMA_{ema_2}']
    df_an['DELTA_PREV'] = df_an.DELTA.shift(1)
    df_slim = df_an.copy()
    df_slim.dropna(inplace=True)
    df_slim.reset_index(drop=True, inplace=True)

    ema_1 = 10
    ema_2 = 30
    df_m5[f'EMA_SHORT_1'] = df_m5.mid_c.ewm(span=ema_1, min_periods=ema_1).mean()
    df_m5[f'EMA_SHORT_2'] = df_m5.mid_c.ewm(span=ema_2, min_periods=ema_2).mean()
    df_m5['donchian_high_short'] = df_m5['mid_c'].rolling(window=100).max()
    df_m5['donchian_low_short'] = df_m5['mid_c'].rolling(window=100).min()
    df_m5['DELTA_SHORT'] = df_m5[f'EMA_SHORT_1'] - df_m5[f'EMA_SHORT_2']
    df_m5['DELTA_SHORT_PREV'] = df_m5.DELTA_SHORT.shift(1)
    df_m5.dropna(inplace=True)
    df_m5.reset_index(drop=True, inplace=True)

    gt = EmaCrossMultiTemporalTester(
        df_slim,
        apply_signal_long,
        apply_signal_short,
        pip_value,
        df_m5,
        use_spread=use_spread,
        LOSS_FACTOR = stop_loss,
        PROFIT_FACTOR = take_profit,
        fixed_tp_sl=fixed_tp_sl
    )
    
    # gt.run_test()
    return gt


qc.LoadQuotehistory("./data")

# pairs = ["EUR", "GBP", "JPY", "CAD", "AUD", "USD", "CHF", "NZD", "BTC", "ETH", "XAU"]
pairs = ["EUR", "GBP"]
res = []
for p1 in pairs:
    for p2 in pairs:
        p = f"{p1}{p2}"
        if p in qc.quotehistory_dict.keys():
            print(p)
            quotehistory = qc.quotehistory_dict[p]
            pip_value = quotehistory.pipLocation * 0.1
            
            res.append(dict(pair=p,res=run_pair(p,pip_value)))



for r in res:
    print(r['pair'], r['res'].result.sum())