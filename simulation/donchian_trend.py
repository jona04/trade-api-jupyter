from collections import deque

import pandas as pd
import datetime as dt
import numpy as np

NONE = 0

def remove_spread(df):
    for a in ["ask", "bid"]:
        for b in ["o", "h", "l", "c"]:
            c = f"{a}_{b}"
            df[c] = df[f"mid_{b}"]

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
def process_cross_up(df, i, band, signal, last_band_cross_up, band_name, next_band_value,
                     PROFIT_FACTOR, LOSS_FACTOR, pip_value, current_price, fixed_tp_sl, sl_type):
    if last_band_cross_up != band_name:
        df.at[i, 'SIGNAL_UP'] = signal
        if fixed_tp_sl:
            df.at[i, 'TP'] = current_price + (pip_value*PROFIT_FACTOR)
            df.at[i, 'SL'] = current_price - (pip_value*LOSS_FACTOR)
        else:
            df.at[i, 'TP'] = next_band_value
            sl_value = df.at[i, 'donchian_mid'] if sl_type == 'mid' else df.at[i, 'donchian_low']
            df.at[i, 'SL'] = current_price - (pip_value*LOSS_FACTOR)
        return band_name
    return last_band_cross_up

def process_cross_down(df, i, band, signal, last_band_cross_down, band_name, next_band_value, 
                       PROFIT_FACTOR, LOSS_FACTOR, pip_value, current_price, fixed_tp_sl, sl_type):
    if last_band_cross_down != band_name:
        df.at[i, 'SIGNAL_DOWN'] = signal
        if fixed_tp_sl:
            df.at[i, 'TP'] = current_price - (pip_value*PROFIT_FACTOR)
            df.at[i, 'SL'] = current_price + (pip_value*LOSS_FACTOR)
        else:
            df.at[i, 'TP'] = next_band_value
            sl_value = df.at[i, 'donchian_mid'] if sl_type == 'mid' else df.at[i, 'donchian_high']
            df.at[i, 'SL'] = current_price + (pip_value*LOSS_FACTOR)
        return band_name
    return last_band_cross_down


# Função para detectar os sinais de cruzamentos
def detect_signals(df, PROFIT_FACTOR, LOSS_FACTOR, pip_value, fixed_tp_sl, sl_type='not_mid', donchian_window_prev=100):

    last_band_cross_up = 0
    last_band_cross_down = 0

    ema_short = df['EMA_short'].values
    donchian_75 = df['donchian_75'].values
    donchian_mid = df['donchian_mid'].values
    donchian_25 = df['donchian_25'].values
    donchian_high = df['donchian_high'].values
    donchian_low = df['donchian_low'].values
    spread = df['SPREAD'].values
    ask_c = df['ask_c'].values
    bid_c = df['bid_c'].values
    mid_c = df['mid_c'].values
    donchian_size = df['donchian_size'].values

    # Inicializando listas para verificar a presença de sinais ativos
    up_active = False
    down_active = False

    for i in range(1, len(df)):
        if spread[i] < 50: #and donchian_size[i] > 300:

            # Cruzamentos de alta
            if ema_short[i-1] <= donchian_75[i-1] and ema_short[i] > donchian_75[i] and up_active:
                last_band_cross_up = process_cross_up(df, i, donchian_75[i], SIGNAL_75, 
                                                      last_band_cross_up, '75',donchian_mid[i], PROFIT_FACTOR, 
                                                      LOSS_FACTOR, pip_value, mid_c[i], fixed_tp_sl, sl_type)

            # Cruzamento de alta na banda MID
            if ema_short[i-1] <= donchian_mid[i-1] and ema_short[i] > donchian_mid[i] and up_active:
                last_band_cross_up = process_cross_up(df, i, donchian_mid[i], SIGNAL_MID, 
                                                      last_band_cross_up, 'mid', donchian_low[i], PROFIT_FACTOR, 
                                                      LOSS_FACTOR, pip_value, mid_c[i], fixed_tp_sl, sl_type)

            # Cruzamentos de baixa
            if ema_short[i-1] >= donchian_25[i-1] and ema_short[i] < donchian_25[i] and down_active:
                last_band_cross_up = process_cross_down(df, i, donchian_25[i], SIGNAL_25, 
                                                      last_band_cross_up, '25',donchian_high[i], PROFIT_FACTOR, 
                                                      LOSS_FACTOR, pip_value, mid_c[i], fixed_tp_sl, sl_type)

            # Cruzamento de baixa na banda MID
            if ema_short[i-1] >= donchian_mid[i-1] and ema_short[i] < donchian_mid[i] and down_active:
                last_band_cross_down = process_cross_down(df, i, donchian_mid[i], SIGNAL_MID, 
                                                          last_band_cross_down, 'mid', donchian_high[i], PROFIT_FACTOR, 
                                                          LOSS_FACTOR, pip_value, mid_c[i], fixed_tp_sl, sl_type)

            # Caso especial para donchian_high
            if ema_short[i-1] <= donchian_high[i-donchian_window_prev] and ema_short[i] > donchian_high[i-donchian_window_prev]:
                df.at[i, 'SIGNAL_UP'] = SIGNAL_HIGH
                last_band_cross_up = 'high'
                up_active = True  # sinal UP ativo
                down_active = False  # desativa sinal DOWN
                if fixed_tp_sl:
                    df.at[i, 'TP'] = mid_c[i] + (pip_value*PROFIT_FACTOR)
                    df.at[i, 'SL'] = mid_c[i] - (pip_value*LOSS_FACTOR)
                else:
                    df.at[i, 'TP'] = mid_c[i] + (pip_value*PROFIT_FACTOR)
                    sl_value = df.at[i, 'donchian_mid'] if sl_type == 'mid' else df.at[i, 'donchian_low']
                    df.at[i, 'SL'] = mid_c[i] - (pip_value*LOSS_FACTOR)

            
            # Caso especial para donchian_low
            if ema_short[i-1] >= donchian_low[i-donchian_window_prev] and ema_short[i] < donchian_low[i-donchian_window_prev]:
                df.at[i, 'SIGNAL_DOWN'] = SIGNAL_LOW
                last_band_cross_down = 'low'
                down_active = True  #sinal DOWN ativo
                up_active = False # desativa sinal UP
                if fixed_tp_sl:
                    df.at[i, 'TP'] = mid_c[i] - (pip_value*PROFIT_FACTOR)
                    df.at[i, 'SL'] = bid_c[i] + (pip_value*LOSS_FACTOR)
                else:
                    df.at[i, 'TP'] = mid_c[i] - (pip_value*PROFIT_FACTOR)
                    sl_value = df.at[i, 'donchian_mid'] if sl_type == 'mid' else df.at[i, 'donchian_high']
                    df.at[i, 'SL'] = bid_c[i] + (pip_value*LOSS_FACTOR)

    return df


INDEX_bid_c = 0
INDEX_ask_c = 1
INDEX_SIGNAL_UP = 2
INDEX_SIGNAL_DOWN = 3
INDEX_time = 4
INDEX_bid_h = 5
INDEX_bid_l = 6
INDEX_ask_h = 7
INDEX_ask_l = 8
INDEX_name = 9
INDEX_ema_short = 10
INDEX_donchian_87 = 11
INDEX_donchian_75 = 12
INDEX_donchian_62 = 13
INDEX_donchian_mid = 14
INDEX_donchian_37 = 15
INDEX_donchian_25 = 16
INDEX_donchian_12 = 17
INDEX_donchian_high = 18
INDEX_donchian_low = 19
INDEX_TP = 20
INDEX_SL = 21

class Trade:
    def __init__(self, list_values, index, profit_factor, loss_factor, pip_value,trans_cost,neg_multiplier):
        self.running = True
        self.start_index_m5 = list_values[INDEX_name][index]
        self.profit_factor = profit_factor
        self.loss_factor = loss_factor
        self.pip_value = pip_value
        self.count = 0
        self.neg_multiplier = neg_multiplier
        self.trans_cost = trans_cost
        self.trigger_type = NONE
        self.TP = list_values[INDEX_TP][index]
        self.SL = list_values[INDEX_SL][index]
        
        if list_values[INDEX_SIGNAL_UP][index] in [1,2,3,4,5,6,7,8,9]:
            self.start_price = list_values[INDEX_bid_c][index]
            self.trigger_price = list_values[INDEX_bid_c][index]
            
        if list_values[INDEX_SIGNAL_DOWN][index] in [1,2,3,4,5,6,7,8,9]:
            self.start_price = list_values[INDEX_ask_c][index]
            self.trigger_price = list_values[INDEX_ask_c][index]
            
        self.SIGNAL_UP = list_values[INDEX_SIGNAL_UP][index]
        self.SIGNAL_DOWN = list_values[INDEX_SIGNAL_DOWN][index]
        self.result = 0.0
        self.end_time = list_values[INDEX_time][index]
        self.start_time = list_values[INDEX_time][index]
        
    def close_trade(self, list_values, index, result, trigger_price, acumulated_loss):
        self.running = False
        self.end_time = list_values[INDEX_time][index]
        self.trigger_price = trigger_price

        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0

        if result < 0.0:
            self.result = (result - self.trans_cost)
            acumulated_loss.append(abs(self.result))
        else:
            self.result = result - self.trans_cost

        if min_acumulated_loss > 0.0:
            if result >= self.neg_multiplier*min_acumulated_loss:
                if len(acumulated_loss) > 0:
                    acumulated_loss = acumulated_loss[self.neg_multiplier:]

        return acumulated_loss

    def update(self, list_values, index, acumulated_loss):
        min_acumulated_loss = acumulated_loss[0] if len(acumulated_loss) > 0 else 0.0
        value_loss_trans_cost = (self.neg_multiplier * min_acumulated_loss) + self.trans_cost
        self.count += 1
        close_op = False
        
        # Processamento de trades diretamente sem funções auxiliares
        def process_trade(signal_type, signal_level_up, signal_level_down,close_op, acumulated_loss):
            if signal_type == 'buy':
                if min_acumulated_loss > 0.0:
                    result = (list_values[INDEX_bid_h][index] - self.start_price) / self.pip_value
                    if result >= value_loss_trans_cost:
                        self.trigger_type = self.SIGNAL_UP
                        result = value_loss_trans_cost
                        trigger_price = list_values[INDEX_bid_h][index]
                        acumulated_loss = self.close_trade(list_values, index, result, trigger_price, acumulated_loss)
                        close_op = True
                if close_op == False:
                    # if list_values[INDEX_SIGNAL_UP][index] != NONE or list_values[INDEX_SIGNAL_DOWN][index] != NONE:
                    #     self.trigger_type = self.SIGNAL_UP
                    #     result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                    #     acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)

                    if list_values[INDEX_SIGNAL_UP][index] == signal_level_up:
                        self.trigger_type = self.SIGNAL_UP
                        result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                        if result > 10:
                            acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)
                    elif list_values[INDEX_SIGNAL_DOWN][index] == signal_level_down:
                        self.trigger_type = self.SIGNAL_UP
                        result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                        acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)
                    
                    elif list_values[INDEX_bid_h][index] >= self.TP:
                        self.trigger_type = self.SIGNAL_UP
                        result = (self.TP - self.start_price) / self.pip_value
                        acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_h][index], acumulated_loss) 
                    elif list_values[INDEX_bid_l][index] <= self.SL:
                        self.trigger_type = self.SIGNAL_UP
                        result = (self.SL - self.start_price) / self.pip_value
                        # print(result,self.SIGNAL_DOWN)
                        acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_l][index], acumulated_loss) 
                    # elif self.SIGNAL_UP == SIGNAL_HIGH and list_values[INDEX_SIGNAL_UP][index] == SIGNAL_HIGH:
                    #     self.trigger_type = self.SIGNAL_UP
                    #     result = (list_values[INDEX_bid_c][index] - self.start_price) / self.pip_value
                    #     if result > 0:
                    #         acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_bid_c][index], acumulated_loss)
            else:
                if min_acumulated_loss > 0.0:
                    result = (self.start_price - list_values[INDEX_ask_l][index]) / self.pip_value
                    if result >= value_loss_trans_cost:
                        self.trigger_type = self.SIGNAL_DOWN
                        result = value_loss_trans_cost
                        trigger_price = list_values[INDEX_ask_l][index]
                        acumulated_loss = self.close_trade(list_values, index, result,trigger_price, acumulated_loss)
                        close_op = True
                if close_op == False:
                    # if list_values[INDEX_SIGNAL_UP][index] != NONE or list_values[INDEX_SIGNAL_DOWN][index] != NONE:
                    #     self.trigger_type = self.SIGNAL_UP
                    #     result = (self.start_price - list_values[INDEX_ask_c][index]) / self.pip_value
                    #     acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_ask_c][index], acumulated_loss)
            
                    if list_values[INDEX_SIGNAL_DOWN][index] == signal_level_up:
                        self.trigger_type = self.SIGNAL_DOWN
                        result = (self.start_price - list_values[INDEX_ask_c][index]) / self.pip_value
                        if result > 10:
                            acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_ask_c][index], acumulated_loss)
                    elif list_values[INDEX_SIGNAL_UP][index] == signal_level_down:
                        self.trigger_type = self.SIGNAL_DOWN
                        result = (self.start_price - list_values[INDEX_ask_c][index]) / self.pip_value
                        acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_ask_c][index], acumulated_loss) 
                    elif list_values[INDEX_ask_l][index] <= self.TP:
                        self.trigger_type = self.SIGNAL_DOWN
                        result = (self.start_price - self.TP) / self.pip_value
                        acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_ask_l][index], acumulated_loss) 
                    elif list_values[INDEX_ask_h][index] >= self.SL:
                        self.trigger_type = self.SIGNAL_DOWN
                        result = (self.start_price - self.SL) / self.pip_value
                        # print(result,self.SIGNAL_DOWN)
                        acumulated_loss = self.close_trade(list_values, index, result, list_values[INDEX_ask_h][index], acumulated_loss) 
                    # elif self.SIGNAL_DOWN == SIGNAL_LOW and list_values[INDEX_SIGNAL_DOWN][index] == SIGNAL_LOW:
                    #     self.trigger_type = self.SIGNAL_DOWN
                    #     result = (self.start_price - list_values[INDEX_ask_c][index]) / self.pip_value
                    #     if result > 0:
                    #         acumulated_loss = self.close_trade(list_values, index, result,list_values[INDEX_ask_c][index], acumulated_loss)
            return acumulated_loss
        
        # Verificação dos sinais de COMPRA
        if self.SIGNAL_UP == SIGNAL_HIGH:
            acumulated_loss = process_trade('buy', SIGNAL_HIGH, SIGNAL_MID,close_op, acumulated_loss)
        elif self.SIGNAL_UP == SIGNAL_75:
            acumulated_loss = process_trade('buy', SIGNAL_HIGH, SIGNAL_MID,close_op, acumulated_loss)
        # elif self.SIGNAL_UP == SIGNAL_MID:
        #     acumulated_loss = process_trade('buy', SIGNAL_75, SIGNAL_LOW,close_op, acumulated_loss)

        # Verificação dos sinais de VENDA
        # elif self.SIGNAL_DOWN == SIGNAL_MID:
        #     acumulated_loss = process_trade('sell', SIGNAL_25, SIGNAL_HIGH,close_op, acumulated_loss)
        elif self.SIGNAL_DOWN == SIGNAL_25:
            acumulated_loss = process_trade('sell', SIGNAL_LOW, SIGNAL_MID,close_op, acumulated_loss)
        elif self.SIGNAL_DOWN == SIGNAL_LOW:
            acumulated_loss = process_trade('sell', SIGNAL_LOW, SIGNAL_MID,close_op, acumulated_loss)

        return acumulated_loss




class DonchianTrend:
    def __init__(self, df,
                    pip_value,
                    use_spread=True,
                    LOSS_FACTOR = 1000,
                    PROFIT_FACTOR = 200,
                    fixed_tp_sl=True,
                    trans_cost=8,
                    neg_multiplier=1,
                    rev=False,
                    spread_limit=50,
                    donchian_window_prev = 100
                    ):
        self.use_spread = use_spread
        self.df = df
        self.donchian_window_prev = donchian_window_prev
        self.LOSS_FACTOR = LOSS_FACTOR
        self.PROFIT_FACTOR = PROFIT_FACTOR
        self.pip_value = pip_value
        self.fixed_tp_sl = fixed_tp_sl
        self.acumulated_loss = []
        self.trans_cost = trans_cost
        self.neg_multiplier = neg_multiplier
        self.rev = rev
        self.spread_limit = spread_limit
        self.len_close = 0
        self.len_open = 0
        
        self.prepare_data()
        
    def prepare_data(self):
        
        # print("prepare_data...")

        if self.use_spread == False:
            remove_spread(self.df)

        # Inicializando as novas colunas com zeros
        self.df['SIGNAL_UP'] = 0
        self.df['SIGNAL_DOWN'] = 0

        # Aplicar a função para detectar sinais
        detect_signals(self.df,self.PROFIT_FACTOR,self.LOSS_FACTOR,self.pip_value, 
                       self.fixed_tp_sl, sl_type='not_mid',donchian_window_prev=self.donchian_window_prev)
        
    def run_test(self):
        open_trades_m5 = deque()
        closed_trades_m5 = deque()

        list_value_refs = [
            self.df.bid_c.values,
            self.df.ask_c.values,
            self.df.SIGNAL_UP.values,
            self.df.SIGNAL_DOWN.values,
            self.df.time.values,
            self.df.bid_h.values,
            self.df.bid_l.values,
            self.df.ask_h.values,
            self.df.ask_l.values,
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
            self.df.TP.values,
            self.df.SL.values,
        ]

        for index in range(self.df.shape[0]):
            
            for ind, ot in enumerate(open_trades_m5):
                self.acumulated_loss = ot.update(list_value_refs, index, sorted(self.acumulated_loss,reverse=self.rev))
                if ot.running == False:
                    closed_trades_m5.append(ot)
            open_trades_m5 = [x for x in open_trades_m5 if x.running == True]

            if list_value_refs[INDEX_SIGNAL_UP][index] in [1,3]:
                open_trades_m5.append(Trade(list_value_refs, index, self.PROFIT_FACTOR, 
                                            self.LOSS_FACTOR, self.pip_value, self.trans_cost, self.neg_multiplier))  
                # print(len(open_trades_m5),len(closed_trades_m5))
            elif list_value_refs[INDEX_SIGNAL_DOWN][index] in [7,9]:
                open_trades_m5.append(Trade(list_value_refs, index, self.PROFIT_FACTOR, 
                                            self.LOSS_FACTOR, self.pip_value, self.trans_cost, self.neg_multiplier))  
                # print(len(open_trades_m5),len(closed_trades_m5))

        self.len_close = len(closed_trades_m5)
        self.len_open = len(open_trades_m5)
        self.df_results = pd.DataFrame.from_dict([vars(x) for x in closed_trades_m5]) 
        res_pos = self.df_results[self.df_results['result'] > 0]
        res_neg = self.df_results[self.df_results['result'] < 0]
        sum_neg = res_neg.result.sum() * -1
        sum_pos = res_pos.result.sum()
        
        print("")
        print("Result:", self.df_results.result.sum())
        print("Len loss: ", len(self.acumulated_loss))
        print("Len Open:" , len(open_trades_m5))
        print("Len Close:" , len(closed_trades_m5))
        print("Len Pos", len(res_pos))
        print("Len Neg", len(res_neg))
        print("Res pos", sum_pos)
        print("Res neg", sum_neg)
        print("Rel len pos neg", len(res_pos)/(len(res_pos)+ len(res_neg)))
        print("Rel len neg pos", len(res_neg)/(len(res_pos)+ len(res_neg)))
        print("Rel pos neg", sum_pos/(sum_pos+ sum_neg))
        print("Rel neg pos", sum_neg/(sum_pos+ sum_neg))
        print("")
