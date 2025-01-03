import numpy as np
from signal_module import calculate_signals_grid_trading1

# Dados de exemplo
close_prices = np.array([100.0, 101.0, 102.0, 103.0], dtype=np.float64)
high_prices = np.array([102.0, 103.0, 104.0, 105.0], dtype=np.float64)
low_prices = np.array([98.0, 99.0, 100.0, 101.0], dtype=np.float64)
timestamps = np.array([0, 60_000_000_000, 120_000_000_000, 280_000_000_000], dtype=np.int64)
signal_up = np.zeros(len(close_prices), dtype=np.int32)
signal_down = np.zeros(len(close_prices), dtype=np.int32)

calculate_signals_grid_trading1(
    close_prices,
    high_prices,
    low_prices,
    timestamps,
    0.001,
    1,
    signal_up,
    signal_down
)

print("Signal Up:", signal_up)
print("Signal Down:", signal_down)
