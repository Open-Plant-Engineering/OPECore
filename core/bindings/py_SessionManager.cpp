#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "Session/SessionManager.hpp"

namespace py = pybind11;

PYBIND11_MODULE(py_SessionManager, m) {
    m.doc() = "Python bindings for SessionManager";

    py::class_<SessionManager>(m, "SessionManager")
        .def(py::init<const std::string&>())

        .def_static("cloneProject",
            [](const std::string& url, const std::string& path) {
                std::string err;
                bool ok = SessionManager::cloneProject(url, path, err);
                return py::make_tuple(ok, err);
            })

        .def("getRepoPath", &SessionManager::getRepoPath)

        .def("createJsonWithUniqueId",
            [](SessionManager& self,
               const std::string& dir,
               const std::string& initialJson,
               std::string& errorOut) {
                std::string err;
                std::string rel = self.createJsonWithUniqueId(dir, initialJson, err);
                errorOut = err;
                return rel;
            },
            py::arg("relativeDir"),
            py::arg("initialJsonText"),
            py::arg("errorMessage"))

        .def("modifyAttribute",
            [](SessionManager& self,
               const std::string& relPath,
               const std::string& key,
               const std::string& valueJson) {
                std::string err;
                bool ok = self.modifyAttribute(relPath, key, valueJson, err);
                return py::make_tuple(ok, err);
            })

        .def("finalizeSession",
            [](SessionManager& self, const std::string& relPath) {
                std::vector<std::string> rejected;
                std::string err;
                bool ok = self.finalizeSession(relPath, rejected, err);
                return py::make_tuple(ok, rejected, err);
            });
}