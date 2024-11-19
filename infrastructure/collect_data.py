import pandas as pd
import datetime as dt
from dateutil import parser
import time 
from infrastructure.quotehistory_collection import QuotehistoryCollection
from api.fxopen_api import FxOpenApi

CANDLE_COUNT = 900

INCREMENTS = {
    'M1': 1 * CANDLE_COUNT,
    'M15': 15 * CANDLE_COUNT,
    'M5' : 5 * CANDLE_COUNT,
    'H1' : 60 * CANDLE_COUNT,
    'H4' : 240 * CANDLE_COUNT,
    'D1' : 1440 * CANDLE_COUNT
}

SLEEP = 0.3

def save_file(final_df: pd.DataFrame, file_prefix, granularity, pair):
    filename = f"{file_prefix}{pair}_{granularity}.pkl"

    final_df.drop_duplicates(subset=['time'], inplace=True)
    final_df.sort_values(by='time', inplace=True)
    final_df.reset_index(inplace=True, drop=True)
    final_df.to_pickle(filename)

    print(f"**** {pair} {granularity}, {final_df.time.min()} {final_df.time.max()} --> {final_df.shape}")


def fetch_candles(pair, granularity, date_f: dt.datetime, api: FxOpenApi):
    
    attempts = 0

    while attempts < 3:
        
        candles_df = api.get_candles_df(
            pair,
            granularity=granularity,
            count=CANDLE_COUNT,
            date_f=date_f
        )

        if candles_df is not None:
            break

        attempts += 1

    if candles_df is not None and candles_df.empty == False:
        return candles_df
    else:
        return None

def collect_data(pair, granularity, date_f, date_t, file_prefix, api:FxOpenApi):
    
    time_step = INCREMENTS[granularity]

    from_date = parser.parse(date_f)
    end_date = parser.parse(date_t)

    candle_dfs = []

    to_date = from_date
    while to_date < end_date:

        to_date = from_date + dt.timedelta(minutes=time_step)
        if to_date > end_date:
            to_date = end_date

        candles = fetch_candles(
            pair,
            granularity,
            from_date,
            api
        )

        if candles is not None and candles.empty == False:
            print(f"{pair} {granularity}, {from_date} {candles.time.min()} {candles.time.max()} --> {candles.shape[0]} candles")
            candle_dfs.append(candles)
            if candles.time.max() > to_date:
                from_date = candles.time.max()
            else:
                from_date = to_date

        else:
            print(f"{pair} {granularity}, {from_date} {to_date} --> NO CANDLES")
            from_date = to_date

    time.sleep(SLEEP)

    if len(candle_dfs) > 0:
        final_df = pd.concat(candle_dfs)
        save_file(final_df, file_prefix, granularity, pair)
    else:
        print(f"{pair} {granularity}, {from_date} {to_date} --> NO DATA SAVED")



def run_collection(qc: QuotehistoryCollection, api:FxOpenApi):
    #  "CAD", "AUD", "CHF", "NZD"
    # our_curr = ["BTC", "ETH","EUR", "XAU","USD","GBP", "JPY"]
    our_curr = ["XAU","USD"]
    for p1 in our_curr:
        for p2 in our_curr:
            pair = f"{p1}{p2}"
            if pair in qc.quotehistory_dict.keys():
                print(pair)
                for g in ["M1"]:
                    print(pair, g)
                    collect_data(
                        pair,
                        g,
                        "2018-05-01T00:00:00",
                        "2019-12-31T00:00:00",
                        "./data/",
                        api
                    )
