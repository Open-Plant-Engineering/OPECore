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
    src/JSON/JsonCRUD.cpp
)

# Link SQLite to your app
target_link_libraries(OpeCore PRIVATE sqlite3)
target_include_directories(OpeCore PRIVATE external/sqlite-amalgamation-3500400)
target_include_directories(OpeCore PUBLIC include)

# -----------------------------
# Installation rules
# -----------------------------

# Install the executable
install(TARGETS OpeCore
    RUNTIME DESTINATION bin
)

# Install your public headers (from include/)
install(DIRECTORY include/ DESTINATION include)

# Folders for testing
# enable_testing()
# add_subdirectory(test)
