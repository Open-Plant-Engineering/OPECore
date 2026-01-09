#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "Git/GitWrapper.hpp"

namespace py = pybind11;

PYBIND11_MODULE(py_GitWrapper, m) {
    m.doc() = "Python bindings for GitWrapper";

    py::class_<GitWrapper>(m, "GitWrapper")
        .def(py::init<const std::string&>())

        .def_static("cloneRepository",
            [](const std::string& url, const std::string& path) {
                std::string err;
                bool ok = GitWrapper::cloneRepository(url, path, err);
                return py::make_tuple(ok, err);
            },
            "Clone a repository")

        .def("gitPull",
            [](GitWrapper& self, const std::string& remote, const std::string& branch) {
                return self.gitPull(remote, branch);
            })

        .def("gitPush",
            [](GitWrapper& self, const std::string& remote, const std::string& branch) {
                return self.gitPush(remote, branch);
            })

        .def("gitMerge", &GitWrapper::gitMerge)
        .def("gitCreateBranch", &GitWrapper::gitCreateBranch)
        .def("gitRenameBranch", &GitWrapper::gitRenameBranch)
        .def("gitRebase", &GitWrapper::gitRebase)
        .def("gitStash", &GitWrapper::gitStash)
        .def("gitReset", &GitWrapper::gitReset)
        .def("gitDeleteBranch", &GitWrapper::gitDeleteBranch)
        .def("checkoutBranch", &GitWrapper::checkoutBranch)

        .def("getModifiedFiles", &GitWrapper::getModifiedFiles);
}