from api.fxopen_api import FxOpenApi
from infrastructure.quotehistory_collection import quotehistoryCollection as qc
from infrastructure.collect_data import run_collection
from simulation.ma_cross import run_ma_sim
from simulation.ma_cross_tp import run_ma_tp_sim
from simulation.return_ma_cross import run_returned_ma_sim
from dateutil import parser
import constants.defs as defs
import time

import json

if __name__ == "__main__":
    api = FxOpenApi()
    
    # Get Symbols
    
    # api.get_quotehistory()
    # with open("api/data/symbol.json") as f:
    #     symbols = json.load(f)
    # quotehistoryCollection.CreateFile(symbols['response_data'], './data')

    # Run tests

    # run_ma_tp_sim()
    #run_ma_sim()
    #run_returned_ma_sim()

    # quotehistoryCollection.LoadQuotehistory("./data")
    # run_collection(quotehistoryCollection, api)

    # dfr = parser.parse("2024-08-12T04:00:00Z")
    # dto = parser.parse("2023-04-28T01:00:00Z")

    # # print(api.fetch_candles("BTCEUR", -10, "H1"))
    # df_candles = api.get_candles_df(pair="XAUUSD", count=-10, granularity="M5", date_f=dfr)
    # print(df_candles)


    # print(api.last_complete_candle("BTCEUR", granularity="H1"))


    # api.place_trade("BTCEUR", 0.001, defs.BUY)


    # print("Getting open")
    # ot = api.get_open_trades()

    # for t in ot:
    #     print("Got trade:", t)
    #     print("Got trade:", t.id)
    #     time.sleep(2)
    #     print("Closing...")
    #     api.close_trade(t.id)


    # time.sleep(1)
    # print("Getting open")
    # ot = api.get_open_trades()
    # print(ot)
    # print("Done")


    # quotehistoryCollection.CreateDB(api.get_quotehistory())
    # qc.LoadQuotehistoryDB()
    # print(qc.quotehistory_dict.keys())