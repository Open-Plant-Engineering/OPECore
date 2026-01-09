#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "JSON/JsonCRUD.hpp"

namespace py = pybind11;

PYBIND11_MODULE(py_JsonCRUD, m) {
    m.doc() = "Python bindings for JsonCRUD";

    py::class_<JsonCRUD>(m, "JsonCRUD")
        .def(py::init<const std::string&>())
        .def("create", &JsonCRUD::create)
        .def("read", &JsonCRUD::read)
        .def("update", &JsonCRUD::update)
        .def("remove", &JsonCRUD::remove)
        .def("printAll", &JsonCRUD::printAll);

    // Static helpers used by SessionManager
    m.def("createFile",
        [](const std::string& file, const std::string& text) {
            std::string err;
            bool ok = JsonCRUD::createFile(file, text, err);
            return py::make_tuple(ok, err);
        });

    m.def("ensureBaseAndWorking",
        [](const std::string& orig, const std::string& base, const std::string& work) {
            std::string err;
            bool ok = JsonCRUD::ensureBaseAndWorking(orig, base, work, err);
            return py::make_tuple(ok, err);
        });

    m.def("modifyAttributeInWorking",
        [](const std::string& work, const std::string& key, const std::string& val) {
            std::string err;
            bool ok = JsonCRUD::modifyAttributeInWorking(work, key, val, err);
            return py::make_tuple(ok, err);
        });

    m.def("finalizeWorkingCopy",
        [](const std::string& orig, const std::string& base, const std::string& work) {
            std::vector<std::string> rejected;
            std::string err;
            bool ok = JsonCRUD::finalizeWorkingCopy(orig, base, work, rejected, err);
            return py::make_tuple(ok, rejected, err);
        });
}