from collections import deque

import pandas as pd
import datetime as dt
import numpy as np

NONE = 0


# Inicializando as constantes para os sinais
SIGNAL_HIGH = 1
SIGNAL_87 = 2
SIGNAL_75 = 3
SIGNAL_62 = 4
SIGNAL_MID = 5
SIGNAL_37 = 6
SIGNAL_25 = 7
SIGNAL_12 = 8
SIGNAL_LOW = 9

# Função para processar os cruzamentos
def process_cross_up(df, i, band, signal, last_band_cross_up, band_name):
    if last_band_cross_up != band_name:
        df.at[i, 'SIGNAL_UP'] = signal
        
        return band_name
    return last_band_cross_up

def process_cross_down(df, i, band, signal, last_band_cross_down, band_name):
    if last_band_cross_down != band_name:
        df.at[i, 'SIGNAL_DOWN'] = signal

        return band_name
    return last_band_cross_down


def detect_signals(df, threshold_up, threshold_down, donchian_window_prev):
    """
    Continuously detects buy and sell signals based on cumulative percentage change
    from the last signal, considering both thresholds simultaneously.
    
    Parameters:
    - df (pd.DataFrame): DataFrame containing a 'Close' column and pre-existing 'SIGNAL_UP' and 'SIGNAL_DOWN' columns (initialized to 0).
    - threshold_up (float): Percentage threshold for each consecutive buy signal.
    - threshold_down (float): Percentage threshold for each consecutive sell signal.
    
    Returns:
    - pd.DataFrame: DataFrame with 'SIGNAL_UP' and 'SIGNAL_DOWN' columns updated for each buy or sell signal.
    """
    
    donchian_low = df['donchian_low'].values
    close = df['Close'].values
    
    # Inicializa o ponto de referência com o primeiro valor de 'Close'
    last_price = df['Close'].iloc[0]
    
    # Garante que as colunas de sinal estão preenchidas com zeros
    df['SIGNAL_UP'] = 0
    df['SIGNAL_DOWN'] = 0

    for i in range(1, len(df)):
        # Calcula a variação percentual acumulada em relação ao último ponto de referência
        pct_change = (df['Close'].iloc[i] - last_price) / last_price * 100
        
        # Se a variação percentual ultrapassa o threshold de compra, sinaliza uma nova compra
        if pct_change >= threshold_up:
            df.at[i, 'SIGNAL_UP'] = 1  # Marca sinal de compra
            last_price = df['Close'].iloc[i]  # Atualiza o ponto de referência para o valor atual

        # # Se a variação percentual ultrapassa o threshold de venda (para baixo), sinaliza uma nova venda
        # elif pct_change <= -threshold_down:
        #     df.at[i, 'SIGNAL_DOWN'] = 1  # Marca sinal de venda
        #     last_price = df['Close'].iloc[i]  # Atualiza o ponto de referência para o valor atual
            
        # Caso especial para donchian_low
        if close[i] < donchian_low[i-donchian_window_prev]:
            if abs(close[i] - last_price) >= last_price * (threshold_down/100):
                df.at[i, 'SIGNAL_DOWN'] = 1
                last_price = close[i]

    return df
    

INDEX_SIGNAL_UP = 0
INDEX_SIGNAL_DOWN = 1
INDEX_time = 2
INDEX_Close = 3
INDEX_name = 4
INDEX_ema_short = 5
INDEX_donchian_87 = 6
INDEX_donchian_75 = 7
INDEX_donchian_62 = 8
INDEX_donchian_mid = 9
INDEX_donchian_37 = 10
INDEX_donchian_25 = 11
INDEX_donchian_12 = 12
INDEX_donchian_high = 13
INDEX_donchian_low = 14
INDEX_returns = 15
INDEX_creturns = 16
INDEX_strategy = 17
INDEX_cstrategy = 18

class Trade:
    def __init__(self, list_values, index, threshold_up, threshold_down):
        self.running = True
        self.start_index_m5 = list_values[INDEX_name][index]
        self.count = 0
        self.trigger_type = NONE
        self.strategy = 0
        self.total_opened = 0
        self.threshold_up = threshold_up
        self.threshold_down = threshold_down
        
        if list_values[INDEX_SIGNAL_UP][index] in [1,2,3,4,5,6,7,8,9]:
            self.start_price = list_values[INDEX_Close][index]
            self.trigger_price = list_values[INDEX_Close][index]
            
        if list_values[INDEX_SIGNAL_DOWN][index] in [1,2,3,4,5,6,7,8,9]:
            self.start_price = list_values[INDEX_Close][index]
            self.trigger_price = list_values[INDEX_Close][index]
            
        self.SIGNAL_UP = list_values[INDEX_SIGNAL_UP][index]
        self.SIGNAL_DOWN = list_values[INDEX_SIGNAL_DOWN][index]
        self.result = 0.0
        self.end_time = list_values[INDEX_time][index]
        self.start_time = list_values[INDEX_time][index]
        
    def close_trade(self, list_values, index, result, trigger_price):
        self.running = False
        self.end_time = list_values[INDEX_time][index]
        self.trigger_price = trigger_price
        self.result = result

    def update(self, list_values, index):
        self.count += 1
        
        # Processamento de trades diretamente sem funções auxiliares
        def process_trade(signal_type, signal_level_down):
            if signal_type == 'buy':
                
                if self.strategy >= self.threshold_up/100:
                # if list_values[INDEX_SIGNAL_UP][index] == 1:
                    self.trigger_type = self.SIGNAL_UP
                    result = (list_values[INDEX_Close][index] - self.start_price)
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # if self.strategy <= -self.sl:
                # # elif list_values[INDEX_SIGNAL_DOWN][index] == signal_level_down:
                #     self.trigger_type = self.SIGNAL_UP
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # if self.strategy <= -0.02:
                #     self.trigger_type = self.SIGNAL_UP
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                        
            # else:
            #     if list_values[INDEX_SIGNAL_DOWN][index] == signal_level_up:
            #         self.trigger_type = self.SIGNAL_DOWN
            #         result = (self.start_price - list_values[INDEX_Close][index])
            #         self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
            #     elif list_values[INDEX_SIGNAL_UP][index] == signal_level_down:
            #         self.trigger_type = self.SIGNAL_DOWN
            #         result = (self.start_price - list_values[INDEX_Close][index])
            #         self.close_trade(list_values, index, result, list_values[INDEX_Close][index]) 

        
        # Verificação dos sinais de COMPRA
        # if self.SIGNAL_UP == SIGNAL_HIGH:
        #     process_trade('buy', SIGNAL_LOW)
        # elif self.SIGNAL_UP == SIGNAL_75:
        #     process_trade('buy', SIGNAL_LOW)
        # elif self.SIGNAL_UP == SIGNAL_MID:
        #     process_trade('buy', SIGNAL_LOW)
        # elif self.SIGNAL_UP == SIGNAL_25:
        #     process_trade('buy', SIGNAL_LOW)
        if self.SIGNAL_UP == 1:
            process_trade('buy', SIGNAL_LOW)
        if self.SIGNAL_DOWN == 1:
            process_trade('buy', SIGNAL_LOW)
        
        # elif self.SIGNAL_DOWN == SIGNAL_25:
        #     process_trade('sell', SIGNAL_MID)
        # elif self.SIGNAL_DOWN == SIGNAL_LOW:
        #     process_trade('sell', SIGNAL_MID)





class DonchianReversion:
    def __init__(self, df, donchian_window_prev = 100, threshold_up=1, threshold_down=1, donchian_up_signals=[1,3,5,7]):
        self.df = df
        self.donchian_window_prev = donchian_window_prev
        self.len_close = 0
        self.len_open = 0
        self.threshold_up = threshold_up
        self.threshold_down = threshold_down
        self.donchian_up_signals = donchian_up_signals
        self.first_price = df.Close.values[0]
        self.last_price = df.Close.values[-1]
        
        self.prepare_data()
        
    def prepare_data(self):
        
        # print("prepare_data...")


        # Inicializando as novas colunas com zeros
        self.df['SIGNAL_UP'] = 0
        self.df['SIGNAL_DOWN'] = 0

        # Aplicar a função para detectar sinais
        detect_signals(self.df, self.threshold_up, self.threshold_down, self.donchian_window_prev)
       
        
    def run_test(self):
        open_trades_m5 = deque()
        closed_trades_m5 = deque()

        list_value_refs = [
            self.df.SIGNAL_UP.values,
            self.df.SIGNAL_DOWN.values,
            self.df.time.values,
            self.df.Close.values,
            self.df.index.values,
            self.df.EMA_short.values,
            self.df.donchian_87.values,
            self.df.donchian_75.values,
            self.df.donchian_62.values,
            self.df.donchian_mid.values,
            self.df.donchian_37.values,
            self.df.donchian_25.values,
            self.df.donchian_12.values,
            self.df.donchian_high.values,
            self.df.donchian_low.values,
            self.df.returns.values,
            self.df.strategy.values,
        ]

        for index in range(self.df.shape[0]):
            
            for ind, ot in enumerate(open_trades_m5):
                ot.update(list_value_refs, index)
                ot.strategy += list_value_refs[INDEX_returns][index]
                
                if ot.running == False:
                    ot.strategy += ot.strategy * -0.00152
                    closed_trades_m5.append(ot)
                
                
                ot.total_opened = len(open_trades_m5)
            
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

            if list_value_refs[INDEX_SIGNAL_UP][index] == 1 or list_value_refs[INDEX_SIGNAL_DOWN][index] == 1:
                if len(open_trades_m5) < 11:
                    open_trades_m5.append(Trade(list_value_refs, index, self.threshold_up, self.threshold_down))  

        self.len_close = len(closed_trades_m5)
        self.len_open = len(open_trades_m5)
        
        if self.len_close > 0:
            self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
            # res_pos = self.df_results[self.df_results['result'] > 0]
            # res_neg = self.df_results[self.df_results['result'] < 0]
            # sum_neg = res_neg.result.sum() * -1
            # sum_pos = res_pos.result.sum()
            
            # print("####", self.donchian_up_signals)
            # print("Result:", self.df_results.result.sum())
            # print("Strategy:", self.df_results.strategy.sum())
            # print("Max oppend:", max(self.df_results.total_opened))
            
            # print("Len Open:" , len(open_trades_m5), "Len Close:" , len(closed_trades_m5))
            # print("Len Pos", len(res_pos), "Len Neg", len(res_neg))
            # print("Res pos", sum_pos, "Res neg", sum_neg)
            # print("Rel len pos neg", len(res_pos)/(len(res_pos)+ len(res_neg)))
            # print("Rel len neg pos", len(res_neg)/(len(res_pos)+ len(res_neg)))
            # print("Rel pos neg", sum_pos/(sum_pos+ sum_neg))
            # print("Rel neg pos", sum_neg/(sum_pos+ sum_neg))
            # print("")
            

        del self.df
        del closed_trades_m5
        del open_trades_m5
        # del self.df_results
