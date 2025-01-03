#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "calculate_signals_grid_trading1.h"
#include "calculate_signals_grid_trading2.h"

namespace py = pybind11;

PYBIND11_MODULE(signal_module, m) {
    // Função 1
    m.def(
        "calculate_signals_grid_trading1",
        [](const std::vector<double>& close_prices,
           const std::vector<double>& high_prices,
           const std::vector<double>& low_prices,
           const std::vector<int64_t>& timestamps,
           double movimentation,
           int time_in_minutes,
           py::array_t<int>& signal_up,
           py::array_t<int>& signal_down) {
            // Obter buffers de sinal_up e sinal_down
            auto buf_up = signal_up.mutable_unchecked<1>();
            auto buf_down = signal_down.mutable_unchecked<1>();

            // Converter para vetores C++ e processar
            std::vector<int> signal_up_vec(buf_up.shape(0), 0);
            std::vector<int> signal_down_vec(buf_down.shape(0), 0);

            // Chamar a função principal
            calculate_signals_grid_trading1(
                close_prices,
                high_prices,
                low_prices,
                timestamps,
                movimentation,
                time_in_minutes,
                signal_up_vec,
                signal_down_vec
            );

            // Atualizar o NumPy array com os resultados
            for (ssize_t i = 0; i < buf_up.shape(0); ++i) {
                buf_up(i) = signal_up_vec[i];
                buf_down(i) = signal_down_vec[i];
            }
        },
        "Calculate signals for grid trading 1"
    );

    // Função 2
    m.def(
        "calculate_signals_grid_trading2",
        [](const std::vector<double>& close_prices,
           const std::vector<double>& high_prices,
           const std::vector<double>& low_prices,
           const std::vector<int64_t>& timestamps,
           double movimentation,
           int time_in_minutes,
           py::array_t<int>& signal_up,
           py::array_t<int>& signal_down) {
            // Obter buffers de sinal_up e sinal_down
            auto buf_up = signal_up.mutable_unchecked<1>();
            auto buf_down = signal_down.mutable_unchecked<1>();

            // Converter para vetores C++ e processar
            std::vector<int> signal_up_vec(buf_up.shape(0), 0);
            std::vector<int> signal_down_vec(buf_down.shape(0), 0);

            // Chamar a função principal
            calculate_signals_grid_trading2(
                close_prices,
                high_prices,
                low_prices,
                timestamps,
                movimentation,
                time_in_minutes,
                signal_up_vec,
                signal_down_vec
            );

            // Atualizar o NumPy array com os resultados
            for (ssize_t i = 0; i < buf_up.shape(0); ++i) {
                buf_up(i) = signal_up_vec[i];
                buf_down(i) = signal_down_vec[i];
            }
        },
        "Calculate signals for grid trading 2"
    );
}
