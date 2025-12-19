mkdir build && cd build
cmake .. -C ../CMakeLists.linux.txt -DCMAKE_INSTALL_PREFIX=..
make
cmake --install .