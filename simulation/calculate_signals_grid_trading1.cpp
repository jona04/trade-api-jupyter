#include "calculate_signals_grid_trading1.h"

void calculate_signals_grid_trading1(
    const std::vector<double>& close_prices,
    const std::vector<double>& high_prices,
    const std::vector<double>& low_prices,
    const std::vector<int64_t>& timestamps,
    double movimentation,
    int time_in_minutes,
    std::vector<int>& signal_up,
    std::vector<int>& signal_down
) {
    int64_t time_threshold = static_cast<int64_t>(time_in_minutes * 60 * 1e9); // Minutos para nanosegundos

    for (size_t j = 0; j < close_prices.size(); ++j) {
        int64_t time_accumulated = 0;
        double max_price = -std::numeric_limits<double>::infinity(); // Menor valor inicial
        double min_price = std::numeric_limits<double>::infinity();  // Maior valor inicial

        for (size_t i = j; i >= 0; --i) {
            time_accumulated = timestamps[j] - timestamps[i];
            
            if (high_prices[i] > max_price) {
                max_price = high_prices[i];
            }
            if (low_prices[i] < min_price) {
                min_price = low_prices[i];
            }
            
            if (time_accumulated >= time_threshold) {
                double max_ = std::abs(max_price / close_prices[j] - 1.0);
                double min_ = std::abs(min_price / close_prices[j] - 1.0);

                // Verifica movimentação para sinais
                if (max_ > min_) {
                    if (max_ >= movimentation) {
                        signal_up[j] = 1;
                    }
                } else {
                    if (min_ >= movimentation) {
                        signal_down[j] = 1;
                    }
                }
                break;
            }

            if (i == 0) { // Evitar underflow
                break;
            }
        }
    }
}
