cmake_minimum_required(VERSION 2.8)

project(testproj C)

# include_directories ("${PROJECT_SOURCE_DIR}/lib")
# add_subdirectory(lib)

# add the executable
# add_executable (mainexe src/main.c src/dep.c)
# target_link_libraries (mainexe mylib)

# add_executable (st_mainexe src/st_main.cpp src/st_dep.cpp)

add_executable(omg src/mytester.c)

# add the executable
# set(THREADS_PREFER_PTHREAD_FLAG ON)
# find_package(Threads REQUIRED)
# add_executable (threadexe src/DriverPOS.c src/StartPOS.c)
# target_link_libraries(threadexe Threads::Threads)
# 
# add_executable (templexe src/template.cpp)
# add_executable (virtexe src/virtual.cpp)
# 
# add_executable (mytest src/mytest.c)
# 
# add_executable (newtest src/newtest.c)