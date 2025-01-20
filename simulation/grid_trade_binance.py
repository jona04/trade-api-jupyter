from signal_module import calculate_signals_grid_trading1
from signal_module import calculate_signals_grid_trading2

from collections import deque

import pandas as pd
import datetime as dt
import numpy as np
import math

NONE = 0

# Inicializando as constantes para os sinais
SIGNAL_UP = 1
SIGNAL_DOWN = 1

def detect_signals_grid_trading1(df, time_in_minutes, movimentation):

    signal_up = np.zeros(len(df), dtype=np.int32)
    signal_down = np.zeros(len(df), dtype=np.int32)

    close_prices = df['Close'].values
    low_prices = df['Low'].values
    high_prices = df['High'].values
    timestamps = df['Time'].astype('int64').values
    
    time_threshold = time_in_minutes * 60  # Convertendo minutos para segundos
    time_threshold = np.timedelta64(int(time_threshold * 1e9), 'ns')

    calculate_signals_grid_trading1(
        close_prices,
        high_prices,
        low_prices,
        timestamps,
        movimentation,
        time_in_minutes,
        signal_up,
        signal_down
    )
    
    # Adicionando os vetores de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    
    return df



def detect_signals_grid_trading11(df, time_in_minutes, movimentation):

    signal_up = np.zeros(len(df), dtype=int)  # Long 
    signal_down = np.zeros(len(df), dtype=int)  # Short 

    close_prices = df['Close'].values
    low_prices = df['Low'].values
    high_prices = df['High'].values
    timestamps = df['Time'].values
    
    time_threshold = time_in_minutes * 60  # Convertendo minutos para segundos
    time_threshold = np.timedelta64(int(time_threshold * 1e9), 'ns')

    for j in range(int(time_in_minutes*60), len(df)):
        time_accumulated = 0
        max_price = None  # Para armazenar o maior preço no intervalo
        min_price = None  # Para armazenar o menor preço no intervalo
        for i in range(j, -1, -1):  # Itera para trás no tempo
            time_accumulated = timestamps[j] - timestamps[i]
            if max_price is None or high_prices[i] > max_price:
                max_price = high_prices[i]  # Atualiza o maior preço encontrado
            if min_price is None or low_prices[i] < min_price:
                min_price = low_prices[i]  # Atualiza o menor preço encontrado
            # Quando o tempo acumulado ultrapassa o limite
            if time_accumulated >= time_threshold:
                # Determina o sinal com base na movimentação
                max_ = abs(max_price / close_prices[j] - 1)
                min_ = abs(min_price / close_prices[j] - 1)
                
                # REVERSAO
                
                if max_ > min_:
                    if max_ >= movimentation:
                        signal_up[j] = 1
                else:
                    if min_ >= movimentation:
                        signal_down[j] = 1
                
                break
    
    # Adicionando os vetores de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    
    return df


def detect_signals_grid_trading2(df, time_in_minutes, movimentation):

    signal_up = np.zeros(len(df), dtype=np.int32)
    signal_down = np.zeros(len(df), dtype=np.int32)

    close_prices = df['Close'].values
    low_prices = df['Low'].values
    high_prices = df['High'].values
    timestamps = df['Time'].values
    
    time_threshold = time_in_minutes * 60  # Convertendo minutos para segundos
    time_threshold = np.timedelta64(int(time_threshold * 1e9), 'ns')

    calculate_signals_grid_trading2(
        close_prices,
        high_prices,
        low_prices,
        timestamps,
        movimentation,
        time_in_minutes,
        signal_up,
        signal_down
    )
    
    # Adicionando os vetores de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    
    return df


def detect_signals_grid_trading22(df, time_in_minutes, movimentation):

    signal_up = np.zeros(len(df), dtype=int)  # Long 
    signal_down = np.zeros(len(df), dtype=int)  # Short 

    close_prices = df['Close'].values
    low_prices = df['Low'].values
    high_prices = df['High'].values
    timestamps = df['Time'].values
    
    time_threshold = time_in_minutes * 60  # Convertendo minutos para segundos
    time_threshold = np.timedelta64(int(time_threshold * 1e9), 'ns')

    for j in range(int(time_in_minutes*60), len(df)):
        time_accumulated = 0
        max_price = None  # Para armazenar o maior preço no intervalo
        min_price = None  # Para armazenar o menor preço no intervalo
        for i in range(j, -1, -1):  # Itera para trás no tempo
            time_accumulated = timestamps[j] - timestamps[i]
            if max_price is None or high_prices[i] > max_price:
                max_price = high_prices[i]  # Atualiza o maior preço encontrado
            if min_price is None or low_prices[i] < min_price:
                min_price = low_prices[i]  # Atualiza o menor preço encontrado
            # Quando o tempo acumulado ultrapassa o limite
            if time_accumulated >= time_threshold:
                # Determina o sinal com base na movimentação
                max_ = abs(max_price / close_prices[j] - 1)
                min_ = abs(min_price / close_prices[j] - 1)
                
                # TENDENCIA
                
                if max_ > min_:
                    if max_ >= movimentation:
                        signal_down[j] = 1
                else:
                    if min_ >= movimentation:
                        signal_up[j] = 1
                break
    
    # Adicionando os vetores de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    
    return df


INDEX_SIGNAL_UP = 0
INDEX_SIGNAL_DOWN = 1
INDEX_time = 2
INDEX_Close = 3
INDEX_High = 4
INDEX_Low = 5
INDEX_index = 6
INDEX_returns = 7
INDEX_strategy = 8

class Trade:
    def __init__(self, list_values, index, tp, sl):
        self.running = True
        self.tp = tp
        self.sl = sl
        self.start_index_m5 = list_values[INDEX_index][index]
        self.count = 0
        self.trigger_type = NONE
        self.strategy = 0
        self.strategy_no_tc = 0
        self.total_opened = 0
        self.first_return = True
        self.trail_stop_trigger = 0

        self.trailing_stop_target = tp  # Define o alvo inicial do trailing stop
        self.trailing_stop_loss = -sl # Define o nível inicial de stop loss

        self.stop_loss = -0.03
        
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
            if signal_type == 'buy':
                
                start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'buy')
                start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'buy')
                
                if self.strategy < self.trailing_stop_loss:
                    # Fechamento pelo trailing stop
                    self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                elif self.strategy > self.trailing_stop_target:
                    # Atualiza o trailing stop quando ultrapassa o próximo alvo
                    self.trail_stop_trigger = 1
                    self.trailing_stop_target += (self.trailing_stop_target)
                    self.trailing_stop_loss = self.strategy / 1.5
                
                
                # if start_price_low_percent < -self.sl:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif start_price_high_percent > self.tp:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                    
            elif signal_type == 'sell':
                
                start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'sell')
                start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'sell')
                
                if self.strategy < self.trailing_stop_loss:
                    # Fechamento pelo trailing stop
                    self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                elif self.strategy > self.trailing_stop_target:
                    # Atualiza o trailing stop quando ultrapassa o próximo alvo
                    self.trail_stop_trigger = 1
                    self.trailing_stop_target += (self.trailing_stop_target)
                    self.trailing_stop_loss = self.strategy / 1.5
                
                
                # if start_price_high_percent < -self.sl:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif start_price_low_percent > self.tp:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                   

        # Verificação dos sinais de COMPRA
        if self.SIGNAL_UP == 1:
            process_trade('buy')
        if self.SIGNAL_DOWN == 1:
            process_trade('sell')

TRIGGER_TYPE_BREAKEVEN_SL = 1
TRIGGER_TYPE_BREAKEVEN_TP = 2
TRIGGER_TYPE_SL = 3

class GridTradeStrategy:
    def __init__(self, df, strategy, tp, sl, movimentation, grid, time_in_minutes, tc=-0.0005):
        """
        Inicializa a estratégia de grid trading.
        
        :param df: DataFrame com os dados de mercado.
        :param strategy: Estratégia a ser utilizada (inteiro identificador).
        :param tp: Percentual de Take Profit.
        :param sl: Percentual de Stop Loss.
        :param movimentation: 
        :param grid: Percentual mínimo de movimentação para abrir novas ordens.
        :param time_in_minutes: Intervalo de tempo para calcular movimentação acumulada.
        :param tc: Taxa de custo por trade.
        """
        self.df = df
        self.strategy = strategy
        self.grid = grid
        self.tp = tp
        self.sl = sl
        self.movimentation = movimentation
        self.time_in_minutes = time_in_minutes
        self.tc = tc
        
        self.first_price = df.Close.values[0]
        self.last_price = df.Close.values[-1]
        self.len_close = 0
        self.len_open = 0
        
        self.last_opened_price = 0.00000001
        
        self.closed_trades = []
        self.open_trades = deque()
        self.prepare_data()
        
    def prepare_data(self):
        """
        Prepara os dados para a estratégia, chamando o método correto para detectar sinais.
        Adiciona as colunas SIGNAL_UP e SIGNAL_DOWN ao DataFrame.
        """
        # print("Preparing data.")
        if self.strategy == 1:
            self.df = detect_signals_grid_trading1(self.df, self.time_in_minutes, self.movimentation)
        elif self.strategy == 11:
            self.df = detect_signals_grid_trading11(self.df, self.time_in_minutes, self.movimentation)
        elif self.strategy == 2:
            self.df = detect_signals_grid_trading2(self.df, self.time_in_minutes, self.movimentation)
        elif self.strategy == 22:
            self.df = detect_signals_grid_trading22(self.df, self.time_in_minutes, self.movimentation)
        else:
            raise ValueError(f"Estratégia {self.strategy} não implementada.")
    
    def run_test(self):
        
        # print("running test...")
        
        opened_trades = deque()
        closed_trades = deque()
        
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
        ]

        for index in range(self.df.shape[0]):
            
            if (
                (
                    (list_value_refs[INDEX_SIGNAL_UP][index] == 1) or 
                    (list_value_refs[INDEX_SIGNAL_DOWN][index] == 1)
                ) 
                and 
                len(opened_trades) == 0
                and 
                abs((self.last_opened_price-list_value_refs[INDEX_Close][index])/self.last_opened_price) > self.grid
            ):
                opened_trades.append(Trade(list_value_refs, index,self.tp,self.sl))  
                self.last_opened_price = list_value_refs[INDEX_Close][index]
                
            for ind, ot in enumerate(opened_trades):
                ot.update(list_value_refs, index)
                
                if ot.first_return: # usado para pegar o retorno apatir da segunda operação depois da abertura
                    ot.first_return = False
                else:
                    if ot.type == 'buy':
                        ot.strategy += list_value_refs[INDEX_returns][index]
                    elif ot.type == 'sell':
                        ot.strategy += (list_value_refs[INDEX_returns][index]*-1)
                    
                if ot.running == False:
                    # if ot.strategy > 0:
                    #     ot.strategy = self.tp
                    # else:
                    #     ot.strategy = -self.sl
                    
                    # if ot.strategy < ot.trailing_stop_loss:
                    # ot.strategy = ot.trailing_stop_loss
                        
                    ot.strategy += (2*self.tc)
                    
                    closed_trades.append(ot)
                
                ot.total_opened = len(opened_trades)
            
            opened_trades = [x for x in opened_trades if x.running == True]


        self.len_close = len(closed_trades)
        self.len_open = len(opened_trades)
        
        if self.len_close > 0:
            self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades]) 

        del self.df
        del closed_trades
        del opened_trades
