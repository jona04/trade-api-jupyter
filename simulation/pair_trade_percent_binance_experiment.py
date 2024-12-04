from collections import deque

import pandas as pd
import datetime as dt
import numpy as np
import math

NONE = 0


# Inicializando as constantes para os sinais
SIGNAL_UP = 1
SIGNAL_DOWN = 1



# emaper cross trend
def detect_signals_strategy_14(df, EMA_percent_s_force):
    """
    Função para detectar sinais de compra e venda com base no cruzamento de 
    EMA_percent_s e double_EMA_percent_s.

    Compra ocorre quando EMA_percent_s cruza para cima de double_EMA_percent_s.
    Venda ocorre quando EMA_percent_s cruza para baixo de double_EMA_percent_s.
    Operação é interrompida quando ocorre o cruzamento contrário.
    """
    
    # Obtém os valores das colunas necessárias
    EMA_percent_s_values = df.Average_EMA_percent_ema_short.values
    double_EMA_percent_s_values = df.Average_EMA_percent_ema_long.values
    
    # Vetores de sinal de compra e venda
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    # Itera sobre o DataFrame a partir do segundo valor
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        EMA_percent_s = EMA_percent_s_values[i]
        EMA_percent_s_prev = EMA_percent_s_values[i-1]
        double_EMA_percent_s = double_EMA_percent_s_values[i]
        double_EMA_percent_s_prev = double_EMA_percent_s_values[i-1]
        
        # Detecção de cruzamento para compra
        if (
            EMA_percent_s_prev < double_EMA_percent_s_prev and  # EMA_percent_s estava abaixo de double_EMA_percent_s
            EMA_percent_s > double_EMA_percent_s and # EMA_percent_s cruzou para cima de double_EMA_percent_s
            EMA_percent_s < -EMA_percent_s_force
        ):
            signal_up[i] = 1  # Marca o ponto de compra

        # Detecção de cruzamento para venda
        elif (
            EMA_percent_s_prev > double_EMA_percent_s_prev and  # EMA_percent_s estava acima de double_EMA_percent_s
            EMA_percent_s < double_EMA_percent_s and # EMA_percent_s cruzou para baixo de double_EMA_percent_s
            EMA_percent_s > EMA_percent_s_force
        ):
            signal_down[i] = 1  # Marca o ponto de venda

    # Adiciona as colunas de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down

    return df

INDEX_SIGNAL_UP = 0
INDEX_SIGNAL_DOWN = 1
INDEX_time = 2
INDEX_Close = 3
INDEX_High = 4
INDEX_Low = 5
INDEX_name = 6
INDEX_returns = 7
INDEX_strategy = 8
INDEX_percent_stop_loss = 9

class Trade:
    def __init__(self, list_values, index, stop_loss_percent):
        self.running = True
        self.start_index_m5 = list_values[INDEX_name][index]
        self.count = 0
        self.trigger_type = NONE
        self.strategy = 0
        self.strategy_no_tc = 0
        self.total_opened = 0
        self.first_return = True
        self.trail_stop_trigger = 0
        self.stop_loss_percent = stop_loss_percent

        self.trailing_stop_target = abs(self.stop_loss_percent)
        self.trailing_stop_loss = self.stop_loss_percent # Define o nível inicial de stop loss

        if list_values[INDEX_SIGNAL_UP][index] in [1]:
            self.type = 'buy'
           
        if list_values[INDEX_SIGNAL_DOWN][index] in [1]:
            self.type = 'sell'
        
        self.start_price = list_values[INDEX_Close][index]
        self.trigger_price = list_values[INDEX_Close][index]
        
        self.SIGNAL_UP = list_values[INDEX_SIGNAL_UP][index]
        self.SIGNAL_DOWN = list_values[INDEX_SIGNAL_DOWN][index]
        self.result = 0.0
        self.end_time = list_values[INDEX_time][index]
        self.start_time = list_values[INDEX_time][index]
        
    def close_trade(self, list_values, index, type, trigger_price):
        self.running = False
        self.end_time = list_values[INDEX_time][index]
        self.trigger_price = trigger_price
        if type == 'buy':
            result = (list_values[INDEX_Close][index] - self.start_price)
        else:
            result = (self.start_price - list_values[INDEX_Close][index])
        self.result = result

    def get_return(self,start_price, current_price, operation_type="buy"):
        if operation_type == "buy":
            return math.log(current_price / start_price)
        elif operation_type == "sell":
            # Para venda, invertemos a relação para que a lógica de ganho em queda de preço seja mantida
            return math.log(start_price / current_price)
        else:
            raise ValueError("operation_type deve ser 'buy' ou 'sell'")

    def update(self, list_values, index):
        self.count += 1

        # Processamento de trades diretamente sem funções auxiliares
        def process_trade(signal_type):
            close = list_values[INDEX_Close][index]
            if signal_type == 'buy':
                
              
                start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'buy')
                if self.strategy > 0.01 and self.trail_stop_trigger == 0:
                    self.trail_stop_trigger = 1
                elif self.strategy > self.trailing_stop_target:
                    self.trailing_stop_target += self.trailing_stop_target  # Dobra o alvo do trailing stop para o próximo nível
                    self.trailing_stop_loss = self.strategy / 1.2  # Atualiza o stop loss para metade do novo nível de lucro
                elif start_price_low_percent < self.trailing_stop_loss:
                    self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])


          
            elif signal_type == 'sell':
                
                
                start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_High][index],'sell')
                if self.strategy > 0.01 and self.trail_stop_trigger == 0:
                    self.trail_stop_trigger = 1
                elif self.strategy > self.trailing_stop_target:
                    self.trailing_stop_target += self.trailing_stop_target  # Dobra o alvo do trailing stop para o próximo nível
                    self.trailing_stop_loss = self.strategy / 1.2  # Atualiza o stop loss para metade do novo nível de lucro
                elif start_price_low_percent < self.trailing_stop_loss:
                    self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                    
        # Verificação dos sinais de COMPRA
        if self.SIGNAL_UP == 1:
            process_trade('buy')
        if self.SIGNAL_DOWN == 1:
            process_trade('sell')
        





class PairTradePercent:
    def __init__(self, 
                 df, 
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
        self.df["percent_stop_loss"] = 0
        # print("prepare_data...")

       
        if self.strategy == 14:
            detect_signals_strategy_14(self.df, self.EMA_percent_s_force)
        
        
    def run_test(self):
        
        # print("running test...")
        
        open_trades_m5 = deque()
        closed_trades_m5 = deque()

        list_value_refs = [
            self.df.SIGNAL_UP.values,
            self.df.SIGNAL_DOWN.values,
            self.df.time.values,
            self.df.Close.values,
            self.df.High.values,
            self.df.Low.values,
            self.df.index.values,
            self.df.returns.values,
            self.df.strategy.values,
            self.df.percent_stop_loss.values
        ]

        for index in range(self.df.shape[0]):
            
            if (
                (list_value_refs[INDEX_SIGNAL_UP][index] == 1 and list_value_refs[INDEX_SIGNAL_UP][index-1] == 0) or 
                (list_value_refs[INDEX_SIGNAL_DOWN][index] == 1 and list_value_refs[INDEX_SIGNAL_DOWN][index-1] == 0)
                ):
                open_trades_m5.append(Trade(list_value_refs, index, self.stop_loss_percent))  
                
                
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
                    if ot.trail_stop_trigger == 1:
                        if ot.strategy < 0:
                            ot.strategy = 0.01
                        elif ot.strategy > 0.01:
                            ot.strategy += 0.01
                    
                    
                    ot.strategy_real = ot.strategy
                    if ot.strategy_real > 0:
                        ot.strategy_real = ot.strategy/2
                    
                    ot.strategy_real += (4*self.tc)
                    ot.strategy += (2*self.tc)
                    
                    closed_trades_m5.append(ot)
                
                ot.total_opened = len(open_trades_m5)
            
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]


        self.len_close = len(closed_trades_m5)
        self.len_open = len(open_trades_m5)
        
        
        
        if self.len_close > 0:
            self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 

        del self.df
        del closed_trades_m5
        del open_trades_m5
        # del self.df_results
