
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



# Função para calcular a variação percentual acumulada
def calculate_percent_change(close_prices, window):
    percent_change = np.zeros(len(close_prices))

    for i in range(window, len(close_prices)):
        window_sum = 0.0
        for j in range(i - window + 1, i + 1):
            percent_change[j] = (close_prices[j] - close_prices[j - 1]) / close_prices[j - 1] * 100
            window_sum += percent_change[j]
        percent_change[i] = window_sum

    return percent_change

# Função para calcular a EMA
def calculate_ema(values, period):
    ema = np.zeros(len(values))
    multiplier = 2 / (period + 1)
    ema[period - 1] = values[period - 1]  # O primeiro valor da EMA é igual ao valor inicial
    for i in range(period, len(values)):
        ema[i] = (values[i] - ema[i - 1]) * multiplier + ema[i - 1]
    return ema

# Função para calcular os indicadores e adicionar ao DataFrame
def calculate_indicators(df, window, ma_list):
    # Obtém os preços de fechamento da coluna 'mid_c'
    close_prices = df['mid_c'].values

    # Calcula a variação percentual acumulada
    percent_change = calculate_percent_change(close_prices, window)

    # Calcula as EMAs
    for ma in ma_list:
        df[get_mal_col(ma)] = calculate_ema(percent_change, ma)
        
    # Adiciona os resultados ao DataFrame original
    df['Percent Change'] = percent_change

    return df


def load_price_data(pair, granularity, window, ma_list):
    df = pd.read_pickle(f"./data/{pair}_{granularity}.pkl")
    
    
    df = calculate_indicators(df, window, ma_list)
    
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def get_resul(df_trades):
    # Inicializa variáveis para controle das operações
    in_position = False
    entry_price = 0
    trade_type = 0  # 1 para BUY, -1 para SELL

    # Listas para armazenar os valores de entrada e saída
    mid_c_entry = []
    mid_c_exit = []
    trade_result = []

    # Loop através do DataFrame para identificar entrada, saída e calcular o resultado
    for index, row in df_trades.iterrows():
        if row['TRADE'] == BUY and not in_position:
            # Inicia uma operação de compra
            entry_price = row['mid_c']
            mid_c_entry.append(entry_price)  # Armazena o preço de entrada
            mid_c_exit.append(np.nan)  # Ainda não há preço de saída
            trade_result.append(np.nan)  # Ainda não há resultado
            trade_type = BUY
            in_position = True
        elif row['TRADE'] == SELL and not in_position:
            # Inicia uma operação de venda
            entry_price = row['mid_c']
            mid_c_entry.append(entry_price)  # Armazena o preço de entrada
            mid_c_exit.append(np.nan)  # Ainda não há preço de saída
            trade_result.append(np.nan)  # Ainda não há resultado
            trade_type = SELL
            in_position = True
        elif row['TRADE'] == SELL and trade_type == BUY and in_position:
            # Finaliza a operação de compra
            mid_c_exit[-1] = row['mid_c']  # Atualiza o preço de saída
            trade_result[-1] = mid_c_exit[-1] - mid_c_entry[-1]  # Resultado para compra (positivo se venda maior que compra)
            # Atualiza para nova operação de venda
            entry_price = row['mid_c']
            mid_c_entry.append(entry_price)  # Armazena o novo preço de entrada
            mid_c_exit.append(np.nan)  # Ainda não há preço de saída
            trade_result.append(np.nan)  # Ainda não há resultado
            trade_type = SELL
        elif row['TRADE'] == BUY and trade_type == SELL and in_position:
            # Finaliza a operação de venda
            mid_c_exit[-1] = row['mid_c']  # Atualiza o preço de saída
            trade_result[-1] = mid_c_entry[-1] - mid_c_exit[-1]  # Resultado para venda (positivo se venda maior que compra)
            # Atualiza para nova operação de compra
            entry_price = row['mid_c']
            mid_c_entry.append(entry_price)  # Armazena o novo preço de entrada
            mid_c_exit.append(np.nan)  # Ainda não há preço de saída
            trade_result.append(np.nan)  # Ainda não há resultado
            trade_type = BUY
        else:
            # Caso não haja operação, preenche com NaN
            mid_c_entry.append(np.nan)
            mid_c_exit.append(np.nan)
            trade_result.append(np.nan)

    # Adiciona as colunas ao DataFrame
    df_trades['mid_c_entry'] = mid_c_entry
    df_trades['mid_c_exit'] = mid_c_exit
    df_trades['trade_result'] = trade_result
    return df_trades

def get_trades(df_analysis, quotehistory, granularity):
    df_trades = df_analysis[df_analysis.TRADE != NONE].copy()
    df_trades = get_resul(df_trades)
    
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
    process_macro(results_list, get_fullname(filepath, "returned_ma_res"))
    process_trades(results_list, get_fullname(filepath, "returned_ma_trades"))


def analyse_pair(quote, granularity, window, ma_long, ma_short, filepath):
    
    ma_list = set(ma_long+ma_short)
    pair = quote.name

    price_data = load_price_data(pair, granularity, window, ma_list)
    
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

            

def run_returned_ma_sim(curr_list=["EUR", "GBP", "JPY", "CAD", "AUD", "USD"],
               granularity=["D1"],
               ma_long=[20,50,100,200,400],
               ma_short=[10, 20, 50,100],
               window=50,
               filepath="./data"
               ):
    qc.LoadQuotehistory("./data")
    for g in granularity:
        for p1 in curr_list:
            for p2 in curr_list:
                pair = f"{p1}{p2}"
                if pair in qc.quotehistory_dict.keys():
                    analyse_pair(qc.quotehistory_dict[pair], g, window, ma_long, ma_short, filepath)


