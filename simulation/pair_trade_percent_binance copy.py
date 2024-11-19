from collections import deque

import pandas as pd
import datetime as dt
import numpy as np

NONE = 0


# Inicializando as constantes para os sinais
SIGNAL_UP = 1
SIGNAL_DOWN = 1

def detect_signals_strategy_15(df):
    """
    Função para detectar sinais de compra e venda com base no cruzamento de
    Average_EMA_percent_ema com zero.
    
    Compra ocorre quando Average_EMA_percent_ema cruza para cima de zero.
    Venda ocorre quando Average_EMA_percent_ema cruza para baixo de zero.
    Operação é interrompida quando ocorre o cruzamento contrário.
    """

    # Obtém os valores da coluna necessária
    avg_ema_values = df['Average_EMA_percent_ema'].values
    
    # Variáveis para rastrear o estado de compra e venda
    in_up_position = False  # Indica se estamos em uma operação de compra
    in_down_position = False  # Indica se estamos em uma operação de venda

    # Vetores de sinal de compra e venda
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    # Itera sobre o DataFrame a partir do segundo valor
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        avg_ema = avg_ema_values[i]
        avg_ema_prev = avg_ema_values[i-1]
        
        # Detecção de cruzamento para compra
        if avg_ema_prev < 0 and avg_ema > 0:  # Cruzamento para cima de zero
            in_up_position = True  # Ativa sinal de compra
            signal_up[i] = 1  # Marca o ponto de compra
            in_down_position = False  # Interrompe possível sinal de venda

        # Detecção de cruzamento para venda
        elif avg_ema_prev > 0 and avg_ema < 0:  # Cruzamento para baixo de zero
            in_down_position = True  # Ativa sinal de venda
            signal_down[i] = 1  # Marca o ponto de venda
            in_up_position = False  # Interrompe possível sinal de compra

        # Continuação do sinal enquanto não há cruzamento contrário
        if in_up_position:
            signal_up[i] = 1  # Mantém o sinal de compra ativo

        if in_down_position:
            signal_down[i] = 1  # Mantém o sinal de venda ativo

    # Adiciona as colunas de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down

    return df






import numpy as np

def detect_signals_strategy_16(df, EMA_percent_s_force):
    """
    Função para detectar sinais de compra e venda com base no cruzamento de
    Average_EMA_percent_ema_short e Average_EMA_percent_ema_long.
    
    Compra ocorre quando Average_EMA_percent_ema_short cruza para cima de Average_EMA_percent_ema_long,
    com Average_EMA_percent_ema_short abaixo de EMA_percent_s_force.
    
    Venda ocorre quando Average_EMA_percent_ema_short cruza para baixo de Average_EMA_percent_ema_long,
    com Average_EMA_percent_ema_short acima de EMA_percent_s_force.
    
    Operação é interrompida quando Average_EMA_percent_ema_short cruza zero no sentido oposto da operação.
    """

    # Obtém os valores das colunas necessárias
    avg_ema_short_values = df['Average_EMA_percent_ema_short'].values
    avg_ema_long_values = df['Average_EMA_percent_ema_long'].values
    
    # Variáveis para rastrear o estado de compra e venda
    in_up_position = False  # Indica se estamos em uma operação de compra
    in_down_position = False  # Indica se estamos em uma operação de venda

    # Vetores de sinal de compra e venda
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    # Itera sobre o DataFrame a partir do segundo valor
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        avg_ema_short = avg_ema_short_values[i]
        avg_ema_short_prev = avg_ema_short_values[i-1]
        avg_ema_long = avg_ema_long_values[i]
        avg_ema_long_prev = avg_ema_long_values[i-1]
        
        # Detecção de cruzamento para compra
        if (
            avg_ema_short_prev < avg_ema_long_prev and  # short estava abaixo de long
            avg_ema_short > avg_ema_long and  # short cruzou para cima de long
            avg_ema_short < -EMA_percent_s_force  # short está abaixo do EMA_percent_s_force
        ):
            in_up_position = True  # Ativa sinal de compra
            signal_up[i] = 1  # Marca o ponto de compra
            in_down_position = False  # Interrompe possível sinal de venda

        # Detecção de cruzamento para venda
        elif (
            avg_ema_short_prev > avg_ema_long_prev and  # short estava acima de long
            avg_ema_short < avg_ema_long and  # short cruzou para baixo de long
            avg_ema_short > EMA_percent_s_force  # short está acima do EMA_percent_s_force
        ):
            in_down_position = True  # Ativa sinal de venda
            signal_down[i] = 1  # Marca o ponto de venda
            in_up_position = False  # Interrompe possível sinal de compra

        # Critério para encerramento de operações
        if in_up_position and avg_ema_long > 0:  # Fecha compra ao cruzar para cima de zero
            in_up_position = False
        elif in_down_position and avg_ema_long < 0:  # Fecha venda ao cruzar para baixo de zero
            in_down_position = False

        # # Manter o sinal ativo enquanto não há cruzamento contrário
        # if in_up_position:
        #     signal_up[i] = 1  # Mantém o sinal de compra ativo

        # if in_down_position:
        #     signal_down[i] = 1  # Mantém o sinal de venda ativo

    # Adiciona as colunas de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down

    return df






INDEX_SIGNAL_UP = 0
INDEX_SIGNAL_DOWN = 1
INDEX_time = 2
INDEX_Close = 3
INDEX_name = 4
EMA_percent_s = 5
INDEX_returns = 6
INDEX_strategy = 7

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
        
        # Inicialize esses atributos no início da classe para definir os valores iniciais
        self.trailing_stop_target = 0.01  # Define o alvo inicial do trailing stop
        self.trailing_stop_loss = stop_loss_percent         # Define o nível inicial de stop loss

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
        
    def close_trade(self, list_values, index, result, trigger_price):
        self.running = False
        self.end_time = list_values[INDEX_time][index]
        self.trigger_price = trigger_price
        self.result = result

    def update(self, list_values, index):
        self.count += 1

        # Processamento de trades diretamente sem funções auxiliares
        def process_trade(signal_type):
            if signal_type == 'buy':
                
                
                if self.strategy > 0.003 and self.trail_stop_trigger == 0:
                    self.trail_stop_trigger = 1
                elif self.strategy < 0.001 and self.trail_stop_trigger == 1:
                    result = 0.00001
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                elif self.strategy > abs(3*self.stop_loss_percent):
                    result = (list_values[INDEX_Close][index] - self.start_price)
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                elif self.strategy < self.stop_loss_percent:
                    result = (list_values[INDEX_Close][index] - self.start_price)
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
          
            elif signal_type == 'sell':
             
                if self.strategy > 0.003 and self.trail_stop_trigger == 0:
                    self.trail_stop_trigger = 1
                elif self.strategy < 0.001 and self.trail_stop_trigger == 1:
                    result = 0.00001
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                elif self.strategy > abs(3*self.stop_loss_percent):
                    result = (self.start_price - list_values[INDEX_Close][index])
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                elif self.strategy < self.stop_loss_percent:
                    result = (self.start_price - list_values[INDEX_Close][index])
                    self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                
                
        # Verificação dos sinais de COMPRA
        if self.SIGNAL_UP == 1:
            process_trade('buy')
        if self.SIGNAL_DOWN == 1:
            process_trade('sell')
        





class PairTradePercent:
    def __init__(self, df, 
                 strategy,
                 EMA_percent_s_force, 
                 stop_loss_percent, 
                 rsi_force, 
                 adx_force,
                 tc=-0.0005):
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

        # Aplicar a função para detectar sinais
        if self.strategy == 15:
            detect_signals_strategy_15(self.df)
        elif self.strategy == 16:
            detect_signals_strategy_16(self.df, self.EMA_percent_s_force)
       
        
    def run_test(self):
        
        # print("running test...")
        
        open_trades_m5 = deque()
        closed_trades_m5 = deque()

        list_value_refs = [
            self.df.SIGNAL_UP.values,
            self.df.SIGNAL_DOWN.values,
            self.df.time.values,
            self.df.Close.values,
            self.df.index.values,
            self.df.EMA_percent_s.values,
            self.df.returns.values,
            self.df.strategy.values,
        ]

        for index in range(self.df.shape[0]):
            
            if (
                (list_value_refs[INDEX_SIGNAL_UP][index] == 1 and list_value_refs[INDEX_SIGNAL_UP][index-1] == 0) or 
                (list_value_refs[INDEX_SIGNAL_DOWN][index] == 1 and list_value_refs[INDEX_SIGNAL_DOWN][index-1] == 0)
                ):
                open_trades_m5.append(Trade(list_value_refs, index,self.stop_loss_percent))  
                
                
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
                    ot.strategy += (2*self.tc)
                    
                    # caso o fechamento nao pegue o breakeven
                    # aplica custo de transação multiplcado por 2 para abertura e fechamento
                    if ot.trailing_stop_loss > ot.strategy:
                        ot.strategy = ot.trailing_stop_loss
                        
                    closed_trades_m5.append(ot)
                
                
                ot.total_opened = len(open_trades_m5)
            
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]


        self.len_close = len(closed_trades_m5)
        self.len_open = len(open_trades_m5)
        
        
        
        
        
        if self.len_close > 0:
            self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 

        # del self.df
        del closed_trades_m5
        del open_trades_m5
        # del self.df_results
