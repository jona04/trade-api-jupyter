import pandas as pd
import plotly.graph_objects as go
from technicals.indicators import RSI
from technicals.patterns import apply_patterns
from exploration.plotting import CandlePlot

from infrastructure.quotehistory_collection import quotehistoryCollection as qc
from simulation.ema_cross_long_tp_sl_tester import EmaCrossLongTpSlTester

BUY = 1
SELL = -1
NONE = 0

def apply_signal_long(row):
    if row.DELTA >= 0 and row.DELTA_PREV < 0:
        return BUY
    elif row.DELTA < 0 and row.DELTA_PREV >= 0:
        return SELL
    return NONE


def run_pair(pair,pip_value):
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
    gt = EmaCrossLongTpSlTester(
        df_slim,
        apply_signal_long,
        pip_value,
        df_m5,
        use_spread=True
    )
    
    gt.run_test()
    return gt.df_results


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