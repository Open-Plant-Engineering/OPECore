# Create test executable
add_executable(OpeCore_test test_main.cpp)

# Link against your library
target_link_libraries(OpeCore_test PRIVATE sqlite_app)

# Register with CTest
add_test(NAME OpeCoreTestApp COMMAND OpeCore_test)