cmake_minimum_required(VERSION 2.8)

project(testproj)

include_directories ("${PROJECT_SOURCE_DIR}/lib")
add_subdirectory(lib)

# add the executable
add_executable (mainexe src/main.cpp src/dep.cpp)
target_link_libraries (mainexe libmylib)

# add the executable
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
add_executable (threadexe src/DriverPOS.c src/StartPOS.c)
target_link_libraries(threadexe Threads::Threads)