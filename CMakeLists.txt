cmake_minimum_required(VERSION 3.15)
project(xaiepy)
set(CMAKE_CXX_STANDARD 17)

if(POLICY CMP0144)
  # respect all caps <PACKAGENAME>_ROOT environment variable to search for
  # package stuff
  cmake_policy(SET CMP0144 NEW)
endif()

if(POLICY CMP0148)
  cmake_policy(SET CMP0148 NEW)
endif()

option(OUTPUT_DIR "Output directory" ${CMAKE_CURRENT_BINARY_DIR})

include(third_party/aie-rt/fal/cmake/collect.cmake)
include(util/helpers.cmake)
set(BOOTGEN_SOURCE_DIR ${PROJECT_SOURCE_DIR}/third_party/bootgen)
include(util/bootgen.cmake)

configure_python_dev_packages()

set(AIERT_SRC_DIR ${PROJECT_SOURCE_DIR}/third_party/aie-rt/driver/src)
# gotta add the subdirectory so the copies to build/include/xaiengine occur...
add_subdirectory(${AIERT_SRC_DIR})

string(TOUPPER "${CMAKE_BUILD_TYPE}" uppercase_CMAKE_BUILD_TYPE)
if(uppercase_CMAKE_BUILD_TYPE STREQUAL "DEBUG")
  set(XAIE_DEBUG "XAIE_DEBUG")
endif()

target_compile_options(aienginev2 PRIVATE -Wall -Wextra -D__AIECDO__)
target_compile_definitions(aienginev2 PUBLIC ${XAIE_DEBUG})
get_target_property(AIERT_SRCS aienginev2 SOURCES)
list(TRANSFORM AIERT_SRCS PREPEND ${AIERT_SRC_DIR}/)
get_target_property(AIERT_INCLUDE_DIRECTORIES aienginev2 INCLUDE_DIRECTORIES)

add_library(xaie SHARED ${AIERT_SRCS})
target_compile_definitions(xaie PUBLIC ${XAIE_DEBUG} __AIECDO__)
target_include_directories(xaie PUBLIC ${AIERT_INCLUDE_DIRECTORIES})
target_include_directories(xaie PUBLIC SYSTEM ${PROJECT_SOURCE_DIR}/include)
set_target_properties(xaie PROPERTIES LINKER_LANGUAGE C
                                      POSITION_INDEPENDENT_CODE ON)
target_link_libraries(xaie PUBLIC cdo_driver)

set_target_properties(
  xaie
  PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})

option(BUILD_PYXRT "Build XRT" ON)
if(BUILD_PYXRT)
  set(XRT_SOURCE_DIR ${PROJECT_SOURCE_DIR}/third_party/XRT)
  include(util/pyxrt.cmake)
  set_target_properties(xclbinutil PROPERTIES MSVC_RUNTIME_LIBRARY
                                              MultiThreadedDLL)
  add_dependencies(xaie pyxrt xclbinutil)
endif()
