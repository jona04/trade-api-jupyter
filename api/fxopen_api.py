import requests
import constants.defs as defs
import json
import time
import pandas as pd
from dateutil import parser
from datetime import datetime as dt
import datetime

from infrastructure.quotehistory_collection import quotehistoryCollection as qc
from models.open_trade import OpenTrade

class FxOpenApi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(defs.SECURE_HEADER)
        self.last_req_time = dt.now()

    def save_response(self, resp, filename):
        with open(f'./api/data/{filename}.json', 'w') as f:
            d = {}
            d['local_request_data'] = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            d['response_data'] = resp.json()
            f.write(json.dumps(d, indent=2))


    def throttle(self):
        el_s = (dt.now() - self.last_req_time).total_seconds()
        if el_s < defs.THROTTLE_TIME:
            time.sleep(defs.THROTTLE_TIME - el_s)
        self.last_req_time = dt.now()


    def make_request(self, url, verb='get', code=200, params=None, data=None, headers=None, save_filename=""):
        
        self.throttle()
        
        full_url = f"{defs.OPENFX_URL}/{url}"
        
        if data is not None:
            data = json.dumps(data)

        try:
            response = None
            if verb == "get":
                response = self.session.get(full_url, params=params, data=data, headers=headers)
            if verb == "post":
                response = self.session.post(full_url, params=params, data=data, headers=headers)
            if verb == "put":
                response = self.session.put(full_url, params=params, data=data, headers=headers)
            if verb == "delete":
                response = self.session.delete(full_url, params=params, data=data, headers=headers)
            
            if response == None:
                return False, {'error': 'verb not found'}
            
            if save_filename != "":
                self.save_response(response, save_filename)

            if response.status_code == code:
                return True, response.json()
            else:
                return False, response.json()
            
        except Exception as error:
            return False, {'Exception': error}
        
    def get_account(self):
        url = f"account"
        ok, data = self.make_request(url, save_filename="account")

        if ok is True:
            return data
        else:
            print("Error get account")
            return None
        

    def get_quotehistory(self, StatusGroupId='Forex'):
        url = f"symbol"
        ok, symbol_data = self.make_request(url, save_filename="symbol")

        if ok == False:
            print("Error get account instrument")
            return None
        
        # target_inst = [x for x in symbol_data if x['StatusGroupId']==StatusGroupId and len(x['Symbol']) == 6]
        target_inst = [x for x in symbol_data if len(x['Symbol']) == 6]

        url = f"quotehistory/symbols"
        ok, his_symbol_data = self.make_request(url, save_filename="quotehistory_symbols")

        final_instruments = [x for x in target_inst if x['Symbol'] in his_symbol_data]

        return final_instruments
    
    def get_price_dict(self, price_label: str, item):
        data = dict(time=pd.to_datetime(item['Timestamp'], unit='ms'))
        for ohlc in defs.LABEL_MAP.keys():
            data[f"{price_label}_{defs.LABEL_MAP[ohlc]}"]=item[ohlc]
        return data
    
    def merge_bid_ask(self, bid_data, ask_data):
        ask_bars = ask_data["Bars"]
        bid_bars = bid_data["Bars"]

        if len(bid_bars)  == 0 or len(ask_bars) == 0:
            return pd.DataFrame()
        
        AvailableTo = pd.to_datetime(bid_data['AvailableTo'], unit='ms')

        bids = [self.get_price_dict('bid', item) for item in bid_bars]
        asks = [self.get_price_dict('ask', item) for item in ask_bars]
        
        # now merge on time - the assumption here is we have the same time values for both. it would be weird if we didn't
        df_bid = pd.DataFrame.from_dict(bids)
        df_ask = pd.DataFrame.from_dict(asks)
        df_merged = pd.merge(left=df_bid, right=df_ask, on='time')   
        
        # FINALLY calcuate the mid, and we are done
        for i in ['_o', '_h', '_l', '_c']:
            df_merged[f'mid{i}'] = (df_merged[f'ask{i}'] - df_merged[f'bid{i}']) / 2 + df_merged[f'bid{i}']
        
        if df_merged.shape[0] > 0 and df_merged.iloc[-1].time == AvailableTo:
            df_merged = df_merged[:-1]

        return df_merged

    def get_candles_df(self, pair, count=-10, granularity="H1", date_f=None):
        ok, data = self.fetch_candles(pair, count=count, granularity=granularity, ts_f=date_f)
        
        if ok == False:
            return None
        
        data_bid, data_ask = data

        if len(data_bid) != len(data_ask):
            return None
        
        if data_ask is None:
            return None
        
        if ("Bars" in data_ask == False) or ("Bars" in data_bid == False):
            return pd.DataFrame()
        
        return self.merge_bid_ask(data_bid, data_ask)
        

    def fetch_candles(self, pair, count=-10, granularity="H1", ts_f=None):
        if ts_f is None:
            ts_f=int(pd.Timestamp(dt.now(datetime.UTC)).timestamp() * 1000)

        if isinstance(ts_f, datetime.datetime):
            ts_f = int(ts_f.timestamp()*1000)

        params = dict(
            timestamp=ts_f,
            count=count
        )

        if count < 0:
            params['count'] = count+1

        base_url = f'quotehistory/{pair}/{granularity}/bars/'
        
        ok_bid, bid_data = self.make_request(base_url+"bid", params=params, save_filename="bids")
        ok_ask, ask_data = self.make_request(base_url+"ask", params=params, save_filename="asks")

        if ok_bid == True and ok_ask == True:
            return True, [bid_data, ask_data]

        return False, None        
        
    def last_complete_candle(self, pair, granularity):
        df = self.get_candles_df(pair, granularity=granularity)
        if df.shape[0] == 0:
            return None
        return df.iloc[-1].time
    

    def place_trade(self, pair_name: str, amount: int, direction: int,
                    stop_loss: float=None, take_profit: float=None):
    

        dir_str = "Buy" if direction == defs.BUY else "Sell"

        url = f"trade"

        instrument = qc.quotehistory_dict[pair_name]
        data = dict(
            Type="Market",
            Symbol=pair_name, 
            Amount=amount,
            Side=dir_str
        )

        if stop_loss is not None:
            data['StopLoss'] = round(stop_loss, instrument.displayPrecision)

        if take_profit is not None:
            data['TakeProfit'] = round(take_profit, instrument.displayPrecision)
            
        print(f"place trade args: {pair_name} {amount} {direction} {stop_loss} {take_profit}")
        print("Place Trade:", data)

        ok, response = self.make_request(url, verb="post", data=data, code=200)

        print(ok, response)

        if 'RemainingAmount' in response and response['RemainingAmount'] != 0:
            return response['Id']
        else:
            return None


    def get_open_trade(self, trade_id):
            url = f"trade/{trade_id}"
            ok, response = self.make_request(url)

            if ok == True and 'Id' in response:
                return OpenTrade(response)


    def get_open_trades(self):
        url = f"trade"
        ok, response = self.make_request(url)

        if ok == True:
            return [OpenTrade(x) for x in response]
            

    def close_trade(self, trade_id):
        url = f"trade"

        params ={
            "trade.type": "Close",
            "trade.id": trade_id
        }

        ok, _ = self.make_request(url, verb="delete", params=params, code=200)

        if ok == True:
            print(f"Closed {trade_id} successfully")
        else:
            print(f"Failed to close {trade_id}")

        return ok