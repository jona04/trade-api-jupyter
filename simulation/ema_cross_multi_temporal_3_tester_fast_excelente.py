import pandas as pd
import datetime as dt
import numpy as np

BUY = 1
SELL = -1
NONE = 0


# def apply_take_profit(row, pip_value, TP):
    
#     if row.SIGNAL != NONE:
#         if row.SIGNAL == BUY:
#             return row.donchian_high
#         else:
#             return row.donchian_low
#     else:
#         return 0.0

def apply_take_profit(row, pip_value, TP):
    
    if row.SIGNAL != NONE:
        if row.SIGNAL == BUY:
            return row.ask_c + (pip_value*TP)
        else:
            return row.bid_c - (pip_value*TP)
    else:
        return 0.0
    
def apply_stop_loss_fixed(row, pip_value, SL):
    
    if row.SIGNAL != NONE:
        if row.SIGNAL == BUY:
            return row.ask_c - (pip_value*SL), SL
        elif row.SIGNAL == SELL:
            return row.bid_c + (pip_value*SL), SL
    else:
        return 0.0, 0.0
    
def apply_stop_loss(row, pip_value, SL):
    
    if row.SIGNAL != NONE:
        if row.SIGNAL == BUY:
            res = ( row.ask_c - row.donchian_low ) / pip_value
            if res > SL:
                return row.ask_c - (pip_value*SL), SL
            return row.donchian_low, res
        
        elif row.SIGNAL == SELL:
            res = ( row.donchian_high - row.bid_c ) / pip_value
            if res > SL:
                return row.bid_c + (pip_value*SL), SL
            return row.donchian_high, res
    else:
        return 0.0, 0.0
    

def remove_spread(df):
    for a in ["ask", "bid"]:
        for b in ["o", "h", "l", "c"]:
            c = f"{a}_{b}"
            df[c] = df[f"mid_{b}"]

def apply_short_signals(df,sig):
    df["SIGNAL"] = df.apply(sig, axis=1)

def apply_tp_sl(df,PROFIT_FACTOR,LOSS_FACTOR,pip_location,fixed_tp_sl):
    df["TP"] = df.apply(lambda row: apply_take_profit(row,pip_location,PROFIT_FACTOR), axis=1)
    if fixed_tp_sl:
        df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss_fixed(row, pip_location,LOSS_FACTOR), axis=1))
    else:
        df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss(row, pip_location,LOSS_FACTOR), axis=1))


INDEX_bid_c = 0
INDEX_ask_c = 1
INDEX_SIGNAL = 2
INDEX_TP = 3
INDEX_SL = 4
INDEX_SL_VALUE = 5
INDEX_time = 6
INDEX_bid_h = 7
INDEX_bid_l = 8
INDEX_ask_h = 9
INDEX_ask_l = 10
INDEX_name = 11


class Trade:
    def __init__(self, list_values, index, profit_factor, loss_factor, pip_value):
        self.running = True
        self.start_index_m5 = list_values[INDEX_name][index]
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        self.pip_value = pip_value
        self.SL_value = list_values[INDEX_SL_VALUE][index]
        self.count = 0

        if list_values[INDEX_SIGNAL][index] == BUY:
            self.start_price = list_values[INDEX_bid_c][index]
            self.trigger_price = list_values[INDEX_bid_c][index]
            
        if list_values[INDEX_SIGNAL][index] == SELL:
            self.start_price = list_values[INDEX_ask_c][index]
            self.trigger_price = list_values[INDEX_ask_c][index]
            
        self.SIGNAL = list_values[INDEX_SIGNAL][index]
        self.TP = list_values[INDEX_TP][index]
        self.SL = list_values[INDEX_SL][index]
        self.result = 0.0
        self.end_time = list_values[INDEX_time][index]
        self.start_time = list_values[INDEX_time][index]
    
    def close_trade(self, list_values, index, result, trigger_price, acumulated_loss):
        self.running = False
        self.result = result
        self.end_time = list_values[INDEX_time][index]
        self.trigger_price = trigger_price

        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0

        if result < 0.0:
            acumulated_loss.append(abs(result))
        #     self.result = result
        # else:
        #     self.result = result

        if min_acumulated_loss > 0.0:
            if result >= min_acumulated_loss:
                if len(acumulated_loss) > 0:
                    acumulated_loss = acumulated_loss[1:]
                # print("zerou agora",len(acumulated_loss))

        return acumulated_loss

    def update(self, list_values, index, acumulated_loss):
        # self.acumulated_sum_loss = acumulated_loss

        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0

        self.count += 1
        if self.SIGNAL == BUY:
            if list_values[INDEX_bid_h][index] >= self.TP:
                acumulated_loss = self.close_trade(list_values, index, self.profit_factor, list_values[INDEX_bid_h][index], acumulated_loss)
            elif list_values[INDEX_bid_l][index] <= self.SL:
                acumulated_loss = self.close_trade(list_values, index, -self.loss_factor, list_values[INDEX_bid_l][index], acumulated_loss)
            elif min_acumulated_loss > 0.0:
                result = (list_values[INDEX_bid_h][index] - self.start_price) / self.pip_value
                if result >= min_acumulated_loss:
                    # print("supostamente zerou compra",result, row.bid_h, min_acumulated_loss)
                    acumulated_loss = self.close_trade(list_values, index, min_acumulated_loss, list_values[INDEX_bid_h][index], acumulated_loss)
                elif list_values[INDEX_SIGNAL][index] == SELL:
                    result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                    acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)
            elif list_values[INDEX_SIGNAL][index] == SELL:
                result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)
            

        if self.SIGNAL == SELL:
            if list_values[INDEX_ask_l][index] <= self.TP:
                acumulated_loss = self.close_trade(list_values, index, self.profit_factor, list_values[INDEX_ask_l][index], acumulated_loss)
            elif list_values[INDEX_ask_h][index] >= self.SL:
                acumulated_loss = self.close_trade(list_values, index, -self.loss_factor, list_values[INDEX_ask_h][index], acumulated_loss)   
            elif min_acumulated_loss > 0.0:
                result = (self.start_price - list_values[INDEX_ask_l][index]) / self.pip_value
                if result >= min_acumulated_loss:
                    # print("supostamente zerou venda", result, row.ask_l, min_acumulated_loss)
                    acumulated_loss = self.close_trade(list_values, index, min_acumulated_loss, list_values[INDEX_ask_l][index], acumulated_loss)
                elif list_values[INDEX_SIGNAL][index] == BUY:
                    result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                    acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)
            elif list_values[INDEX_SIGNAL][index] == BUY:
                result = (self.start_price - list_values[INDEX_ask_c][index]) / self.pip_value
                acumulated_loss = self.close_trade(list_values, index, result,list_values[INDEX_ask_c][index], acumulated_loss)
            

        return acumulated_loss
    

class EmaCrossMultiTemporal3TesterFast:
    def __init__(self, df,
                    apply_short_signal,
                    pip_value,
                    use_spread=True,
                    LOSS_FACTOR = 1000,
                    PROFIT_FACTOR = 200,
                    fixed_tp_sl=True
                    ):
        self.use_spread = use_spread
        self.apply_short_signal = apply_short_signal
        self.df = df.copy()
        self.LOSS_FACTOR = LOSS_FACTOR
        self.PROFIT_FACTOR = PROFIT_FACTOR
        self.pip_value = pip_value
        self.fixed_tp_sl = fixed_tp_sl
        self.acumulated_loss = []

        self.prepare_data()
        
    def prepare_data(self):
        
        print("prepare_data...")

        if self.use_spread == False:
            remove_spread(self.df)

        apply_short_signals(self.df, self.apply_short_signal)
        self.df.SIGNAL = self.df.SIGNAL.astype(int)
        
        apply_tp_sl(self.df,
                    self.PROFIT_FACTOR,
                    self.LOSS_FACTOR,
                    self.pip_value,
                    self.fixed_tp_sl)
        
    def run_test(self):
        print("run_test...")
        open_trades_m5 = []
        closed_trades_m5 = []

        list_value_refs = [
            self.df.bid_c.array,
            self.df.ask_c.array,
            self.df.SIGNAL.array,
            self.df.TP.array,
            self.df.SL.array,
            self.df.SL_VALUE.array,
            self.df.time.array,
            self.df.bid_h.array,
            self.df.bid_l.array,
            self.df.ask_h.array,
            self.df.ask_l.array,
            self.df.index.array,
        ]

        for index in range(self.df.shape[0]):
            
            if list_value_refs[INDEX_SIGNAL][index] != NONE:
                open_trades_m5.append(Trade(list_value_refs, index, self.PROFIT_FACTOR, self.LOSS_FACTOR, self.pip_value))  
                
            for ot in open_trades_m5:
                self.acumulated_loss = ot.update(list_value_refs, index, sorted(self.acumulated_loss,reverse=True))
                if ot.running == False:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

        self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
        print("Result:", self.df_results.result.sum())
        print("Len loss: ", len(self.acumulated_loss))
        print("Len Open:" , len(open_trades_m5))
        print("Len Close:" , len(closed_trades_m5))
