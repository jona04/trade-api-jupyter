from collections import deque

import pandas as pd
import datetime as dt
import numpy as np
import math

NONE = 0

# Inicializando as constantes para os sinais
SIGNAL_HIGH = 1
SIGNAL_87 = 2
SIGNAL_75 = 3
SIGNAL_75_TREND = 33
SIGNAL_62 = 4
SIGNAL_MID = 5
SIGNAL_37 = 6
SIGNAL_25 = 7
SIGNAL_25_TREND = 77
SIGNAL_12 = 8
SIGNAL_LOW = 9

# Função para detectar os sinais de cruzamentos
def detect_signals(df, donchian_window_prev=500):

    last_band_cross_up = 0
    last_band_cross_down = 0

    ema_short = df['EMA_short'].values
    donchian_75 = df['donchian_75'].values
    donchian_25 = df['donchian_25'].values
    donchian_high = df['donchian_high'].values
    donchian_low = df['donchian_low'].values
    donchian_mid = df['donchian_mid'].values

    # Inicializando listas para verificar a presença de sinais ativos
    up_active = False
    down_active = False

    for i in range(1, len(df)):
        # Cruzamentos de alta
        if ema_short[i-1] <= donchian_75[i-1] and ema_short[i] > donchian_75[i]:
            if last_band_cross_up != '75':
                df.at[i, 'SIGNAL_UP'] = SIGNAL_75
                last_band_cross_up = '75'
                
        elif ema_short[i-1] <= donchian_25[i-1] and ema_short[i] > donchian_25[i]:
            if last_band_cross_up != '25':
                df.at[i, 'SIGNAL_UP'] = SIGNAL_25
                last_band_cross_up = '25'    

        elif ema_short[i-1] <= donchian_mid[i-1] and ema_short[i] > donchian_mid[i]:
            if last_band_cross_up != 'mid':
                df.at[i, 'SIGNAL_UP'] = SIGNAL_MID
                last_band_cross_up = 'mid'
                
        # Cruzamentos de baixa
        elif ema_short[i-1] >= donchian_25[i-1] and ema_short[i] < donchian_25[i]:
            if last_band_cross_down != '25':
                df.at[i, 'SIGNAL_DOWN'] = SIGNAL_25
                last_band_cross_down = '25'
                
        elif ema_short[i-1] >= donchian_75[i-1] and ema_short[i] < donchian_75[i]:
            if last_band_cross_down != '75':
                df.at[i, 'SIGNAL_DOWN'] = SIGNAL_75
                last_band_cross_down = '75'
        
        elif ema_short[i-1] >= donchian_mid[i-1] and ema_short[i] < donchian_mid[i]:
            if last_band_cross_down != 'mid':
                df.at[i, 'SIGNAL_DOWN'] = SIGNAL_MID
                last_band_cross_down = 'mid'
                
        # Caso especial para donchian_high
        elif ema_short[i-1] <= donchian_high[i-donchian_window_prev] and ema_short[i] > donchian_high[i-donchian_window_prev]:
            df.at[i, 'SIGNAL_UP'] = SIGNAL_HIGH
            last_band_cross_up = 'high'
            last_band_cross_down = 'high'
            up_active = True  # sinal UP ativo
            down_active = False  # desativa sinal DOWN
            
        # Caso especial para donchian_low
        elif ema_short[i-1] >= donchian_low[i-donchian_window_prev] and ema_short[i] < donchian_low[i-donchian_window_prev]:
            df.at[i, 'SIGNAL_DOWN'] = SIGNAL_LOW
            last_band_cross_down = 'low'
            last_band_cross_up = 'low'
            down_active = True  #sinal DOWN ativo
            up_active = False # desativa sinal UP
 
    return df


INDEX_Close = 0
INDEX_High = 1
INDEX_Low = 2
INDEX_SIGNAL_UP = 3
INDEX_SIGNAL_DOWN = 4
INDEX_time = 5
INDEX_name = 6
INDEX_ema_short = 7
INDEX_donchian_87 = 8
INDEX_donchian_75 = 9
INDEX_donchian_62 = 10
INDEX_donchian_mid = 11
INDEX_donchian_37 = 12
INDEX_donchian_25 = 13
INDEX_donchian_12 = 14
INDEX_donchian_high = 15
INDEX_donchian_low = 16
INDEX_returns = 17
INDEX_strategy = 18

class Trade:
    def __init__(self, list_values, index):
        self.running = True
        self.start_index_m5 = list_values[INDEX_name][index]
        self.count = 0
        self.trigger_type = NONE
        self.strategy = 0
        self.strategy_no_tc = 0
        self.total_opened = 0
        self.first_return = True
        # self.trail_stop_trigger = 0
        # self.trailing_stop_loss = 0
        
        if list_values[INDEX_SIGNAL_UP][index] in [1,2,3,4,5,6,7,8,9]:
            self.start_price = list_values[INDEX_Close][index]
            self.trigger_price = list_values[INDEX_Close][index]
            self.type = 'buy'
            
        if list_values[INDEX_SIGNAL_DOWN][index] in [1,2,3,4,5,6,7,8,9]:
            self.start_price = list_values[INDEX_Close][index]
            self.trigger_price = list_values[INDEX_Close][index]
            self.type = 'sell'
            
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
        self.count +=1
        
        # Processamento de trades diretamente sem funções auxiliares
        def process_trade(signal_type, signal_level_up, signal_level_down):
            if signal_type == 'buy':

                if list_values[INDEX_SIGNAL_UP][index] == signal_level_up:
                    self.trigger_type = self.SIGNAL_UP
                    result = (list_values[INDEX_Close][index] - self.start_price)
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                elif list_values[INDEX_SIGNAL_DOWN][index] == signal_level_down:
                    self.trigger_type = self.SIGNAL_UP
                    result = (list_values[INDEX_Close][index] - self.start_price)
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy > 0.003 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_loss = 0.001
                # elif self.trailing_stop_loss != 0 and self.strategy < self.trailing_stop_loss:
                #     self.trigger_type = self.SIGNAL_UP
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                    
            else:
                
                if list_values[INDEX_SIGNAL_DOWN][index] == signal_level_up:
                    self.trigger_type = self.SIGNAL_DOWN
                    result = (self.start_price - list_values[INDEX_Close][index])
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                elif list_values[INDEX_SIGNAL_UP][index] == signal_level_down:
                    self.trigger_type = self.SIGNAL_DOWN
                    result = (self.start_price - list_values[INDEX_Close][index])
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy > 0.003 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_loss = 0.001
                # elif self.trailing_stop_loss != 0 and self.strategy < self.trailing_stop_loss:
                #     self.trigger_type = self.SIGNAL_DOWN
                #     result = (self.start_price - list_values[INDEX_Close][index])
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
              
        
        # Verificação dos sinais de COMPRA
        if self.SIGNAL_UP == SIGNAL_MID:
            process_trade('buy', SIGNAL_HIGH, SIGNAL_LOW)
        # elif self.SIGNAL_UP == SIGNAL_75:
        #     process_trade('buy', SIGNAL_HIGH, SIGNAL_LOW)
            
        # Verificação dos sinais de VENDA
        elif self.SIGNAL_DOWN == SIGNAL_MID:
            process_trade('sell', SIGNAL_LOW, SIGNAL_HIGH)
        # elif self.SIGNAL_DOWN == SIGNAL_LOW:
        #     process_trade('sell', SIGNAL_LOW, SIGNAL_HIGH)
            
    

class DonchianMultiTemporalBinance:
    def __init__(self, df, 
                 strategy,
                 EMA_percent_s_force, 
                 stop_loss_percent, 
                 rsi_force, 
                 adx_force,
                 tc=-0.0004):
        self.df = df
        self.first_price = df.Close.values[0]
        self.last_price = df.Close.values[-1]
        self.len_close = 0
        self.len_open = 0
        self.EMA_percent_s_force = EMA_percent_s_force
        self.strategy = strategy
        self.stop_loss_percent = stop_loss_percent
        self.rsi_force = rsi_force
        self.adx_force = adx_force
        self.tc = tc
 
        self.prepare_data()
        
    def prepare_data(self):
        
        # print("prepare_data...")


        # Inicializando as novas colunas com zeros
        self.df['SIGNAL_UP'] = 0
        self.df['SIGNAL_DOWN'] = 0

        # Aplicar a função para detectar sinais
        detect_signals(self.df)
        
    def run_test(self):
        # print("run_test...")
        open_trades_m5 = deque()
        closed_trades_m5 = deque()

        list_value_refs = [
            self.df.Close.values,
            self.df.High.values,
            self.df.Low.values,
            self.df.SIGNAL_UP.values,
            self.df.SIGNAL_DOWN.values,
            self.df.time.values,
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
            
            if list_value_refs[INDEX_SIGNAL_UP][index] in [5]:
                open_trades_m5.append(Trade(list_value_refs, index))  
            elif list_value_refs[INDEX_SIGNAL_DOWN][index] in [5]:
                open_trades_m5.append(Trade(list_value_refs, index))  
                
            for ind, ot in enumerate(open_trades_m5):
                ot.update(list_value_refs, index)
                
                if ot.first_return: # usado para pegar o retorno apatir da segunda operação depois da abertura
                    ot.first_return = False
                else:
                    if ot.type == 'buy':
                        ot.strategy += list_value_refs[INDEX_returns][index]
                        ot.strategy_no_tc += list_value_refs[INDEX_returns][index]
                    elif ot.type == 'sell':
                        ot.strategy += (list_value_refs[INDEX_returns][index]*-1)
                        ot.strategy_no_tc += (list_value_refs[INDEX_returns][index]*-1)
                    
                if ot.running == False:
                    # caso o fechamento nao pegue o breakeven
                    # aplica custo de transação multiplcado por 2 para abertura e fechamento
                    # if ot.trail_stop_trigger == 1 and ot.strategy < 0:
                    #     ot.strategy = ot.trailing_stop_loss
                    # elif ot.strategy < 0 and ot.trail_stop_trigger != 0:
                    #     ot.strategy = ot.trailing_stop_loss
                    # ot.strategy = ot.trailing_stop_loss
                    
                    ot.strategy += (2*self.tc)
                    
                    closed_trades_m5.append(ot)
                
                
                
                ot.total_opened = len(open_trades_m5)
            
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]
            
        self.len_close = len(closed_trades_m5)
        self.len_open = len(open_trades_m5)
        
        if self.len_close > 0:
            self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
            res_pos = self.df_results[self.df_results['strategy'] > 0]
            res_neg = self.df_results[self.df_results['strategy'] < 0]
            # sum_neg = res_neg.strategy.sum() * -1
            # sum_pos = res_pos.strategy.sum()
            
            # print("####")
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
            

        # del self.df
        del closed_trades_m5
        del open_trades_m5
        # del self.df_results