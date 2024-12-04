from collections import deque

import pandas as pd
import datetime as dt
import numpy as np
import math

NONE = 0


# Inicializando as constantes para os sinais
SIGNAL_UP = 1
SIGNAL_DOWN = 1


#abre alerta de sinal da operação de compra quando emaper cruza linha 0 e close acima/abaixo de ema long 
#abre operação quando alerta de sinal ativo e emaper vai para direção oposta no sentido da tendencia e atende ao
#requisito de força do emaper
#
#fecha operação quando close cruza ema longo no sentido contrario 
# ou
#emaper esta no sentido oposto da abertura e começa a mudar de sentido 
def detect_signals_strategy_1(df, EMA_percent_s_force):
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values

    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal, in_up_continue_signal = False, False
    in_down_first_signal, in_down_continue_signal = False, False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)
    
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if previous_EMA_percent_s > 0 and EMA_percent_s < 0:  # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and 
                (EMA_percent_s - previous_EMA_percent_s) > 0 and 
                EMA_percent_s < -EMA_percent_s_force
            ): 
                signal_up[i] = 1
                in_up_continue_signal = True
                in_up_first_signal = False
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (EMA_percent_s > 0 and (previous_EMA_percent_s - EMA_percent_s) > 0)
            ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
            else:
                signal_up[i] = 1

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if previous_EMA_percent_s < 0 and EMA_percent_s > 0:  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and 
                (EMA_percent_s - previous_EMA_percent_s) < 0 and 
                EMA_percent_s > EMA_percent_s_force
            ):  # EMA_1_medio começa a descer
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True
                in_down_first_signal - False

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (EMA_percent_s < 0 and (previous_EMA_percent_s - EMA_percent_s) < 0)
            ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    
    
    return df

#abre alerta de sinal da operação de compra quando emaper cruza linha 0 e close acima/abaixo de ema long 
#abre operação quando alerta de sinal ativo e emaper vai para direção oposta no sentido da tendencia e atende ao
#requisito de força do emaper
#
#fecha operação quando close cruza ema longo no sentido contrario 
# ou
#emaper cruza o valor 0 no sentido contrario ao que abriu a operação
def detect_signals_strategy_2(df, EMA_percent_s_force):
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
 
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if previous_EMA_percent_s > 0 and EMA_percent_s < 0:  # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if in_up_first_signal and (EMA_percent_s - previous_EMA_percent_s) > 0 and EMA_percent_s < -EMA_percent_s_force:  # EMA_1_medio começa a subir
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                in_up_first_signal =False
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_up_continue_signal = False
            else:
                signal_up[i] = 1

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if previous_EMA_percent_s < 0 and EMA_percent_s > 0:  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal 
                and (EMA_percent_s - previous_EMA_percent_s) < 0 
                and EMA_percent_s > EMA_percent_s_force  # EMA_1_medio começa a descer
            ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True
                in_down_first_signal = False

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
            ):  # Condições de interrupção
                in_down_continue_signal = False
            else:
                signal_down[i] = 1

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    
    return df

#abre alerta de sinal da operação de compra quando emaper cruza linha 0 e close acima/abaixo de ema long 
#abre operação quando alerta de sinal ativo e emaper vai para direção oposta no sentido da tendencia e atende ao
#requisito de força do emaper
#
#fecha operação quando close cruza ema longo no sentido contrario 
# ou
#emaper cruza o valor 0 no mesmo sentido que abriu a operação
def detect_signals_strategy_3(df, EMA_percent_s_force):
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
   
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if previous_EMA_percent_s > 0 and EMA_percent_s < 0:  # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if in_up_first_signal and (EMA_percent_s - previous_EMA_percent_s) > 0 and EMA_percent_s < -EMA_percent_s_force:  # EMA_1_medio começa a subir
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                in_up_first_signal = False
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if previous_EMA_percent_s < 0 and EMA_percent_s > 0:  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if in_down_first_signal and (EMA_percent_s - previous_EMA_percent_s) < 0 and EMA_percent_s > EMA_percent_s_force:  # EMA_1_medio começa a descer
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True
                in_down_first_signal = False

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    
    return df


# essa é a estratégia 1 + rsi
def detect_signals_strategy_4(df, EMA_percent_s_force, rsi_force):
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    RSI_values = df.RSI.values
   
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                RSI_values[i] < rsi_force # valida força do rsi menor que limiar de sobrevenda
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (EMA_percent_s > 0 and (previous_EMA_percent_s - EMA_percent_s) > 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0): # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                RSI_values[i] > (100-rsi_force) # valida força do rsi maior que limiar de sobrecomra
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (EMA_percent_s < 0 and (previous_EMA_percent_s - EMA_percent_s) < 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 1 + adx
def detect_signals_strategy_5(df, EMA_percent_s_force, adx_force):
    
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    ADX_values = df.ADX.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                ADX_values[i] < adx_force # valida força do rsi menor que limiar de força de tendencia
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (EMA_percent_s > 0 and (previous_EMA_percent_s - EMA_percent_s) > 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0):  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                ADX_values[i] < adx_force # valida força do adx menor que limiar de força de tendendcia
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (EMA_percent_s < 0 and (previous_EMA_percent_s - EMA_percent_s) < 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 2 + rsi
def detect_signals_strategy_6(df, EMA_percent_s_force, rsi_force):
    
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    RSI_values = df.RSI.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                RSI_values[i] < rsi_force # valida força do rsi menor que limiar de sobrevenda
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0): # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                RSI_values[i] > (100-rsi_force) # valida força do rsi maior que limiar de sobrecomra
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 2 + adx
def detect_signals_strategy_7(df, EMA_percent_s_force, adx_force):
    
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    ADX_values = df.ADX.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                ADX_values[i] < adx_force # valida força do rsi menor que limiar de força de tendencia
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0):  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                ADX_values[i] < adx_force # valida força do adx menor que limiar de força de tendendcia
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 3 + rsi
def detect_signals_strategy_8(df, EMA_percent_s_force, rsi_force):
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    RSI_values = df.RSI.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                RSI_values[i] < rsi_force # valida força do rsi menor que limiar de sobrevenda
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0): # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                RSI_values[i] > (100-rsi_force) # valida força do rsi maior que limiar de sobrecomra
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 3 + adx
def detect_signals_strategy_9(df, EMA_percent_s_force, adx_force):
    
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    ADX_values = df.ADX.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                ADX_values[i] < adx_force # valida força do rsi menor que limiar de força de tendencia
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0):  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                ADX_values[i] < adx_force # valida força do adx menor que limiar de força de tendendcia
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 1 + rsi + adx
def detect_signals_strategy_10(df, EMA_percent_s_force, rsi_force, adx_force):
    
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    ADX_values = df.ADX.values
    RSI_values = df.RSI.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                RSI_values[i] < rsi_force and # valida força do rsi menor que limiar de sobrevenda
                ADX_values[i] < adx_force # valida força do rsi menor que limiar de força de tendencia
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (EMA_percent_s > 0 and (previous_EMA_percent_s - EMA_percent_s) > 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0):  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                RSI_values[i] > (100-rsi_force) and # valida força do rsi maior que limiar de sobrecomra
                ADX_values[i] < adx_force # valida força do adx menor que limiar de força de tendendcia
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (EMA_percent_s < 0 and (previous_EMA_percent_s - EMA_percent_s) < 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 2 + rsi + adx
def detect_signals_strategy_11(df, EMA_percent_s_force, rsi_force, adx_force):
    
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    ADX_values = df.ADX.values
    RSI_values = df.RSI.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                RSI_values[i] < rsi_force and # valida força do rsi menor que limiar de sobrevenda
                ADX_values[i] < adx_force # valida força do rsi menor que limiar de força de tendencia
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0):  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                RSI_values[i] > (100-rsi_force) and # valida força do rsi maior que limiar de sobrecomra
                ADX_values[i] < adx_force # valida força do adx menor que limiar de força de tendendcia
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df

# essa é a estratégia 3 + rsi + adx
def detect_signals_strategy_12(df, EMA_percent_s_force, rsi_force, adx_force):
    
    
    close1_values = df.Close.values
    ema_long1_values = df.EMA_long.values
    EMA_percent_s_values = df.EMA_percent_s.values
    ADX_values = df.ADX.values
    RSI_values = df.RSI.values
     
    # Flags para rastrear a continuidade dos sinais
    in_up_first_signal = False
    in_up_continue_signal = False
    
    in_down_first_signal = False
    in_down_continue_signal = False

    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    for i in range(1, len(df)):
        # Valores atuais e anteriores
        close1 = close1_values[i]
        ema_long1 = ema_long1_values[i]
        EMA_percent_s = EMA_percent_s_values[i]
        previous_EMA_percent_s = EMA_percent_s_values[i-1]
        
        # Lógica para iniciar o SIGNAL_UP
        if close1 > ema_long1:
        # if close1 > ema_long1 or close1 < ema_long1:
            # Condição para iniciar o SIGNAL_UP
            if (previous_EMA_percent_s > 0 and EMA_percent_s < 0): # EMA_1_medio passa de positivo para negativo
                in_up_first_signal = True  # Ativa o sinal de subida
                in_up_continue_signal = False
                in_down_first_signal, in_down_continue_signal = False, False # Interrompe qualquer sinal de descida
                continue
            
            if (
                in_up_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) > 0 and # valida emaper subindo
                EMA_percent_s < -EMA_percent_s_force and  # emaper menor que limiar de força
                RSI_values[i] < rsi_force and # valida força do rsi menor que limiar de sobrevenda
                ADX_values[i] < adx_force # valida força do rsi menor que limiar de força de tendencia
                ):
                signal_up[i] = 1  # Marca o sinal de subida
                in_up_continue_signal = True
                
        # Condição para continuar ou interromper o SIGNAL_UP
        if in_up_continue_signal:
            if (
                close1 < ema_long1 or 
                (previous_EMA_percent_s < 0 and EMA_percent_s > 0)
                ):  # Condições de interrupção
                in_up_first_signal, in_up_continue_signal = False, False
        
            else:
                signal_up[i] = 1  # Mantém o sinal de subida contínuo

        # Lógica para iniciar o SIGNAL_DOWN (inverso do SIGNAL_UP)
        if close1 < ema_long1:
        # if close1 < ema_long1 or close1 > ema_long1:
            # Condição para iniciar o SIGNAL_DOWN
            if (previous_EMA_percent_s < 0 and EMA_percent_s > 0):  # EMA_1_medio passa de negativo para positivo
                in_down_first_signal = True  # Ativa o sinal de descida
                in_down_continue_signal = False
                in_up_first_signal, in_up_continue_signal = False, False  # Interrompe qualquer sinal de subida
                continue
            
            if (
                in_down_first_signal and # valida tendencia
                (EMA_percent_s - previous_EMA_percent_s) < 0 and # valida emaper descendo
                EMA_percent_s > EMA_percent_s_force and  # emaper manior que limiar de força
                RSI_values[i] > (100-rsi_force) and # valida força do rsi maior que limiar de sobrecomra
                ADX_values[i] < adx_force # valida força do adx menor que limiar de força de tendendcia
                ):
                signal_down[i] = 1  # Marca o sinal de descida
                in_down_continue_signal = True

        # Condição para continuar ou interromper o SIGNAL_DOWN
        if in_down_continue_signal:
            if (
                close1 > ema_long1 or 
                (previous_EMA_percent_s > 0 and EMA_percent_s < 0)
                ):  # Condições de interrupção
                in_down_first_signal, in_down_continue_signal = False, False
            else:
                signal_down[i] = 1  # Mantém o sinal de descida contínuo

    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
        
    return df


# emaper cross invertido
def detect_signals_strategy_13(df, EMA_percent_s_force):
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
    
    # Variáveis para rastrear o estado de compra e venda
    in_up_position = False  # Indica se estamos em uma operação de compra
    in_down_position = False  # Indica se estamos em uma operação de venda

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
            in_up_position = True  # Ativa sinal de compra
            signal_up[i] = 1  # Marca o ponto de compra
            in_down_position = False  # Interrompe possível sinal de venda

        # Detecção de cruzamento para venda
        elif (
            EMA_percent_s_prev > double_EMA_percent_s_prev and  # EMA_percent_s estava acima de double_EMA_percent_s
            EMA_percent_s < double_EMA_percent_s and # EMA_percent_s cruzou para baixo de double_EMA_percent_s
            EMA_percent_s > EMA_percent_s_force
        ):
            in_down_position = True  # Ativa sinal de venda
            signal_down[i] = 1  # Marca o ponto de venda
            in_up_position = False  # Interrompe possível sinal de compra

        # Continuação do sinal enquanto não há cruzamento contrário
        if in_up_position:
            signal_up[i] = 1  # Mantém o sinal de compra ativo

        if in_down_position:
            signal_down[i] = 1  # Mantém o sinal de venda ativo

    # Adiciona as colunas de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_down
    df["SIGNAL_DOWN"] = signal_up

    return df

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


def detect_signals_strategy_14a(df, EMA_percent_s_force):
    # Vetores booleanos para detecção de cruzamento
    cross_up = (df['Average_EMA_percent_ema_short'].shift(1) < df['Average_EMA_percent_ema_long'].shift(1)) & \
               (df['Average_EMA_percent_ema_short'] > df['Average_EMA_percent_ema_long']) & \
               (df['Average_EMA_percent_ema_short'] < -EMA_percent_s_force)
    
    cross_down = (df['Average_EMA_percent_ema_short'].shift(1) > df['Average_EMA_percent_ema_long'].shift(1)) & \
                 (df['Average_EMA_percent_ema_short'] < df['Average_EMA_percent_ema_long']) & \
                 (df['Average_EMA_percent_ema_short'] > EMA_percent_s_force)
    
    # Converte os cruzamentos em sinal
    df['SIGNAL_UP'] = cross_up.astype(int)
    df['SIGNAL_DOWN'] = cross_down.astype(int)
    
    return df


# emaper cross normal
def detect_signals_strategy_15(df, EMA_percent_s_force):
    """
    Função para detectar sinais de compra e venda com base no cruzamento de 
    EMA_percent_s e double_EMA_percent_s.

    Compra ocorre quando EMA_percent_s cruza para cima de double_EMA_percent_s.
    Venda ocorre quando EMA_percent_s cruza para baixo de double_EMA_percent_s.
    Operação é interrompida quando ocorre o cruzamento contrário.
    """
    
    # Obtém os valores das colunas necessárias
    EMA_percent_s_values = df.EMA_percent_s.values
    double_EMA_percent_s_values = df.double_EMA_percent_s.values
    
    # Variáveis para rastrear o estado de compra e venda
    in_up_position = False  # Indica se estamos em uma operação de compra
    in_down_position = False  # Indica se estamos em uma operação de venda

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
            EMA_percent_s > double_EMA_percent_s  # EMA_percent_s cruzou para cima de double_EMA_percent_s
        ):
            if EMA_percent_s < -EMA_percent_s_force:
                in_up_position = True  # Ativa sinal de compra
                signal_up[i] = 1  # Marca o ponto de compra
            in_down_position = False  # Interrompe possível sinal de venda

        # Detecção de cruzamento para venda
        elif (
            EMA_percent_s_prev > double_EMA_percent_s_prev and  # EMA_percent_s estava acima de double_EMA_percent_s
            EMA_percent_s < double_EMA_percent_s  # EMA_percent_s cruzou para baixo de double_EMA_percent_s
        ):
            if EMA_percent_s > EMA_percent_s_force:
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





def detect_signals_strategy_16(df):
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


def detect_signals_strategy_17(df, EMA_percent_s_force, stop_loss_percent):
    """
    Função para detectar sinais de compra e venda com base no cruzamento de
    Average_EMA_percent_ema_short e Average_EMA_percent_ema_long.
    
    Compra ocorre quando Average_EMA_percent_ema_short cruza para cima de Average_EMA_percent_ema_long,
    com Average_EMA_percent_ema_short abaixo de EMA_percent_s_force.
    
    Venda ocorre quando Average_EMA_percent_ema_short cruza para baixo de Average_EMA_percent_ema_long,
    com Average_EMA_percent_ema_short acima de EMA_percent_s_force.
    
    Adiciona o cálculo de percent_stop_loss com base em Donchian High/Low e Close.
    """

    # Obtém os valores das colunas necessárias
    avg_ema_short_values = df['Average_EMA_percent_ema_short'].values
    avg_ema_long_values = df['Average_EMA_percent_ema_long'].values
    close_values = df['Close'].values
    donchian_high_values = df['donchian_high'].values
    donchian_low_values = df['donchian_low'].values

    # Vetores de sinal de compra e venda
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    # Vetor para armazenar o cálculo do stop loss percentual
    percent_stop_loss = np.zeros(len(df), dtype=float)

    # Itera sobre o DataFrame a partir do segundo valor
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        avg_ema_short = avg_ema_short_values[i]
        avg_ema_short_prev = avg_ema_short_values[i-1]
        avg_ema_long = avg_ema_long_values[i]
        avg_ema_long_prev = avg_ema_long_values[i-1]
        close_price = close_values[i]
        donchian_high = donchian_high_values[i]
        donchian_low = donchian_low_values[i]
        
        # Detecção de cruzamento para compra
        if (
            avg_ema_short_prev < avg_ema_long_prev and  # short estava abaixo de long
            avg_ema_short > avg_ema_long and  # short cruzou para cima de long
            avg_ema_short < -EMA_percent_s_force  # short está abaixo do EMA_percent_s_force
        ):
            # Calcula a variação percentual entre Close e donchian_low
            percent_stop_loss[i] = ((close_price - donchian_low) / donchian_low)
            
            if percent_stop_loss[i] < stop_loss_percent:
                signal_up[i] = 1  # Marca o ponto de abertura de compra
            

        # Detecção de cruzamento para venda
        elif (
            avg_ema_short_prev > avg_ema_long_prev and  # short estava acima de long
            avg_ema_short < avg_ema_long and  # short cruzou para baixo de long
            avg_ema_short > EMA_percent_s_force  # short está acima do EMA_percent_s_force
        ):
            # Calcula a variação percentual entre donchian_high e Close
            percent_stop_loss[i] = ((donchian_high - close_price) / close_price)
            
            if percent_stop_loss[i] < stop_loss_percent:
                signal_down[i] = 1  # Marca o ponto de abertura de venda
            

    # Adiciona as colunas de sinal e percent_stop_loss ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    df["percent_stop_loss"] = percent_stop_loss * -1

    return df


import numpy as np

def detect_signals_strategy_18(df, stop_loss_percent):
    """
    Função para detectar sinais de compra e venda com base no cruzamento de zero
    de Average_EMA_percent_ema_short.

    Compra ocorre quando Average_EMA_percent_ema_short cruza zero para cima.
    Venda ocorre quando Average_EMA_percent_ema_short cruza zero para baixo.
    
    Adiciona o cálculo de percent_stop_loss com base em Donchian High/Low e Close.
    """

    # Obtém os valores das colunas necessárias
    avg_ema_short_values = df['Average_EMA_percent_ema_short'].values
    close_values = df['Close'].values
    donchian_high_values = df['donchian_high'].values
    donchian_low_values = df['donchian_low'].values

    # Vetores de sinal de compra e venda
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    # Vetor para armazenar o cálculo do stop loss percentual
    percent_stop_loss = np.zeros(len(df), dtype=float)

    # Itera sobre o DataFrame a partir do segundo valor
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        avg_ema_short = avg_ema_short_values[i]
        avg_ema_short_prev = avg_ema_short_values[i-1]
        close_price = close_values[i]
        donchian_high = donchian_high_values[i]
        donchian_low = donchian_low_values[i]
        
        # Detecção de cruzamento para compra (cruzamento para cima de zero)
        if avg_ema_short_prev < 0 and avg_ema_short > 0:
            # Calcula a variação percentual entre Close e donchian_low
            percent_stop_loss[i] = ((close_price - donchian_low) / donchian_low)
            
            if percent_stop_loss[i] < stop_loss_percent:
                signal_up[i] = 1  # Marca o ponto de abertura de compra
            

        # Detecção de cruzamento para venda (cruzamento para baixo de zero)
        elif avg_ema_short_prev > 0 and avg_ema_short < 0:
            # Calcula a variação percentual entre donchian_high e Close
            percent_stop_loss[i] = ((donchian_high - close_price) / close_price)
            
            if percent_stop_loss[i] < stop_loss_percent:
                signal_down[i] = 1  # Marca o ponto de abertura de venda

    # Adiciona as colunas de sinal e percent_stop_loss ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    df["percent_stop_loss"] = percent_stop_loss * -1

    return df




import numpy as np

def detect_signals_strategy_19(df, stop_loss_percent, lookback_period=20):
    """
    Estratégia de seguimento de tendência usando Donchian Channel.
    
    Compra ocorre quando o preço cruza acima de donchian_mid após tocar ou
    se aproximar de donchian_low, indicando possível reversão para tendência de alta.
    
    Venda ocorre quando o preço cruza abaixo de donchian_mid após tocar ou
    se aproximar de donchian_high, indicando possível reversão para tendência de baixa.
    
    Um stop loss é calculado baseado na distância percentual entre o preço de entrada e o limite do Donchian Channel.
    """

    # Obtém os valores das colunas necessárias
    close_values = df['Close'].values
    donchian_high_values = df['donchian_high'].values
    donchian_mid_values = df['donchian_mid'].values
    donchian_low_values = df['donchian_low'].values

    # Vetores de sinal de compra e venda
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    # Vetor para armazenar o cálculo do stop loss percentual
    percent_stop_loss = np.zeros(len(df), dtype=float)

    # Variáveis para controlar o estado das operações
    in_position = False  # Define se há uma posição aberta
    position_type = None  # Define o tipo de posição aberta ('buy' ou 'sell')

    # Itera sobre o DataFrame a partir do índice lookback_period para garantir que temos histórico suficiente
    for i in range(lookback_period, len(df)):
        close_price = close_values[i]
        donchian_high = donchian_high_values[i - lookback_period]
        donchian_mid = donchian_mid_values[i]
        donchian_low = donchian_low_values[i - lookback_period]

        # Sinal de Compra (Tendência de Alta)
        if not in_position and close_values[i-1] < donchian_mid_values[i-1] and close_price > donchian_mid:
            # Calcula a variação percentual entre Close e donchian_low
            percent_stop_loss[i] = ((close_price - donchian_low) / donchian_low)
            
            # if percent_stop_loss[i] < stop_loss_percent:
            signal_up[i] = 1  # Marca o ponto de abertura de compra
            in_position = True
            position_type = 'buy'

        # Sinal de Venda (Tendência de Baixa)
        elif not in_position and close_values[i-1] > donchian_mid_values[i-1] and close_price < donchian_mid:
            # Calcula a variação percentual entre donchian_high e Close
            percent_stop_loss[i] = ((donchian_high - close_price) / close_price)
            
            # if percent_stop_loss[i] < stop_loss_percent:
            signal_down[i] = 1  # Marca o ponto de abertura de venda
            in_position = True
            position_type = 'sell'

        # Verificação para encerrar a posição no extremo oposto
        if in_position:
            if position_type == 'buy' and (close_price > donchian_high or close_price < donchian_low):
                in_position = False  # Encerra a posição de compra
            elif position_type == 'sell' and (close_price > donchian_high or close_price < donchian_low):
                in_position = False  # Encerra a posição de venda

    # Adiciona as colunas de sinal e percent_stop_loss ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    df["percent_stop_loss"] = percent_stop_loss * -1  # Multiplica por -1 para mostrar como valor negativo

    return df


# emaper cross trend com adx
def detect_signals_strategy_20(df, EMA_percent_s_force, adx_force):
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
    ADX_values = df.ADX.values
    
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
            EMA_percent_s < -EMA_percent_s_force and
            ADX_values[i] < adx_force
        ):
            signal_up[i] = 1  # Marca o ponto de compra

        # Detecção de cruzamento para venda
        elif (
            EMA_percent_s_prev > double_EMA_percent_s_prev and  # EMA_percent_s estava acima de double_EMA_percent_s
            EMA_percent_s < double_EMA_percent_s and # EMA_percent_s cruzou para baixo de double_EMA_percent_s
            EMA_percent_s > EMA_percent_s_force and 
            ADX_values[i] < adx_force
        ):
            signal_down[i] = 1  # Marca o ponto de venda

    # Adiciona as colunas de sinal ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down

    return df


def detect_signals_strategy_21(df, stop_loss_percent):
    """
    Função para detectar sinais de compra e venda com base no cruzamento de zero
    de Average_EMA_percent_ema_short.

    Compra ocorre quando Average_EMA_percent_ema_short cruza zero para cima.
    Venda ocorre quando Average_EMA_percent_ema_short cruza zero para baixo.
    
    Adiciona o cálculo de percent_stop_loss com base em Donchian High/Low e Close.
    """

    # Obtém os valores das colunas necessárias
    avg_ema_super_long_values = df['Average_EMA_percent_ema_super_long'].values
    close_values = df['Close'].values
    donchian_high_values = df['donchian_high'].values
    donchian_low_values = df['donchian_low'].values

    # Vetores de sinal de compra e venda
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)

    # Vetor para armazenar o cálculo do stop loss percentual
    percent_stop_loss = np.zeros(len(df), dtype=float)

    # Itera sobre o DataFrame a partir do segundo valor
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        avg_ema_short = avg_ema_super_long_values[i]
        avg_ema_short_prev = avg_ema_super_long_values[i-1]
        close_price = close_values[i]
        donchian_high = donchian_high_values[i]
        donchian_low = donchian_low_values[i]
        
        # Detecção de cruzamento para compra (cruzamento para cima de zero)
        if avg_ema_short_prev < 0 and avg_ema_short > 0:
            # Calcula a variação percentual entre Close e donchian_low
            percent_stop_loss[i] = ((close_price - donchian_low) / donchian_low)
            
            # if percent_stop_loss[i] < stop_loss_percent:
            signal_up[i] = 1  # Marca o ponto de abertura de compra
            

        # Detecção de cruzamento para venda (cruzamento para baixo de zero)
        elif avg_ema_short_prev > 0 and avg_ema_short < 0:
            # Calcula a variação percentual entre donchian_high e Close
            percent_stop_loss[i] = ((donchian_high - close_price) / close_price)
            
            # if percent_stop_loss[i] < stop_loss_percent:
            signal_down[i] = 1  # Marca o ponto de abertura de venda

    # Adiciona as colunas de sinal e percent_stop_loss ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    df["percent_stop_loss"] = percent_stop_loss * -1

    return df



def detect_signals_strategy_22(df, stop_loss_percent):
    """
    Detecta sinais de compra e venda com base nos cruzamentos de zero de avg_ema_short e ema_long.
    
    Compra:
      - Ocorre apenas se ambos (ema_long e avg_ema_short) estiverem positivos após um cruzamento.
    Venda:
      - Ocorre apenas se ambos (ema_long e avg_ema_short) estiverem negativos após um cruzamento.
    """
    # Obtém os valores necessários
    avg_ema_super_long_values = df['Average_EMA_percent_ema_super_long'].values
    ema_long_values = df['EMA_long_delta'].values
    close_values = df['Close'].values
    donchian_high_values = df['donchian_high'].values
    donchian_low_values = df['donchian_low'].values

    # Inicializa os sinais, percent_stop_loss e estado atual
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)
    percent_stop_loss = np.zeros(len(df), dtype=float)
    position = None  # Estado atual: None, "comprado" ou "vendido"

    # Itera sobre o DataFrame
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        ema_long = ema_long_values[i]
        ema_long_prev = ema_long_values[i-1]
        avg_ema_short = avg_ema_super_long_values[i]
        avg_ema_short_prev = avg_ema_super_long_values[i-1]
        close_price = close_values[i]
        donchian_high = donchian_high_values[i]
        donchian_low = donchian_low_values[i]

        # Compra: ambos precisam estar positivos
        if position != "comprado" and ema_long > 0 and avg_ema_short > 0:
            # Confirma cruzamentos de alta
            if (avg_ema_short_prev < 0 or ema_long_prev < 0):
                # Calcula o stop loss
                percent_stop_loss[i] = ((close_price - donchian_low) / donchian_low)
                signal_up[i] = 1
                position = "comprado"  # Atualiza o estado

        # Venda: ambos precisam estar negativos
        elif position != "vendido" and ema_long < 0 and avg_ema_short < 0:
            # Confirma cruzamentos de baixa
            if (avg_ema_short_prev > 0 or ema_long_prev > 0):
                # Calcula o stop loss
                percent_stop_loss[i] = ((donchian_high - close_price) / close_price)
                signal_down[i] = 1
                position = "vendido"  # Atualiza o estado

        # Mantém o estado atual caso nenhum cruzamento significativo ocorra
        elif ema_long * avg_ema_short > 0:
            # Ambos estão no mesmo lado do zero, sem mudança de posição
            continue

    # Adiciona os sinais e percent_stop_loss ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    df["percent_stop_loss"] = percent_stop_loss * -1

    return df



def detect_signals_strategy_23(df, stop_loss_percent):
    """
    Detecta sinais de compra e venda com base no cruzamento de zero de ema_long.

    Compra:
      - Ocorre quando ema_long cruza de negativo para positivo.
    Venda:
      - Ocorre quando ema_long cruza de positivo para negativo.
    """
    # Obtém os valores necessários
    ema_long_values = df['EMA_long_delta'].values
    close_values = df['Close'].values
    donchian_high_values = df['donchian_high'].values
    donchian_low_values = df['donchian_low'].values

    # Inicializa os sinais, percent_stop_loss e estado atual
    signal_up = np.zeros(len(df), dtype=int)
    signal_down = np.zeros(len(df), dtype=int)
    percent_stop_loss = np.zeros(len(df), dtype=float)
    position = None  # Estado atual: None, "comprado" ou "vendido"

    # Itera sobre o DataFrame
    for i in range(1, len(df)):
        # Valores atuais e anteriores
        ema_long = ema_long_values[i]
        ema_long_prev = ema_long_values[i-1]
        close_price = close_values[i]
        donchian_high = donchian_high_values[i]
        donchian_low = donchian_low_values[i]

        # Compra: ema_long cruza de negativo para positivo
        if position != "comprado" and ema_long > 0 and ema_long_prev <= 0:
            # Calcula o stop loss
            percent_stop_loss[i] = ((close_price - donchian_low) / donchian_low)
            signal_up[i] = 1
            position = "comprado"  # Atualiza o estado

        # Venda: ema_long cruza de positivo para negativo
        elif position != "vendido" and ema_long < 0 and ema_long_prev >= 0:
            # Calcula o stop loss
            percent_stop_loss[i] = ((donchian_high - close_price) / close_price)
            signal_down[i] = 1
            position = "vendido"  # Atualiza o estado

    # Adiciona os sinais e percent_stop_loss ao DataFrame
    df["SIGNAL_UP"] = signal_up
    df["SIGNAL_DOWN"] = signal_down
    df["percent_stop_loss"] = percent_stop_loss * -1

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
        # self.percent_stop_loss = list_values[INDEX_percent_stop_loss][index]
        
        # Inicialize esses atributos no início da classe para definir os valores iniciais
        # if self.percent_stop_loss < -0.04:
        #     self.percent_stop_loss = -0.04
        
        # self.trailing_stop_target = abs(self.stop_loss_percent)  # Define o alvo inicial do trailing stop
        # self.trailing_stop_loss = self.stop_loss_percent # Define o nível inicial de stop loss

        self.trailing_stop_target = 0.05  # Define o alvo inicial do trailing stop
        self.trailing_stop_loss = -0.01 # Define o nível inicial de stop loss

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

    # def get_return(self,start_price, current_price, operation_type):
    #     if operation_type == "buy":
    #         return ((current_price - start_price) / start_price)
    #     elif operation_type == "sell":
    #         return ((start_price - current_price) / start_price)
    #     else:
    #         raise ValueError("operation_type deve ser 'buy' ou 'sell'")
    
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
                
                # elif self.strategy > self.trail_stop:
                #     if self.trail_stop_target == 0:
                #         self.trail_stop_target = 0.005
                #     else:
                #         self.trail_stop_target = self.trail_stop
                #     self.trail_stop = self.trail_stop + self.trail_stop
                # elif self.trail_stop_target > 0.001 and self.strategy < self.trail_stop_target:
                #     self.trigger_type = self.SIGNAL_UP
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                
                
                # if list_values[INDEX_SIGNAL_UP][index] == 1:
                #     if self.strategy < -self.stop_loss_percent:
                #         self.trigger_type = self.SIGNAL_UP
                #         result = (list_values[INDEX_Close][index] - self.start_price)
                #         self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # else:
                #     self.trigger_type = self.SIGNAL_UP
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                
                # start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'buy')
                # if self.strategy > 0.003 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                # elif start_price_low_percent < 0.001 and self.trail_stop_trigger == 1:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif self.strategy < -self.stop_loss_percent:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif list_values[INDEX_SIGNAL_DOWN][index] == 0:
                #     self.trigger_type = self.SIGNAL_DOWN
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                    
                
                # if self.strategy > 0.002:
                #     self.trigger_type = self.SIGNAL_UP
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy < stop_loss_percent:
                #     self.trigger_type = self.SIGNAL_UP
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
          
                # if self.strategy > 0.003 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                # elif self.strategy < 0.001 and self.trail_stop_trigger == 1:
                #     result = 0.00001
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy > abs(3*self.stop_loss_percent):
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy < self.stop_loss_percent:
                #     result = (list_values[INDEX_Close][index] - self.start_price)
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])

                # start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_Low][index], 'buy')
                # if self.strategy > 0.01 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                #     # self.trailing_stop_loss = 0.005
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualização dos níveis de trailing stop
                #     self.trailing_stop_target += self.trailing_stop_target  # Dobra o alvo do trailing stop para o próximo nível
                #     self.trailing_stop_loss = self.strategy / 1.2  # Atualiza o stop loss para metade do novo nível de lucro
                # elif start_price_low_percent < self.trailing_stop_loss:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])

                # if self.strategy > 0.02 and self.trail_stop_trigger == 0:
                #     # Transição para estado 1 (lucro significativo)
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_loss = 0.01
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualiza o trailing stop quando ultrapassa o próximo alvo
                #     self.trailing_stop_target += (self.trailing_stop_target / 2)
                #     self.trailing_stop_loss = self.strategy / 1.2
                # elif self.strategy < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])

                # if self.strategy > 0.02 and self.trail_stop_trigger == 0:
                #     # Transição para estado 1 (lucro significativo)
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_loss = 0.001
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualiza o trailing stop quando ultrapassa o próximo alvo
                #     self.trailing_stop_target += (self.trailing_stop_target / 2)
                #     self.trailing_stop_loss = self.strategy / 1.5
                # elif self.strategy < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])
                # elif list_values[INDEX_SIGNAL_DOWN][index] == 1 and self.trail_stop_trigger == 0:
                #     self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])

                if list_values[INDEX_SIGNAL_DOWN][index] == 1:
                    self.close_trade(list_values, index, 'buy', list_values[INDEX_Close][index])

            elif signal_type == 'sell':
                # if list_values[INDEX_SIGNAL_DOWN][index] == -1:
                #     pass
                # elif self.strategy > self.trail_stop:
                #     if self.trail_stop_target == 0:
                #         self.trail_stop_target = 0.005
                #     else:
                #         self.trail_stop_target = self.trail_stop
                #     self.trail_stop = self.trail_stop + self.trail_stop
                # elif self.trail_stop_target > 0.001 and self.strategy < self.trail_stop_target:
                #     self.trigger_type = self.SIGNAL_DOWN
                #     result = (self.start_price - list_values[INDEX_Close][index])
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                
                
                
                # if list_values[INDEX_SIGNAL_DOWN][index] == 1:
                #     if self.strategy < -self.stop_loss_percent:
                #         self.trigger_type = self.SIGNAL_DOWN
                #         result = (self.start_price - list_values[INDEX_Close][index])
                #         self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # else:
                #     self.trigger_type = self.SIGNAL_DOWN
                #     result = (self.start_price - list_values[INDEX_Close][index])
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                
                # start_price_high_percent = self.get_return(self.start_price, list_values[INDEX_High][index],'sell')
                # if self.strategy > 0.003 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                # elif start_price_high_percent < 0.001 and self.trail_stop_trigger == 1:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif self.strategy < -self.stop_loss_percent:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif list_values[INDEX_SIGNAL_DOWN][index] == 0:
                #     self.trigger_type = self.SIGNAL_DOWN
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                    
                
                
                # if self.strategy > 0.002:
                #     self.trigger_type = self.SIGNAL_DOWN
                #     result = (self.start_price - list_values[INDEX_Close][index])
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy < stop_loss_percent:
                #     self.trigger_type = self.SIGNAL_DOWN
                #     result = (self.start_price - list_values[INDEX_Close][index])
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                
                
                # if self.strategy > 0.003 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                # elif self.strategy < 0.001 and self.trail_stop_trigger == 1:
                #     result = 0.00001
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy > abs(3*self.stop_loss_percent):
                #     result = (self.start_price - list_values[INDEX_Close][index])
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                # elif self.strategy < self.stop_loss_percent:
                #     result = (self.start_price - list_values[INDEX_Close][index])
                #     self.close_trade(list_values, index, result, list_values[INDEX_Close][index])
                
                
                # start_price_low_percent = self.get_return(self.start_price, list_values[INDEX_High][index],'sell')
                # if self.strategy > 0.01 and self.trail_stop_trigger == 0:
                #     self.trail_stop_trigger = 1
                #     # self.trailing_stop_loss = 0.005
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualização dos níveis de trailing stop
                #     self.trailing_stop_target += self.trailing_stop_target  # Dobra o alvo do trailing stop para o próximo nível
                #     self.trailing_stop_loss = self.strategy / 1.2  # Atualiza o stop loss para metade do novo nível de lucro
                # elif start_price_low_percent < self.trailing_stop_loss:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                
                
                # if self.strategy > 0.02 and self.trail_stop_trigger == 0:
                #     # Transição para estado 1 (lucro significativo)
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_loss = 0.01
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualiza o trailing stop quando ultrapassa o próximo alvo
                #     self.trailing_stop_target += (self.trailing_stop_target / 2)
                #     self.trailing_stop_loss = self.strategy / 1.2
                # elif self.strategy < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])

                # if self.strategy > 0.02 and self.trail_stop_trigger == 0:
                #     # Transição para estado 1 (lucro significativo)
                #     self.trail_stop_trigger = 1
                #     self.trailing_stop_loss = 0.001
                # elif self.strategy > self.trailing_stop_target:
                #     # Atualiza o trailing stop quando ultrapassa o próximo alvo
                #     self.trailing_stop_target += (self.trailing_stop_target / 2)
                #     self.trailing_stop_loss = self.strategy / 1.5
                # elif self.strategy < self.trailing_stop_loss:
                #     # Fechamento pelo trailing stop
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])
                # elif list_values[INDEX_SIGNAL_UP][index] == 1 and self.trail_stop_trigger == 0:
                #     self.close_trade(list_values, index, 'sell', list_values[INDEX_Close][index])

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

        # Aplicar a função para detectar sinais
        if self.strategy == 1:
            detect_signals_strategy_1(self.df, self.EMA_percent_s_force)
        elif self.strategy == 2:
            detect_signals_strategy_2(self.df, self.EMA_percent_s_force)
        elif self.strategy == 3:
            detect_signals_strategy_3(self.df, self.EMA_percent_s_force)
        elif self.strategy == 4:
            detect_signals_strategy_4(self.df, self.EMA_percent_s_force, self.rsi_force)
        elif self.strategy == 5:
            detect_signals_strategy_5(self.df, self.EMA_percent_s_force, self.adx_force)
        elif self.strategy == 6:
            detect_signals_strategy_6(self.df, self.EMA_percent_s_force, self.rsi_force)
        elif self.strategy == 7:
            detect_signals_strategy_7(self.df, self.EMA_percent_s_force, self.adx_force)
        elif self.strategy == 8:
            detect_signals_strategy_8(self.df, self.EMA_percent_s_force, self.rsi_force)
        elif self.strategy == 9:
            detect_signals_strategy_9(self.df, self.EMA_percent_s_force, self.adx_force)
        elif self.strategy == 10:
            detect_signals_strategy_10(self.df, self.EMA_percent_s_force, self.rsi_force, self.adx_force)
        elif self.strategy == 11:
            detect_signals_strategy_11(self.df, self.EMA_percent_s_force, self.rsi_force, self.adx_force)
        elif self.strategy == 12:
            detect_signals_strategy_12(self.df, self.EMA_percent_s_force, self.rsi_force, self.adx_force)
        elif self.strategy == 13:
            detect_signals_strategy_13(self.df, self.EMA_percent_s_force)
        elif self.strategy == 14:
            detect_signals_strategy_14(self.df, self.EMA_percent_s_force)
        elif self.strategy == 15:
            detect_signals_strategy_15(self.df, self.EMA_percent_s_force)
        elif self.strategy == 16:
            detect_signals_strategy_16(self.df)
        elif self.strategy == 17:
            detect_signals_strategy_17(self.df, self.EMA_percent_s_force, self.stop_loss_percent)
        elif self.strategy == 18:
            detect_signals_strategy_18(self.df, self.stop_loss_percent)
        elif self.strategy == 19:
            detect_signals_strategy_19(self.df, self.stop_loss_percent)
        elif self.strategy == 20:
            detect_signals_strategy_20(self.df, self.EMA_percent_s_force, self.adx_force)
        elif self.strategy == 21:
            detect_signals_strategy_21(self.df, self.stop_loss_percent)
        elif self.strategy == 22:
            detect_signals_strategy_22(self.df, self.stop_loss_percent)
        elif self.strategy == 23:
            detect_signals_strategy_23(self.df, self.stop_loss_percent)
        
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
                    # if ot.trail_stop_trigger == 1:
                    #     if ot.strategy < 0:
                    #         ot.strategy = 0.01
                    #         ot.trigger_type = TRIGGER_TYPE_BREAKEVEN_SL
                    #     elif ot.strategy > 0.01:
                    #         ot.strategy += 0.01
                    #         ot.trigger_type = TRIGGER_TYPE_BREAKEVEN_TP
                    # else:
                    #     ot.trigger_type = TRIGGER_TYPE_SL
                    
                    # if ot.strategy < -0.005:
                    #     ot.strategy = -0.005
                    
                    if ot.strategy < 0.001 and ot.trail_stop_trigger == 1:
                        ot.strategy = 0.001
                    
                    ot.strategy_real = ot.strategy
                    # if ot.strategy_real > 0:
                    #     ot.strategy_real = ot.strategy/2
                    
                    ot.strategy_real += (2*self.tc)
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
