cmake_minimum_required(VERSION 3.15)
project(OPE_core_engine)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Python COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_package(libgit2 CONFIG REQUIRED)

add_library(OPE_core_engine STATIC
    src/engine.cpp
    src/Git/GitWrapper.cpp
    src/JSON/JsonCRUD.cpp
    src/Session/SessionManager.cpp
)

pybind11_add_module(OPE_core_engine_py bindings/py_engine.cpp)
pybind11_add_module(py_GitWrapper bindings/py_GitWrapper.cpp)
pybind11_add_module(py_JsonCRUD bindings/py_JsonCRUD.cpp)
pybind11_add_module(py_SessionManager bindings/py_SessionManager.cpp)

target_include_directories(OPE_core_engine PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_include_directories(py_GitWrapper PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_include_directories(py_JsonCRUD PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_include_directories(py_SessionManager PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(OPE_core_engine PRIVATE
    pybind11::pybind11
    nlohmann_json::nlohmann_json
    libgit2::libgit2package
)

target_link_libraries(OPE_core_engine_py PRIVATE
    OPE_core_engine
)

target_link_libraries(py_GitWrapper PRIVATE
    OPE_core_engine
)

target_link_libraries(py_JsonCRUD PRIVATE
    OPE_core_engine
)

target_link_libraries(py_SessionManager PRIVATE
    OPE_core_engine
)