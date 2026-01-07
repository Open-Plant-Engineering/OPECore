cmake_minimum_required(VERSION 3.15)
project(OPE_ui)

find_package(Qt6 COMPONENTS Widgets REQUIRED)

add_executable(OPE_ui src/main.cpp)
target_link_libraries(OPE_ui Qt6::Widgets)