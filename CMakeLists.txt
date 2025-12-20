cmake_minimum_required(VERSION 3.10)
project(OpeCore)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find libgit2 (installed once, reused forever)
find_package(libgit2 REQUIRED)
# Find SOCI (core + backends already built/installed)
find_package(SOCI REQUIRED)  # From SOCIConfig.cmake installed by SOCI itself

# Optionally, if you want to be explicit about include dirs and libs:
# message(STATUS "SOCI include dirs: ${SOCI_INCLUDE_DIRS}")
# message(STATUS "SOCI libraries: ${SOCI_LIBRARIES}")

include_directories(${LIBGIT2_INCLUDE_DIRS})
link_directories(${LIBGIT2_LIBRARY_DIRS})
include_directories(${SOCI_INCLUDE_DIRS})
link_directories(${SOCI_LIBRARIES})

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
    src/Git/GitWrapper.cpp
    src/Database/Database.cpp
)

# Link SQLite to your app
target_link_libraries(OpeCore 
                        PRIVATE 
                            sqlite3
                            git2
                            mysqlclient
                            soci_core
                            soci_sqlite3
                            soci_mysql
                            pthread 
                            dl
                        )
target_include_directories(OpeCore 
                            PRIVATE 
                                external/sqlite-amalgamation-3500400
                            PUBLIC 
                                include
                                /usr/include/mysql
                            )

# On some systems you may also need (if SOCI wasn't built to link them transitively):
# find_package(SQLite3 REQUIRED)
# find_package(MySQLClient REQUIRED)  # or `mysqlclient` via find_library
# target_link_libraries(soci_crud PRIVATE SQLite::SQLite3 mysqlclient)
# target_link_libraries(OpeCore PRIVATE SOCI::sqlite3 SOCI::mysql)


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
