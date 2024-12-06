from collections import deque

import pandas as pd
import datetime as dt
import numpy as np
import math

NONE = 0


# Inicializando as constantes para os sinais
SIGNAL_UP = 1
SIGNAL_DOWN = 1



def detect_signals_strategy_1(df, entry_threshold, exit_threshold):
    """
    Gera sinais de entrada e saída com base no Z-Score.
    Mantém o sinal ativo até que o Z-Score cruze zero (se exit_threshold = 0)
    ou atinja a faixa de saída definida por exit_threshold.
    
    :param df: DataFrame com a coluna 'Z-Score'.
    :param entry_threshold: Limiar para entrada (ex.: ±2).
    :param exit_threshold: Limiar para saída (ex.: 0).
    :return: DataFrame atualizado com sinais específicos para cada par.
    """
    # Inicializando vetores para sinais
    signal_up_pair1 = np.zeros(len(df), dtype=int)  # Long Pair1
    signal_down_pair1 = np.zeros(len(df), dtype=int)  # Short Pair1
    signal_up_pair2 = np.zeros(len(df), dtype=int)  # Long Pair2
    signal_down_pair2 = np.zeros(len(df), dtype=int)  # Short Pair2
    
    z_score_values = df['Z-Score'].values  # Extraindo Z-Score como array
    
    # Flags para controlar a posição ativa
    position_pair1 = 0  # 1 = Long Pair1, -1 = Short Pair1, 0 = Sem posição
    position_pair2 = 0  # 1 = Long Pair2, -1 = Short Pair2, 0 = Sem posição
    
    # Iterar sobre os índices do DataFrame
    for i in range(1, len(z_score_values)):  # Começa no índice 1 para verificar o cruzamento
        if position_pair1 == 0 and position_pair2 == 0:  # Sem posição ativa
            if z_score_values[i] > entry_threshold:
                # Z > entry_threshold: Short Pair1, Long Pair2
                signal_down_pair1[i] = 1  # Short Pair1
                signal_up_pair2[i] = 1  # Long Pair2
                position_pair1 = -1
                position_pair2 = 1
            elif z_score_values[i] < -entry_threshold:
                # Z < -entry_threshold: Long Pair1, Short Pair2
                signal_up_pair1[i] = 1  # Long Pair1
                signal_down_pair2[i] = 1  # Short Pair2
                position_pair1 = 1
                position_pair2 = -1
        else:  # Posição ativa
            if exit_threshold == 0:
                # Verificar cruzamento de zero (mudança de sinal)
                if z_score_values[i] * z_score_values[i - 1] < 0:  # Mudança de sinal
                    position_pair1 = 0
                    position_pair2 = 0
            else:
                # Saída normal: Z-Score dentro do range de exit_threshold
                if -exit_threshold < z_score_values[i] < exit_threshold:
                    position_pair1 = 0
                    position_pair2 = 0

            # Manter posição ativa
            if position_pair1 == 1:
                signal_up_pair1[i] = 1  # Continuar Long Pair1
            elif position_pair1 == -1:
                signal_down_pair1[i] = 1  # Continuar Short Pair1
            if position_pair2 == 1:
                signal_up_pair2[i] = 1  # Continuar Long Pair2
            elif position_pair2 == -1:
                signal_down_pair2[i] = 1  # Continuar Short Pair2

    # Adicionando os vetores de sinal ao DataFrame
    df["SIGNAL_UP_PAIR1"] = signal_up_pair1
    df["SIGNAL_DOWN_PAIR1"] = signal_down_pair1
    df["SIGNAL_UP_PAIR2"] = signal_up_pair2
    df["SIGNAL_DOWN_PAIR2"] = signal_down_pair2
    
    return df


def detect_signals_strategy_2(df, entry_threshold, exit_threshold):
    """
    Gera sinais de entrada e saída com base no Z-Score e confirmação de volume.
    Mantém o sinal ativo até que o Z-Score cruze zero (se exit_threshold = 0)
    ou atinja a faixa de saída definida por exit_threshold.

    :param df: DataFrame com as colunas 'Z-Score' e 'Volume_Valid'.
    :param entry_threshold: Limiar para entrada (ex.: ±2).
    :param exit_threshold: Limiar para saída (ex.: 0).
    :return: DataFrame atualizado com sinais específicos para cada par.
    """
    # Inicializando vetores para sinais
    signal_up_pair1 = np.zeros(len(df), dtype=int)  # Long Pair1
    signal_down_pair1 = np.zeros(len(df), dtype=int)  # Short Pair1
    signal_up_pair2 = np.zeros(len(df), dtype=int)  # Long Pair2
    signal_down_pair2 = np.zeros(len(df), dtype=int)  # Short Pair2

    z_score_values = df['Z-Score'].values  # Extraindo Z-Score como array
    volume_valid = df['Volume_Valid'].values  # Extraindo validação de volume como array

    # Flags para controlar a posição ativa
    position_pair1 = 0  # 1 = Long Pair1, -1 = Short Pair1, 0 = Sem posição
    position_pair2 = 0  # 1 = Long Pair2, -1 = Short Pair2, 0 = Sem posição

    # Iterar sobre os índices do DataFrame
    for i in range(1, len(z_score_values)):  # Começa no índice 1 para verificar o cruzamento
        if position_pair1 == 0 and position_pair2 == 0:  # Sem posição ativa
            if z_score_values[i] > entry_threshold and volume_valid[i]:
                # Z > entry_threshold: Short Pair1, Long Pair2
                signal_down_pair1[i] = 1  # Short Pair1
                signal_up_pair2[i] = 1  # Long Pair2
                position_pair1 = -1
                position_pair2 = 1
            elif z_score_values[i] < -entry_threshold and volume_valid[i]:
                # Z < -entry_threshold: Long Pair1, Short Pair2
                signal_up_pair1[i] = 1  # Long Pair1
                signal_down_pair2[i] = 1  # Short Pair2
                position_pair1 = 1
                position_pair2 = -1
        else:  # Posição ativa
            if exit_threshold == 0:
                # Verificar cruzamento de zero (mudança de sinal)
                if z_score_values[i] * z_score_values[i - 1] < 0:  # Mudança de sinal
                    position_pair1 = 0
                    position_pair2 = 0
            else:
                # Saída normal: Z-Score dentro do range de exit_threshold
                if -exit_threshold < z_score_values[i] < exit_threshold:
                    position_pair1 = 0
                    position_pair2 = 0

            # Manter posição ativa
            if position_pair1 == 1:
                signal_up_pair1[i] = 1  # Continuar Long Pair1
            elif position_pair1 == -1:
                signal_down_pair1[i] = 1  # Continuar Short Pair1
            if position_pair2 == 1:
                signal_up_pair2[i] = 1  # Continuar Long Pair2
            elif position_pair2 == -1:
                signal_down_pair2[i] = 1  # Continuar Short Pair2

    # Adicionando os vetores de sinal ao DataFrame
    df["SIGNAL_UP_PAIR1"] = signal_up_pair1
    df["SIGNAL_DOWN_PAIR1"] = signal_down_pair1
    df["SIGNAL_UP_PAIR2"] = signal_up_pair2
    df["SIGNAL_DOWN_PAIR2"] = signal_down_pair2

    return df


INDEX_SIGNAL_UP_PAIR1 = 0
INDEX_SIGNAL_DOWN_PAIR1 = 1
INDEX_SIGNAL_UP_PAIR2 = 2
INDEX_SIGNAL_DOWN_PAIR2 = 3
INDEX_time = 4
INDEX_Close = 5
INDEX_name = 6
INDEX_returns = 7
INDEX_strategy = 8
INDEX_Low = 9
INDEX_High = 10

class Trade:
    def __init__(self, list_values, index):
        self.running = True
        self.start_index_m5 = list_values[INDEX_name][index]
        self.count = 0
        self.trigger_type = NONE
        self.strategy_pair1 = 0
        self.strategy_no_tc = 0
        self.total_opened = 0
        self.first_return = True
        self.trail_stop_trigger = 0

        self.trailing_stop_target = 0.01  # Define o alvo inicial do trailing stop
        self.trailing_stop_loss = -0.02 # Define o nível inicial de stop loss

        self.stop_loss = -0.03
        
        if list_values[INDEX_SIGNAL_UP_PAIR1][index] in [1]:
            self.type = 'buy'
           
        if list_values[INDEX_SIGNAL_DOWN_PAIR1][index] in [1]:
            self.type = 'sell'
        
        self.start_price = list_values[INDEX_Close][index]
        self.trigger_price = list_values[INDEX_Close][index]
        
        self.SIGNAL_UP = list_values[INDEX_SIGNAL_UP_PAIR1][index]
        self.SIGNAL_DOWN = list_values[INDEX_SIGNAL_DOWN_PAIR1][index]
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
                
                # if start_price_high_percent > self.trailing_stop_target:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif list_values[INDEX_SIGNAL_UP_PAIR1][index] == 0 and self.trail_stop_trigger == 0:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif start_price_low_percent < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif start_price_low_percent < self.stop_loss:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                    
                    
                if self.strategy_pair1 > self.trailing_stop_target:
                    # Atualiza o trailing stop quando ultrapassa o próximo alvo
                    self.trail_stop_trigger = 1
                    self.trailing_stop_target += (self.trailing_stop_target)
                    self.trailing_stop_loss = self.strategy_pair1 / 1.5
                elif list_values[INDEX_SIGNAL_UP_PAIR1][index] == 0 and self.trail_stop_trigger == 0:
                    self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                elif start_price_low_percent < self.trailing_stop_loss:
                    # Fechamento pelo trailing stop
                    self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                elif start_price_low_percent < self.stop_loss:
                    self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                    
                # start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'buy')
                # start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'buy')
                # if start_price_high_percent >= self.trailing_stop_target:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif start_price_low_percent <= self.trailing_stop_loss:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                    
            elif signal_type == 'sell':
                
                start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'sell')
                start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'sell')
                
                # if start_price_low_percent > self.trailing_stop_target:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif list_values[INDEX_SIGNAL_DOWN_PAIR1][index] == 0 and self.trail_stop_trigger == 0:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif start_price_high_percent < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif start_price_high_percent < self.stop_loss:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                    
                    
                start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'sell')
                if self.strategy_pair1 > self.trailing_stop_target:
                    # Atualiza o trailing stop quando ultrapassa o próximo alvo
                    self.trail_stop_trigger = 1
                    self.trailing_stop_target += (self.trailing_stop_target)
                    self.trailing_stop_loss = self.strategy_pair1 / 1.5
                elif list_values[INDEX_SIGNAL_DOWN_PAIR1][index] == 0 and self.trail_stop_trigger == 0:
                    self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                elif start_price_high_percent < self.trailing_stop_loss:
                    # Fechamento pelo trailing stop
                    self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                elif start_price_high_percent < self.stop_loss:
                    self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                    
                # start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'sell')
                # start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'sell')
                # if start_price_low_percent > self.trailing_stop_target:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif start_price_high_percent < self.trailing_stop_loss:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                    

        # Verificação dos sinais de COMPRA
        if self.SIGNAL_UP == 1:
            process_trade('buy')
        if self.SIGNAL_DOWN == 1:
            process_trade('sell')
        



TRIGGER_TYPE_BREAKEVEN_SL = 1
TRIGGER_TYPE_BREAKEVEN_TP = 2
TRIGGER_TYPE_SL = 3

class PairTradePercent:
    def __init__(self, 
                 df, 
                 strategy,
                 entry_threshold, 
                 exit_threshold,
                 corr=0,
                 spread_vol=0,
                 tc=-0.0005,
                 ):
        self.df = df
        self.first_price = df.Close_Pair1.values[0]
        self.last_price = df.Close_Pair1.values[-1]
        self.len_close = 0
        self.len_open = 0
        self.strategy = strategy
        self.tc = tc
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.corr = corr
        self.spread_vol = spread_vol
        
        self.prepare_data()
        
    def prepare_data(self):
        # print("prepare_data...")

        # Aplicar a função para detectar sinais

        if self.strategy == 1:
            detect_signals_strategy_1(self.df, self.entry_threshold, self.exit_threshold)
        if self.strategy == 2:
            detect_signals_strategy_2(self.df, self.entry_threshold, self.exit_threshold)
        
    def run_test(self):
        
        # print("running test...")
        
        open_trades_pair1 = deque()
        closed_trades_pair1 = deque()
        
        open_trades_pair2 = deque()
        closed_trades_pair2 = deque()

        list_value_refs = [
            self.df.SIGNAL_UP_PAIR1.values,
            self.df.SIGNAL_DOWN_PAIR1.values,
            self.df.SIGNAL_UP_PAIR2.values,
            self.df.SIGNAL_DOWN_PAIR2.values,
            self.df.time.values,
            self.df.Close_Pair1.values,
            self.df.index.values,
            self.df.returns_pair1.values,
            self.df.strategy_pair1.values,
            self.df.Low.values,
            self.df.High.values
        ]

        for index in range(self.df.shape[0]):
            
            if (
                # (
                #     (list_value_refs[INDEX_SIGNAL_UP_PAIR1][index] == 1 and list_value_refs[INDEX_SIGNAL_UP_PAIR1][index-1] == 0) or 
                #     (list_value_refs[INDEX_SIGNAL_DOWN_PAIR1][index] == 1 and list_value_refs[INDEX_SIGNAL_DOWN_PAIR1][index-1] == 0)
                # ) and 
                # len(open_trades_pair1) == 0
                (
                    (list_value_refs[INDEX_SIGNAL_UP_PAIR1][index] == 1) or 
                    (list_value_refs[INDEX_SIGNAL_DOWN_PAIR1][index] == 1)
                ) and 
                len(open_trades_pair1) == 0
            ):
                open_trades_pair1.append(Trade(list_value_refs, index))  
                
                
            for ind, ot in enumerate(open_trades_pair1):
                ot.update(list_value_refs, index)
                
                if ot.first_return: # usado para pegar o retorno apatir da segunda operação depois da abertura
                    ot.first_return = False
                else:
                    if ot.type == 'buy':
                        ot.strategy_pair1 += list_value_refs[INDEX_returns][index]
                        ot.strategy_no_tc += list_value_refs[INDEX_returns][index]
                    elif ot.type == 'sell':
                        ot.strategy_pair1 += (list_value_refs[INDEX_returns][index]*-1)
                        ot.strategy_no_tc += (list_value_refs[INDEX_returns][index]*-1)
                    
                if ot.running == False:
                    if ot.strategy_pair1 < ot.trailing_stop_loss:
                        ot.strategy_pair1 = ot.trailing_stop_loss
                    # if ot.strategy_pair1 > ot.trailing_stop_target:
                    #     ot.strategy_pair1 = ot.trailing_stop_target
                        
                    ot.strategy_pair1 += (2*self.tc)
                    
                    closed_trades_pair1.append(ot)
                
                ot.total_opened = len(open_trades_pair1)
            
            open_trades_pair1 = [x for x in open_trades_pair1 if x.running == True]


        self.len_close = len(closed_trades_pair1)
        self.len_open = len(open_trades_pair1)
        
        if self.len_close > 0:
            self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_pair1]) 

        del self.df
        del closed_trades_pair1
        del open_trades_pair1
        # del self.df_results
