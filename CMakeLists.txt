cmake_minimum_required(VERSION 3.1)
project(DRServer CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(THREADS_PREFER_PTHREAD_FLAG ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_HOME_DIRECTORY}/bin)

find_package(Threads REQUIRED)
find_package(Boost 1.67 REQUIRED COMPONENTS thread regex system program_options iostreams)
find_package(ZLIB REQUIRED)
find_package(cppzmq REQUIRED)

add_executable(gameserver
  src/gameserver.cpp
  src/gateway/gateway.cpp
  src/broker/broker.cpp
)
target_include_directories(gameserver PRIVATE
  ${Boost_INCLUDE_DIRS}
  ${ZLIB_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/broker
  ${CMAKE_CURRENT_SOURCE_DIR}/src/protocol
  ${CMAKE_CURRENT_SOURCE_DIR}/src/gateway
)
target_link_libraries(gameserver
  ${Boost_LIBRARIES}
  ${ZLIB_LIBRARIES}
  Threads::Threads
  cppzmq
)
