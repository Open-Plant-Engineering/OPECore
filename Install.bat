mkdir build
cd build
cmake .. -C ../CMakeLists.windows.txt -DCMAKE_INSTALL_PREFIX=..
cmake --build . --config Release
cmake --install . --config Release