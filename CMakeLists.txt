cmake_minimum_required(VERSION 3.1)
project(DRServer CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(THREADS_PREFER_PTHREAD_FLAG ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_HOME_DIRECTORY}/bin)
set(CMAKE_MODULE_PATH ${CMAKE_HOME_DIRECTORY})

find_package(Threads REQUIRED)
find_package(Boost 1.67 REQUIRED COMPONENTS thread regex system iostreams)
find_package(ZLIB REQUIRED)
find_package(cppzmq REQUIRED)
find_package(Config++ REQUIRED)

add_executable(gateway
  src/gateway/gateway.cpp
  src/gateway/session.cpp
)
target_include_directories(gateway PRIVATE
  ${Boost_INCLUDE_DIRS}
  ${ZLIB_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/protocol
  ${CMAKE_CURRENT_SOURCE_DIR}/src/gateway
)
target_link_libraries(gateway
  ${Boost_LIBRARIES}
  ${ZLIB_LIBRARIES}
  Threads::Threads
  cppzmq
  ${CONFIG++_LIBRARY}
)

add_executable(broker
  src/broker/broker.cpp
)
target_include_directories(broker PRIVATE
  ${Boost_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/broker
  ${CMAKE_CURRENT_SOURCE_DIR}/src/protocol
)
target_link_libraries(broker
  ${Boost_LIBRARIES}
  Threads::Threads
  cppzmq
  ${CONFIG++_LIBRARY}
)

add_executable(example
  src/example/example.cpp
)
target_include_directories(example PRIVATE
  ${Boost_INCLUDE_DIRS}
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/example
  ${CMAKE_CURRENT_SOURCE_DIR}/src/protocol
)
target_link_libraries(example
  ${Boost_LIBRARIES}
  Threads::Threads
  cppzmq
  ${CONFIG++_LIBRARY}
)
