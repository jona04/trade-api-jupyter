
import pandas as pd
import os.path
from infrastructure.quotehistory_collection import quotehistoryCollection as qc
import numpy as np

class MAResult:
    def __init__(self, df_trades, pair, ma_l, ma_s, granularity):
        self.pair = pair
        self.df_trades = df_trades
        self.ma_l = ma_l
        self.ma_s = ma_s
        self.granularity = granularity
        self.result = self.result_ob()

    def __repr__(self):
        return str(self.result)

    def result_ob(self):
        return dict(
            pair = self.pair,
            num_trades = self.df_trades.shape[0],
            total_gain = int(self.df_trades.GAIN.sum()),
            mean_gain = int(self.df_trades.GAIN.mean()),
            min_gain = int(self.df_trades.GAIN.min()),
            max_gain = int(self.df_trades.GAIN.max()),
            granularity = self.granularity,
            cross = f"{self.ma_s}_{self.ma_l}",
            ma_l = self.ma_l,
            ma_s = self.ma_s
        )




BUY = 1
SELL = -1
NONE = 0
get_mal_col = lambda x: f"MA_{x}"
add_cross = lambda x: f"{x.ma_s}_{x.ma_l}"

def is_trade(row):
    if row.DELTA >= 0 and row.DELTA_PREV < 0:
        return BUY
    elif row.DELTA < 0 and row.DELTA_PREV >= 0:
        return SELL
    return NONE

def load_price_data(pair, granularity, ma_list):
    df = pd.read_pickle(f"./data/{granularity}/{pair}_{granularity}.pkl")
    for ma in ma_list:
        df[get_mal_col(ma)] = df.mid_c.ewm(span=ma, min_periods=ma).mean()
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def get_result(df_trades, pip_location, tp_pips=200, sl_pips=1000):
    # Inicializa variáveis para controle das operações
    in_position = False
    entry_price = 0
    trade_type = 0  # 1 para BUY, -1 para SELL
    entry_index = None  # Índice de entrada

    # Define o valor do pip
    pip_value = pip_location

    # Listas para armazenar os valores de entrada, saída, resultado e tempo de saída
    mid_c_entry = [np.nan] * len(df_trades)
    mid_c_exit = [np.nan] * len(df_trades)
    trade_result = [np.nan] * len(df_trades)
    time_exit = [np.nan] * len(df_trades)

    # Loop através do DataFrame para identificar entrada, saída e calcular o resultado
    for index, row in df_trades.iterrows():
        if in_position:
            # Verifica o Take Profit e Stop Loss para uma posição aberta
            if trade_type == BUY:
                current_profit_pips = (row['mid_c'] - entry_price) / pip_value
                current_loss_pips = (entry_price - row['mid_c']) / pip_value
                if current_profit_pips >= tp_pips or current_loss_pips >= sl_pips or row['TRADE'] == SELL:
                    # Finaliza a operação de compra
                    mid_c_exit[entry_index] = row['mid_c']
                    trade_result[entry_index] = (mid_c_exit[entry_index] - mid_c_entry[entry_index]) / pip_value
                    time_exit[entry_index] = row['time']  # Armazena o tempo de saída
                    in_position = False
                    entry_index = None  # Reseta o índice de entrada

            elif trade_type == SELL:
                current_profit_pips = (entry_price - row['mid_c']) / pip_value
                current_loss_pips = (row['mid_c'] - entry_price) / pip_value
                if current_profit_pips >= tp_pips or current_loss_pips >= sl_pips or row['TRADE'] == BUY:
                    # Finaliza a operação de venda
                    mid_c_exit[entry_index] = row['mid_c']
                    trade_result[entry_index] = (mid_c_entry[entry_index] - mid_c_exit[entry_index]) / pip_value
                    time_exit[entry_index] = row['time']  # Armazena o tempo de saída
                    in_position = False
                    entry_index = None  # Reseta o índice de entrada

        # Inicia uma nova operação quando há um cruzamento
        if row['TRADE'] == BUY and not in_position:
            # Inicia uma operação de compra
            entry_price = row['mid_c']
            trade_type = BUY
            in_position = True
            entry_index = index  # Armazena o índice de entrada
            mid_c_entry[entry_index] = entry_price
        elif row['TRADE'] == SELL and not in_position:
            # Inicia uma operação de venda
            entry_price = row['mid_c']
            trade_type = SELL
            in_position = True
            entry_index = index  # Armazena o índice de entrada
            mid_c_entry[entry_index] = entry_price

    # Adiciona as colunas ao DataFrame
    df_trades['mid_c_entry'] = mid_c_entry
    df_trades['mid_c_exit'] = mid_c_exit
    df_trades['trade_result'] = trade_result
    df_trades['time_exit'] = time_exit

    return df_trades






def get_trades(df_analysis, quotehistory, granularity):
    df_trades = get_result(df_analysis.copy(), quotehistory.pipLocation)
    df_trades = df_trades[df_trades.TRADE != NONE]
    df_trades['GAIN'] = df_trades['trade_result'] / quotehistory.pipLocation
    df_trades['granularity'] = granularity
    df_trades['pair'] = quotehistory.name
    df_trades['GAIN_C'] = df_trades['GAIN'].cumsum()
    return df_trades

def asses_pair(price_data, ma_l, ma_s, quotehistory, granularity):
    df_analysis = price_data.copy()
    df_analysis['DELTA'] = df_analysis[ma_s] - df_analysis[ma_l]
    df_analysis['DELTA_PREV'] = df_analysis['DELTA'].shift(1)
    df_analysis['TRADE'] = df_analysis.apply(is_trade, axis=1)
    df_trades = get_trades(df_analysis, quotehistory, granularity)
    df_analysis['ma_s'] = ma_s
    df_analysis['ma_l'] = ma_l
    df_trades['cross'] = df_analysis.apply(add_cross, axis=1)
    return MAResult(
        df_trades,
        quotehistory.name,
        ma_l,
        ma_s,
        granularity
    )


def append_df_to_file(df, filename):

    if os.path.isfile(filename):
        fd = pd.read_pickle(filename)
        df = pd.concat([fd,df])
    df.reset_index(inplace=True, drop=True)
    df.to_pickle(filename)


def get_fullname(filepath, filename):
    return f"{filepath}/{filename}.pkl"


def process_macro(results_lists, filename):
    rl = [x.result for x in results_lists]
    df = pd.DataFrame.from_dict(rl)
    append_df_to_file(df, filename)


def process_trades(results_lists, filename):
    df = pd.concat([x.df_trades for x in results_lists])
    append_df_to_file(df, filename)




def process_results(results_list, filepath):
    process_macro(results_list, get_fullname(filepath, "ma_res_tp"))
    process_trades(results_list, get_fullname(filepath, "ma_trades_tp"))


def analyse_pair(quote, granularity, ma_long, ma_short, filepath):
    
    ma_list = set(ma_long+ma_short)
    pair = quote.name

    price_data = load_price_data(pair, granularity, ma_list)
    
    results_list = []

    for ma_l in ma_long:
        for ma_s in ma_short:
            if ma_l <= ma_s:
                continue

            ma_result = asses_pair(
                price_data,
                get_mal_col(ma_l),
                get_mal_col(ma_s),
                quote,
                granularity
            )
            results_list.append(ma_result)
    
    process_results(results_list, filepath)

            

def run_ma_tp_sim(curr_list=["EUR", "GBP", "JPY", "CAD", "AUD", "USD", "CHF", "NZD", "BTC", "ETH", "XAU"],
               granularity=["H4"],
               ma_long=[30],
               ma_short=[10],
               filepath="./data"
               ):
    qc.LoadQuotehistory("./data")
    for g in granularity:
        for p1 in curr_list:
            for p2 in curr_list:
                pair = f"{p1}{p2}"
                if pair in qc.quotehistory_dict.keys():
                    analyse_pair(qc.quotehistory_dict[pair], g, ma_long, ma_short, filepath)


