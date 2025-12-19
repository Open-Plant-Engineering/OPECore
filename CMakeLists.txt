cmake_minimum_required(VERSION 3.10)
project(OpeCore)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(
    include
    external/sqlite-amalgamation-3500400
    external
)

# Add SQLite amalgamation
add_library(sqlite3 STATIC external/sqlite-amalgamation-3500400/sqlite3.c)

# Add your application executable
# add_library(OpeCore
#     src/main.cpp
#     src/app.cpp
# )

# Add executable
add_executable(OpeCore
    src/main.cpp
    src/OpeDbCore.cpp
    src/OpeSessionManager.cpp
)

# Link SQLite to your app
target_link_libraries(OpeCore PRIVATE sqlite3)
target_include_directories(OpeCore PUBLIC include)

# Folders for testing
# enable_testing()
# add_subdirectory(test)
