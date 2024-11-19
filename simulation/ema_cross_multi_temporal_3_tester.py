import pandas as pd
import datetime as dt
import numpy as np

BUY = 1
SELL = -1
NONE = 0


def apply_take_profit(row, pip_value, TP):
    
    if row.SIGNAL != NONE:
        if row.SIGNAL == BUY:
            return row.donchian_high
        else:
            return row.donchian_low
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

class Trade:
    def __init__(self, row, profit_factor, loss_factor, pip_value):
        self.running = True
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        self.pip_value = pip_value
        self.SL_value = row.SL_VALUE
        self.count = 0

        if row.SIGNAL == BUY:
            self.start_price = row.bid_c
            self.trigger_price = row.bid_c
            
        if row.SIGNAL == SELL:
            self.start_price = row.ask_c
            self.trigger_price = row.ask_c
            
        self.SIGNAL = row.SIGNAL
        self.TP = row.TP
        self.SL = row.SL
        self.result = 0.0
        self.end_time = row.time
        self.start_time = row.time
        
    def close_trade(self, row, result, trigger_price, acumulated_loss):
        self.running = False
        self.end_time = row.time
        self.trigger_price = trigger_price

        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0

        if result < 0.0:
            acumulated_loss.append(abs(result))
            self.result = result
        else:
            self.result = result

        if min_acumulated_loss > 0.0:
            if result >= min_acumulated_loss:
                if len(acumulated_loss) > 0:
                    acumulated_loss = acumulated_loss[1:]
                # print("zerou agora",len(acumulated_loss))

        return acumulated_loss

    def update(self, row, acumulated_loss):
        # self.acumulated_sum_loss = acumulated_loss

        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0

        self.count += 1
        if self.SIGNAL == BUY:
            # if row.bid_h >= self.TP:
            #     result = (self.TP - self.start_price) / self.pip_value
            #     acumulated_loss = self.close_trade(row, result, row.bid_h, acumulated_loss)
            # if row.SIGNAL == SELL:
            #     result = (row.bid_c - self.start_price) / self.pip_value
            #     acumulated_loss = self.close_trade(row, result, row.bid_c, acumulated_loss)
            if row.bid_l <= self.SL:
                acumulated_loss = self.close_trade(row, -self.loss_factor, row.bid_l, acumulated_loss)
            elif min_acumulated_loss > 0.0:
                result = (row.bid_c - self.start_price) / self.pip_value
                if result >= min_acumulated_loss:
                    # print("supostamente zerou compra",result, row.bid_h, min_acumulated_loss)
                    acumulated_loss = self.close_trade(row, result, row.bid_c, acumulated_loss)

        if self.SIGNAL == SELL:
            # if row.ask_l <= self.TP:
            #     result = (self.start_price - self.TP) / self.pip_value
            #     acumulated_loss = self.close_trade(row, result, row.ask_l, acumulated_loss)
            # if row.SIGNAL == BUY:
            #     result = (self.start_price - row.ask_c) / self.pip_value
            #     acumulated_loss = self.close_trade(row, result, row.ask_c, acumulated_loss)
            if row.ask_h >= self.SL:
                acumulated_loss = self.close_trade(row, -self.loss_factor, row.ask_h, acumulated_loss)   
            elif min_acumulated_loss > 0.0:
                result = (self.start_price - row.ask_c) / self.pip_value
                if result >= min_acumulated_loss:
                    # print("supostamente zerou venda", result, row.ask_l, min_acumulated_loss)
                    acumulated_loss = self.close_trade(row, result, row.ask_c, acumulated_loss)

        return acumulated_loss
    

class EmaCrossMultiTemporal3Tester:
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

        for index, row in self.df.iterrows():
            
            if row.SIGNAL != NONE:
                open_trades_m5.append(Trade(row, self.PROFIT_FACTOR, self.LOSS_FACTOR, self.pip_value))  
                
            for ot in open_trades_m5:
                self.acumulated_loss = ot.update(row, sorted(self.acumulated_loss))
                if ot.running == False:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

        self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
        print("Result:", self.df_results.result.sum())
        print("Len loss: ", len(self.acumulated_loss))
        print("Len Open:" , len(open_trades_m5))
        print("Len Close:" , len(closed_trades_m5))
