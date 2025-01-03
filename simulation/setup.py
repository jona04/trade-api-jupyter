from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "signal_module",
        [
            "bindings.cpp",
            "calculate_signals_grid_trading1.cpp",
            "calculate_signals_grid_trading2.cpp",
        ],
    ),
]

setup(
    name="signal_module",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
