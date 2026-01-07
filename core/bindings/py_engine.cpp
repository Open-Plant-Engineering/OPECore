#include <pybind11/pybind11.h>
#include "engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(OPE_core_engine_py, m) {
    py::class_<Engine>(m, "Engine")
        .def(py::init<>())
        .def("add", &Engine::add);
}