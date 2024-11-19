import pandas as pd
import datetime as dt
import numpy as np

BUY_REVERSE = 1
SELL_REVERSE = -1
BUY_TREND = 2
SELL_TREND = -2
NONE = 0

TRIGGER_TYPE_TP = 1
TRIGGER_TYPE_SL = 2
TRIGGER_TYPE_ACUMULATED_LOSS = 3
TRIGGER_TYPE_REVERSED_CROSS = 4

# def apply_take_profit(row, pip_value, TP):
    
#     if row.SIGNAL != NONE:
#         if row.SIGNAL == BUY:
#             return row.donchian_high
#         else:
#             return row.donchian_low
#     else:
#         return 0.0

# def apply_take_profit(row, pip_value, TP):
    
#     if row.SIGNAL != NONE:
#         if row.SIGNAL == BUY:
#             return row.ask_c + (pip_value*TP)
#         else:
#             return row.bid_c - (pip_value*TP)
#     else:
#         return 0.0
    
# def apply_stop_loss_fixed(row, pip_value, SL):
    
#     if row.SIGNAL != NONE:
#         if row.SIGNAL == BUY:
#             return row.ask_c - (pip_value*SL), SL
#         elif row.SIGNAL == SELL:
#             return row.bid_c + (pip_value*SL), SL
#     else:
#         return 0.0, 0.0
    
# def apply_stop_loss(row, pip_value, SL):
    
#     if row.SIGNAL != NONE:
#         if row.SIGNAL == BUY:
#             res = ( row.ask_c - row.donchian_low ) / pip_value
#             if res > SL:
#                 return row.ask_c - (pip_value*SL), SL
#             return row.donchian_low, res
        
#         elif row.SIGNAL == SELL:
#             res = ( row.donchian_high - row.bid_c ) / pip_value
#             if res > SL:
#                 return row.bid_c + (pip_value*SL), SL
#             return row.donchian_high, res
#     else:
#         return 0.0, 0.0
    

def remove_spread(df):
    for a in ["ask", "bid"]:
        for b in ["o", "h", "l", "c"]:
            c = f"{a}_{b}"
            df[c] = df[f"mid_{b}"]

def apply_signals(df,sig, spread_limit):
    df["SIGNAL"] = df.apply(sig, spread=spread_limit, axis=1)

def apply_short_signals(df,sig):
    df["SIGNAL_SHORT"] = df.apply(sig, axis=1)

# def apply_tp_sl(df,PROFIT_FACTOR,LOSS_FACTOR,pip_location,fixed_tp_sl):
#     df["TP"] = df.apply(lambda row: apply_take_profit(row,pip_location,PROFIT_FACTOR), axis=1)
#     if fixed_tp_sl:
#         df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss_fixed(row, pip_location,LOSS_FACTOR), axis=1))
#     else:
#         df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss(row, pip_location,LOSS_FACTOR), axis=1))


INDEX_bid_c = 0
INDEX_ask_c = 1
INDEX_SIGNAL = 2
# INDEX_SIGNAL_SHORT = 3
# INDEX_TP = 3
# INDEX_SL = 4
# INDEX_SL_VALUE = 5
INDEX_time = 3
INDEX_bid_h = 4
INDEX_bid_l = 5
INDEX_ask_h = 6
INDEX_ask_l = 7
INDEX_name = 8


class Trade:
    def __init__(self, list_values, index, profit_factor, loss_factor, pip_value,trans_cost,neg_multiplier):
        self.running = True
        self.start_index_m5 = list_values[INDEX_name][index]
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        self.pip_value = pip_value
        # self.SL_value = list_values[INDEX_SL_VALUE][index]
        self.count = 0
        self.neg_multiplier = neg_multiplier
        self.trans_cost = trans_cost
        self.trigger_type = NONE

        if list_values[INDEX_SIGNAL][index] == BUY_REVERSE:
            self.start_price = list_values[INDEX_bid_c][index]
            self.trigger_price = list_values[INDEX_bid_c][index]
            
        if list_values[INDEX_SIGNAL][index] == SELL_REVERSE:
            self.start_price = list_values[INDEX_ask_c][index]
            self.trigger_price = list_values[INDEX_ask_c][index]
            
        self.SIGNAL = list_values[INDEX_SIGNAL][index]
        # self.TP = list_values[INDEX_TP][index]
        # self.SL = list_values[INDEX_SL][index]
        self.result = 0.0
        self.end_time = list_values[INDEX_time][index]
        self.start_time = list_values[INDEX_time][index]
    
    def close_trade(self, list_values, index, result, trigger_price, acumulated_loss):
        self.running = False
        self.result = result - self.trans_cost
        self.end_time = list_values[INDEX_time][index]
        self.trigger_price = trigger_price

        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0

        if result < 0.0:
            acumulated_loss.append(abs(result))
        #     self.result = result
        # else:
        #     self.result = result

        if min_acumulated_loss > 0.0:
            if result >= self.neg_multiplier*min_acumulated_loss:
                if len(acumulated_loss) > 0:
                    acumulated_loss = acumulated_loss[1:]
                # print("zerou agora",len(acumulated_loss))

        return acumulated_loss

    def update(self, list_values, index, acumulated_loss):
        # self.acumulated_sum_loss = acumulated_loss

        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0
        value_loss_trans_cost = (self.neg_multiplier*min_acumulated_loss) + self.trans_cost
        self.count += 1
        if self.SIGNAL == BUY_REVERSE:
            # if list_values[INDEX_bid_c][index] >= self.TP:
            #     self.trigger_type = TRIGGER_TYPE_TP
            #     acumulated_loss = self.close_trade(list_values, index, self.profit_factor, list_values[INDEX_bid_c][index], acumulated_loss)
            # elif list_values[INDEX_bid_c][index] <= self.SL:
            #     self.trigger_type = TRIGGER_TYPE_SL
            #     acumulated_loss = self.close_trade(list_values, index, -self.loss_factor, list_values[INDEX_bid_c][index], acumulated_loss)
            # elif min_acumulated_loss > 0.0:
            #     result = (list_values[INDEX_bid_h][index] - self.start_price) / self.pip_value
            #     if result >= value_loss_trans_cost:
            #         self.trigger_type = TRIGGER_TYPE_ACUMULATED_LOSS
            #         acumulated_loss = self.close_trade(list_values, index, value_loss_trans_cost, list_values[INDEX_bid_h][index], acumulated_loss)
                # elif list_values[INDEX_SIGNAL][index] == SELL:
                #     self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
                #     result = (list_values[INDEX_bid_h][index] - self.start_price) / self.pip_value
                #     acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_h][index], acumulated_loss)
            if list_values[INDEX_SIGNAL][index] == BUY_REVERSE:
                self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
                result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)
            

        if self.SIGNAL == SELL_REVERSE:
            # if list_values[INDEX_ask_c][index] <= self.TP:
            #     self.trigger_type = TRIGGER_TYPE_TP
            #     acumulated_loss = self.close_trade(list_values, index, self.profit_factor, list_values[INDEX_ask_c][index], acumulated_loss)
            # elif list_values[INDEX_ask_c][index] >= self.SL:
            #     self.trigger_type = TRIGGER_TYPE_SL
            #     acumulated_loss = self.close_trade(list_values, index, -self.loss_factor, list_values[INDEX_ask_c][index], acumulated_loss)   
            # elif min_acumulated_loss > 0.0:
            #     result = (self.start_price - list_values[INDEX_ask_l][index]) / self.pip_value
            #     if result >= value_loss_trans_cost:
            #         self.trigger_type = TRIGGER_TYPE_ACUMULATED_LOSS
            #         acumulated_loss = self.close_trade(list_values, index, value_loss_trans_cost, list_values[INDEX_ask_l][index], acumulated_loss)
            #     elif list_values[INDEX_SIGNAL][index] == BUY:
            #         self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
            #         result = (self.start_price - list_values[INDEX_ask_l][index]) / self.pip_value
            #         acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_ask_l][index], acumulated_loss)
            if list_values[INDEX_SIGNAL][index] == SELL_REVERSE:
                self.trigger_type = TRIGGER_TYPE_REVERSED_CROSS
                result = (self.start_price - list_values[INDEX_ask_c][index]) / self.pip_value
                acumulated_loss = self.close_trade(list_values, index, result,list_values[INDEX_ask_c][index], acumulated_loss)
            

        return acumulated_loss
    

class DonchianMultiTemporal4Tester:
    def __init__(self, df,
                    apply_signal,
                    apply_short_signal,
                    pip_value,
                    use_spread=True,
                    LOSS_FACTOR = 1000,
                    PROFIT_FACTOR = 200,
                    fixed_tp_sl=True,
                    trans_cost=8,
                    neg_multiplier=1,
                    rev=False,
                    spread_limit=50
                    ):
        self.use_spread = use_spread
        self.apply_signal = apply_signal
        self.apply_short_signal = apply_short_signal
        self.df = df.copy()
        self.LOSS_FACTOR = LOSS_FACTOR
        self.PROFIT_FACTOR = PROFIT_FACTOR
        self.pip_value = pip_value
        self.fixed_tp_sl = fixed_tp_sl
        self.acumulated_loss = []
        self.trans_cost = trans_cost
        self.neg_multiplier = neg_multiplier
        self.rev = rev
        self.spread_limit = spread_limit

        self.prepare_data()
        
    def prepare_data(self):
        
        print("prepare_data...")

        if self.use_spread == False:
            remove_spread(self.df)

        apply_signals(self.df, self.apply_signal, self.spread_limit)
        self.df.SIGNAL = self.df.SIGNAL.astype(int)

        if self.apply_short_signal != None:
            apply_short_signals(self.df, self.apply_short_signal)
            self.df.SIGNAL_SHORT = self.df.SIGNAL_SHORT.astype(int)
        
        # apply_tp_sl(self.df,
        #             self.PROFIT_FACTOR,
        #             self.LOSS_FACTOR,
        #             self.pip_value,
        #             self.fixed_tp_sl)
        
    def run_test(self):
        print("run_test...")
        open_trades_m5 = []
        closed_trades_m5 = []

        list_value_refs = [
            self.df.bid_c.array,
            self.df.ask_c.array,
            self.df.SIGNAL.array,
            # self.df.TP.array,
            # self.df.SL.array,
            # self.df.SL_VALUE.array,
            self.df.time.array,
            self.df.bid_h.array,
            self.df.bid_l.array,
            self.df.ask_h.array,
            self.df.ask_l.array,
            self.df.index.array,
        ]

        for index in range(self.df.shape[0]):
            
            for ind, ot in enumerate(open_trades_m5):
                # if ind == 0:
                #     continue
                self.acumulated_loss = ot.update(list_value_refs, index, sorted(self.acumulated_loss,reverse=self.rev))
                if ot.running == False:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

            if list_value_refs[INDEX_SIGNAL][index] != NONE:
                open_trades_m5.append(Trade(list_value_refs, index, self.PROFIT_FACTOR, 
                                            self.LOSS_FACTOR, self.pip_value, self.trans_cost, self.neg_multiplier))  
            
        self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
        print("Result:", self.df_results.result.sum())
        print("Len loss: ", len(self.acumulated_loss))
        print("Len Open:" , len(open_trades_m5))
        print("Len Close:" , len(closed_trades_m5))
