import pandas as pd
import datetime as dt

BUY = 1
SELL = -1
NONE = 0

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

def apply_signals(df, PROFIT_FACTOR,LOSS_FACTOR,pip_location, sig, fixed_tp_sl):
    df["SIGNAL"] = df.apply(sig, axis=1)
    df["TP"] = df.apply(lambda row: apply_take_profit(row,pip_location,PROFIT_FACTOR), axis=1)
    # df["SL_VALUE"] = df.apply(lambda row: apply_stop_loss(row, pip_location,LOSS_FACTOR), axis=1)
    if fixed_tp_sl:
        df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss_fixed(row, pip_location,LOSS_FACTOR), axis=1))
    else:
        df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss(row, pip_location,LOSS_FACTOR), axis=1))

def create_signals(df, time_d=1):
    df_signals = df[df.SIGNAL != NONE].copy() 
    df_signals['m5_start'] = [x + dt.timedelta(hours=time_d) for x in df_signals.time]
    df_signals.drop(['time', 'mid_o', 'mid_h', 'mid_l', 'bid_o', 'bid_h', 'bid_l',
    'ask_o', 'ask_h', 'ask_l'], axis=1, inplace=True)
    df_signals.rename(columns={
        'bid_c' : 'start_price_BUY',
        'ask_c' : 'start_price_SELL',
        'm5_start' : 'time'
    }, inplace=True)
    return df_signals


class Trade:
    def __init__(self, row, profit_factor, loss_factor, pip_value):
        self.running = True
        self.start_index_m5 = row.name
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        self.pip_value = pip_value
        self.SL_value = row.SL_VALUE
        
        if row.SIGNAL == BUY:
            self.start_price = row.start_price_BUY
            self.trigger_price = row.start_price_BUY
            
        if row.SIGNAL == SELL:
            self.start_price = row.start_price_SELL
            self.trigger_price = row.start_price_SELL
            
        self.SIGNAL = row.SIGNAL
        self.TP = row.TP
        self.SL = row.SL
        self.result = 0.0
        self.end_time = row.time
        self.start_time = row.time
        
    def close_trade(self, row, result, trigger_price):
        self.running = False
        # self.result = result
        self.end_time = row.time
        self.trigger_price = trigger_price
        

        if result > 0:
            self.result = result
        else:
            if self.SIGNAL == BUY:
                self.result = -self.SL_value
            elif self.SIGNAL == SELL:
                self.result = -self.SL_value


    def update(self, row):
        if self.SIGNAL == BUY:
            if row.bid_h >= self.TP:
                self.close_trade(row, self.profit_factor, row.bid_h)
            elif row.bid_l <= self.SL:
                self.close_trade(row, -self.loss_factor, row.bid_l)
            elif self.SIGNAL == SELL:
                print("cruzamento inverso compra")
                result = (row.mid_c - self.start_price) / self.pip_value
                self.close_trade(row, result, row.mid_l)

        if self.SIGNAL == SELL:
            if row.ask_l <= self.TP:
                self.close_trade(row, self.profit_factor, row.ask_l)
            elif row.ask_h >= self.SL:
                self.close_trade(row, -self.loss_factor, row.ask_h)   
            elif self.SIGNAL == BUY:
                print("cruzamento inverso venda")
                result = (self.start_price - row.mid_c) / self.pip_value
                self.close_trade(row, result, row.mid_l)

class EmaCrossLongTpSlTester:
    def __init__(self, df_big,
                    apply_signal, 
                    pip_value,
                    df_m5,
                    use_spread=True,
                    LOSS_FACTOR = 1000,
                    PROFIT_FACTOR = 200,
                    fixed_tp_sl=True,
                    time_d=1 ):
        self.df_big = df_big.copy()
        self.use_spread = use_spread
        self.apply_signal = apply_signal
        self.df_m5 = df_m5.copy()
        self.LOSS_FACTOR = LOSS_FACTOR
        self.PROFIT_FACTOR = PROFIT_FACTOR
        self.time_d = time_d
        self.pip_value = pip_value
        self.fixed_tp_sl = fixed_tp_sl

        self.prepare_data()
        
    def prepare_data(self):
        
        print("prepare_data...")

        if self.use_spread == False:
            remove_spread( self.df_big)
            remove_spread( self.df_m5)

        apply_signals(self.df_big,
                    self.PROFIT_FACTOR,
                    self.LOSS_FACTOR,
                    self.pip_value,
                    self.apply_signal,
                    self.fixed_tp_sl)

        df_m5_slim = self.df_m5[['time','bid_h', 'bid_l', 'ask_h', 'ask_l' ]].copy()
        df_signals = create_signals(self.df_big, time_d=self.time_d)

        self.merged = pd.merge(left=df_m5_slim, right=df_signals, on='time', how='left')
        self.merged.fillna(0, inplace=True)
        self.merged.SIGNAL = self.merged.SIGNAL.astype(int)
        
    def run_test(self):
        print("run_test...")
        open_trades_m5 = []
        closed_trades_m5 = []

        for index, row in self.merged.iterrows():
            
            if row.SIGNAL != NONE:
                open_trades_m5.append(Trade(row, self.PROFIT_FACTOR, self.LOSS_FACTOR, self.pip_value))  
                
            for ot in open_trades_m5:
                ot.update(row)
                if ot.running == False:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

        self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
        print("Result:", self.df_results.result.sum())
