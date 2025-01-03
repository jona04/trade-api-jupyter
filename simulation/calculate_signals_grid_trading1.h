#ifndef CALCULATE_SIGNALS_GRID_TRADING1_H
#define CALCULATE_SIGNALS_GRID_TRADING1_H

#include <vector>
#include <cmath>
#include <cstdint>

void calculate_signals_grid_trading1(
    const std::vector<double>& close_prices,
    const std::vector<double>& high_prices,
    const std::vector<double>& low_prices,
    const std::vector<int64_t>& timestamps,
    double movimentation,
    int time_in_minutes,
    std::vector<int>& signal_up,
    std::vector<int>& signal_down
);

#endif
