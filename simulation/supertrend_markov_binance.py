
from collections import deque

import pandas as pd
import datetime as dt
import numpy as np
import math
import ta

NONE = 0

# Inicializando as constantes para os sinais
SIGNAL_UP = 1
SIGNAL_DOWN = 1

def calculate_supertrend(df, atr_multiplier=3, atr_period=15):

    """
    Cálculo básico do SuperTrend para um DataFrame já consolidado.

    Args:
        df (pd.DataFrame): DataFrame contendo 'High', 'Low', e 'Close'.
        atr_multiplier (float): Multiplicador para o cálculo das bandas.
        atr_period (int): Período para o cálculo do ATR.

    Returns:
        pd.DataFrame: DataFrame com colunas adicionais para SuperTrend, Upperband e Lowerband.
    """
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=atr_period)

    # Cálculo das bandas básicas
    avg_high_low = (df['High'] + df['Low']) / 2
    df['BasicUpperband'] = avg_high_low + (atr_multiplier * df['ATR'])
    df['BasicLowerband'] = avg_high_low - (atr_multiplier * df['ATR'])

    basic_upperband = df['BasicUpperband'].values
    basic_lowerband = df['BasicLowerband'].values
    
    # Inicializar listas para bandas superiores e inferiores ajustadas
    upper_band = [df['BasicUpperband'].iloc[0]]
    lower_band = [df['BasicLowerband'].iloc[0]]
    
    # Ajustar bandas com base nas condições de cruzamento
    for i in range(1, len(df)):
        # Ajuste da banda superior
        if (basic_upperband[i] < upper_band[i - 1]) or (df['Close'].iloc[i - 1] > upper_band[i - 1]):
            upper_band.append(basic_upperband[i])
        else:
            upper_band.append(upper_band[i - 1])

        # Ajuste da banda inferior
        if (basic_lowerband[i] > lower_band[i - 1]) or (df['Close'].iloc[i - 1] < lower_band[i - 1]):
            lower_band.append(basic_lowerband[i])
        else:
            lower_band.append(lower_band[i - 1])

    # Adicionar bandas ajustadas ao DataFrame
    df['Upperband'] = upper_band
    df['Lowerband'] = lower_band

    # Determinar a tendência e o SuperTrend
    trend = [1]  # Inicializando tendência: 1 = Alta, -1 = Baixa
    supertrend = [df['Upperband'].iloc[0]]  # Inicializando SuperTrend

    close = df['Close'].values
    
    for i in range(1, len(df)):
        # Atualizar tendência
        if trend[i - 1] == 1 and close[i] < lower_band[i]:
            trend.append(-1)
        elif trend[i - 1] == -1 and close[i] > upper_band[i]:
            trend.append(1)
        else:
            trend.append(trend[i - 1])

        # Atualizar SuperTrend
        if trend[i] == -1:
            supertrend.append(upper_band[i])
        else:
            supertrend.append(lower_band[i])

    df['Trend'] = trend
    df['SuperTrend'] = supertrend

    # Remover colunas temporárias
    df.drop(['BasicUpperband', 'BasicLowerband'], axis=1, inplace=True)

    return df


def detect_signals_supertrend_trading(df, atr_multiplier=3, atr_period=15, new_timeframe=15):
    """
    Método principal para calcular o SuperTrend com suporte a timeframes maiores.

    Args:
        df (pd.DataFrame): DataFrame contendo 'High', 'Low', e 'Close'.
        atr_multiplier (float): Multiplicador para o cálculo das bandas.
        atr_period (int): Período para o cálculo do ATR.
        new_timeframe (int): Número de candles para consolidar (ex: 60 para 1 hora em candles de 1 minuto).

    Returns:
        pd.DataFrame: DataFrame original com colunas adicionais para SuperTrend.
    """
    
    if new_timeframe > 1:
        # Agrupar os dados
        df_grouped = df.copy()
        df_grouped['group'] = (df_grouped.index // new_timeframe)
        
        grouped = df_grouped.groupby('group').agg({
            'High': 'max',
            'Low': 'min',
            'Close': 'last'
        }).reset_index(drop=True)
        
        # Calcular o SuperTrend no timeframe agrupado
        grouped = calculate_supertrend(grouped, atr_multiplier=atr_multiplier, atr_period=atr_period)

    
        # Interpolar os valores calculados para o dataframe original
        df[f'Upperband_{new_timeframe}'] = grouped['Upperband'].repeat(new_timeframe).iloc[:len(df)].values
        df[f'Lowerband_{new_timeframe}'] = grouped['Lowerband'].repeat(new_timeframe).iloc[:len(df)].values
        df[f'Trend_{new_timeframe}'] = grouped['Trend'].repeat(new_timeframe).iloc[:len(df)].values
        df[f'SuperTrend_{new_timeframe}'] = grouped['SuperTrend'].repeat(new_timeframe).iloc[:len(df)].values
    else:
        # Calcular o SuperTrend no timeframe original
        df = calculate_supertrend(df, atr_multiplier=atr_multiplier, atr_period=atr_period)

    # Detectando mudanças na coluna Trend
    df["SIGNAL_UP"] = np.where((df[f'Trend_{new_timeframe}'].shift(1) == -1) & (df[f'Trend_{new_timeframe}'] == 1), 1, 0)
    df["SIGNAL_DOWN"] = np.where((df[f'Trend_{new_timeframe}'].shift(1) == 1) & (df[f'Trend_{new_timeframe}'] == -1), 1, 0)

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
                
                # start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'buy')
                # start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'buy')
                
                # if self.strategy < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualiza o trailing stop quando ultrapassa o próximo alvo
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_target += (self.trailing_stop_target)
                #     self.trailing_stop_loss = self.strategy / 1.5
                if list_values[INDEX_SIGNAL_DOWN][index] == 1:
                    self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
               
            elif signal_type == 'sell':
                
                # start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'sell')
                # start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index], 'sell')
                
                # if self.strategy < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualiza o trailing stop quando ultrapassa o próximo alvo
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_target += (self.trailing_stop_target)
                #     self.trailing_stop_loss = self.strategy / 1.5
                if list_values[INDEX_SIGNAL_UP][index] == 1:
                    self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
             

        # Verificação dos sinais de COMPRA
        if self.SIGNAL_UP == 1:
            process_trade('buy')
        if self.SIGNAL_DOWN == 1:
            process_trade('sell')

TRIGGER_TYPE_BREAKEVEN_SL = 1
TRIGGER_TYPE_BREAKEVEN_TP = 2
TRIGGER_TYPE_SL = 3

class SupertrendTradeStrategy:
    def __init__(self, df, strategy, tp, sl, timeframe, tc=-0.0005):
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
        self.tp = tp
        self.sl = sl
        self.tc = tc
        self.new_timeframe = timeframe
        
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
            self.df = detect_signals_supertrend_trading(self.df, new_timeframe = self.new_timeframe)
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

        for index in range(1,self.df.shape[0]):
            
            if (
                (
                    (list_value_refs[INDEX_SIGNAL_UP][index] == 1) or 
                    (list_value_refs[INDEX_SIGNAL_DOWN][index] == 1)
                )
            ):
                opened_trades.append(Trade(list_value_refs, index,self.tp,self.sl))  
                
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
