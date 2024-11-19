import pandas as pd
import datetime as dt
import numpy as np

BUY = 1
SELL = -1
NONE = 0

# Função otimizada para propagar os sinais
def propagate_signals(df):
    # Criar uma máscara onde SIGNAL é diferente de 0
    mask = df['SIGNAL'] != 0

    # Usar np.where para criar uma série de blocos de valores com base em 1 ou -1
    signal_filled = np.where(mask, df['SIGNAL'], np.nan)

    # Preencher para frente os valores de 1 e -1
    signal_filled = pd.Series(signal_filled).ffill()

    # Preencher para trás para garantir que o último -1 seja propagado corretamente
    signal_filled = signal_filled.bfill()

    # Atualizar a coluna SIGNAL no DataFrame
    df['SIGNAL'] = signal_filled.astype(int)

    return df

def apply_take_profit(row, pip_value, TP):
    
    if row.SIGNAL_SHORT != NONE:
        if row.SIGNAL_SHORT == BUY:
            return row.ask_c + (pip_value*TP)
        else:
            return row.bid_c - (pip_value*TP)
    else:
        return 0.0

def apply_stop_loss_fixed(row, pip_value, SL):
    
    if row.SIGNAL_SHORT != NONE:
        if row.SIGNAL_SHORT == BUY:
            return row.ask_c - (pip_value*SL), SL
        elif row.SIGNAL_SHORT == SELL:
            return row.bid_c + (pip_value*SL), SL
    else:
        return 0.0, 0.0
    
def apply_stop_loss(row, pip_value, SL):
    
    if row.SIGNAL_SHORT != NONE:
        if row.SIGNAL_SHORT == BUY:
            res = ( row.ask_c - row.donchian_low ) / pip_value
            if res > SL:
                return row.ask_c - (pip_value*SL), SL
            return row.donchian_low, res
        
        elif row.SIGNAL_SHORT == SELL:
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
    df["SIGNAL_SHORT"] = df.apply(sig, axis=1)

def apply_long_signals(df, sig):
    df["SIGNAL"] = df.apply(sig, axis=1)
    
def create_long_signals(df, time_d=1):
    df_signals = df[df.SIGNAL != NONE].copy() 
    df_signals['m5_start'] = [x + dt.timedelta(hours=time_d) for x in df_signals.time]
    df_signals.drop(['time', 'mid_o', 'mid_h', 'mid_l', 'bid_o', 'bid_h', 'bid_l','bid_c',
    'ask_o', 'ask_h', 'ask_l', 'ask_c'], axis=1, inplace=True)
    df_signals.rename(columns={
        'mid_c' : 'mid_c_long',
        'm5_start' : 'time'
    }, inplace=True)
    return df_signals

def apply_tp_sl(df,PROFIT_FACTOR,LOSS_FACTOR,pip_location,fixed_tp_sl):
    df["TP"] = df.apply(lambda row: apply_take_profit(row,pip_location,PROFIT_FACTOR), axis=1)
    if fixed_tp_sl:
        df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss_fixed(row, pip_location,LOSS_FACTOR), axis=1))
    else:
        df["SL"], df["SL_VALUE"] = zip(*df.apply(lambda row: apply_stop_loss(row, pip_location,LOSS_FACTOR), axis=1))

class Trade:
    def __init__(self, row, profit_factor, loss_factor, pip_value):
        self.running = True
        self.start_index_m5 = row.name
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        self.pip_value = pip_value
        self.SL_value = row.SL_VALUE
        self.count = 0

        if row.SIGNAL_SHORT == BUY:
            self.start_price = row.bid_c
            self.trigger_price = row.bid_c
            
        if row.SIGNAL_SHORT == SELL:
            self.start_price = row.ask_c
            self.trigger_price = row.ask_c
            
        self.SIGNAL = row.SIGNAL
        self.SIGNAL_SHORT = row.SIGNAL_SHORT
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
            if self.SIGNAL_SHORT == BUY:
                self.result = result
            elif self.SIGNAL_SHORT == SELL:
                self.result = result


    def update(self, row):
        self.count += 1
        if self.SIGNAL_SHORT == BUY:
            if row.bid_h >= self.TP:
                self.close_trade(row, self.profit_factor, row.bid_h)
            elif row.bid_l <= self.SL:
                self.close_trade(row, -self.loss_factor, row.bid_l)
            elif row.SIGNAL == SELL:
                # print("cruzamento inverso compra",row.bid_c,self.start_price,self.pip_value, self.count)
                result = (row.bid_c - self.start_price) / self.pip_value
                self.close_trade(row, result, row.bid_c)

        if self.SIGNAL_SHORT == SELL:
            if row.ask_l <= self.TP:
                self.close_trade(row, self.profit_factor, row.ask_l)
            elif row.ask_h >= self.SL:
                self.close_trade(row, -self.loss_factor, row.ask_h)   
            elif row.SIGNAL == BUY:
                # print("cruzamento inverso venda",row.ask_c,self.start_price,self.pip_value, self.count)
                result = (self.start_price - row.ask_c) / self.pip_value
                self.close_trade(row, result, row.ask_c)

class EmaCrossMultiTemporalTester:
    def __init__(self, df_big,
                    apply_long_signal, 
                    apply_short_signal,
                    pip_value,
                    df_m5,
                    use_spread=True,
                    LOSS_FACTOR = 1000,
                    PROFIT_FACTOR = 200,
                    fixed_tp_sl=True,
                    time_d=1 ):
        self.df_big = df_big.copy()
        self.use_spread = use_spread
        self.apply_long_signal = apply_long_signal
        self.apply_short_signal = apply_short_signal
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
            remove_spread(self.df_big)
            remove_spread(self.df_m5)

        apply_long_signals(self.df_big, self.apply_long_signal)
        df_signals = create_long_signals(self.df_big, time_d=self.time_d)
    
        df_m5_slim = self.df_m5[['time',
                                 'bid_c','bid_h', 'bid_l','bid_o', 
                                 'ask_c','ask_h', 'ask_l','ask_o', 
                                 'mid_c','mid_h','mid_l','mid_o',
                                 'EMA_SHORT_1', 'EMA_SHORT_2','SPREAD','EMA_480','EMA_1440', 
                                 'donchian_high_short', 'donchian_low_short', 
                                 'DELTA_SHORT', 'DELTA_SHORT_PREV' ]].copy()
        self.merged = pd.merge(left=df_m5_slim, right=df_signals, on='time', how='left')
        self.merged.fillna(0, inplace=True)
        self.merged.SIGNAL = self.merged.SIGNAL.astype(int)
        
        propagate_signals(self.merged)
        apply_short_signals(self.merged, self.apply_short_signal)
        
        apply_tp_sl(self.merged,
                    self.PROFIT_FACTOR,
                    self.LOSS_FACTOR,
                    self.pip_value,
                    self.fixed_tp_sl)
        
    def run_test(self):
        print("run_test...")
        open_trades_m5 = []
        closed_trades_m5 = []

        for index, row in self.merged.iterrows():
            
            if row.SIGNAL_SHORT != NONE:
                open_trades_m5.append(Trade(row, self.PROFIT_FACTOR, self.LOSS_FACTOR, self.pip_value))  
                
            for ot in open_trades_m5:
                ot.update(row)
                if ot.running == False:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

        self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
        print("Result:", self.df_results.result.sum())
