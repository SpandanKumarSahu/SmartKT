cmake_minimum_required(VERSION 2.8)

project(smallproj)

include_directories ("${PROJECT_SOURCE_DIR}/lib")
add_subdirectory(lib)

# add the executable
add_executable (prog src/prog.cpp)
target_link_libraries (prog lib)

# add the executable
add_executable(dp src/builder_pattern_1.cpp)
target_link_libraries (dp lib)
