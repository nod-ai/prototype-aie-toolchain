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

if(WIN32)
  # see util/remove_path_limit.ps1
  set(CMAKE_OBJECT_PATH_MAX 4096)
endif()

set(OUTPUT_DIR
    ${CMAKE_CURRENT_BINARY_DIR}
    CACHE STRING "Output directory")

# ##############################################################################
# requirements
# ##############################################################################

if(NOT ${CMAKE_SIZEOF_VOID_P} EQUAL 8)
  # if you open up the wrong developer shell in windows...
  message(
    FATAL_ERROR
      "Something has gone terribly wrong: CMAKE_SIZEOF_VOID_P=${CMAKE_SIZEOF_VOID_P}"
  )
endif()
# can delete after this is all worked out
# https://gitlab.kitware.com/cmake/cmake/-/issues/25702
find_package(OpenSSL)
if(NOT DEFINED OPENSSL_FOUND OR NOT ${OPENSSL_FOUND})
  list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/util")
  find_package(OpenSSL)
  if(NOT DEFINED USE_OUR_FIND_OPENSSL OR NOT ${USE_OUR_FIND_OPENSSL})
    message(FATAL_ERROR "Didn't pickup our FindOpenSSL.cmake")
  endif()
  if(NOT DEFINED OPENSSL_FOUND OR NOT ${OPENSSL_FOUND})
    message(FATAL_ERROR "OpenSSL not found")
  endif()
endif()
message(STATUS "OpenSSL include directories:" ${OPENSSL_INCLUDE_DIR})

include(util/helpers.cmake)
configure_python_dev_packages()

find_package(Threads REQUIRED)
find_package(Boost REQUIRED COMPONENTS system program_options filesystem)
message(STATUS "Boost include directories:" ${Boost_INCLUDE_DIRS})

if(NOT WIN32)
  find_package(RapidJSON REQUIRED)
endif()

# ##############################################################################
# bootgen
# ##############################################################################

set(BOOTGEN_SOURCE_DIR ${PROJECT_SOURCE_DIR}/third_party/bootgen)
file(GLOB BOOTGEN_SOURCES "${BOOTGEN_SOURCE_DIR}/*.c"
     "${BOOTGEN_SOURCE_DIR}/*.cpp")
list(REMOVE_ITEM BOOTGEN_SOURCES "${BOOTGEN_SOURCE_DIR}/main.cpp")

add_library(bootgen-lib STATIC ${BOOTGEN_SOURCES})
if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  target_compile_definitions(bootgen-lib PUBLIC YY_NO_UNISTD_H)
endif()
target_include_directories(bootgen-lib PUBLIC ${BOOTGEN_SOURCE_DIR}
                                              ${OPENSSL_INCLUDE_DIR})
target_compile_definitions(bootgen-lib PUBLIC OPENSSL_USE_APPLINK)
target_link_libraries(bootgen-lib PUBLIC OpenSSL::SSL OpenSSL::applink)

add_library(cdo_driver STATIC ${BOOTGEN_SOURCE_DIR}/cdo-driver/cdo_driver.c)
target_include_directories(cdo_driver PUBLIC ${BOOTGEN_SOURCE_DIR}/cdo-driver)
set_target_properties(cdo_driver PROPERTIES LINKER_LANGUAGE C)

pybind11_add_module(_bootgen xaiepy/bootgen.cpp)
target_include_directories(_bootgen PUBLIC ${BOOTGEN_SOURCE_DIR})
target_link_libraries(_bootgen PUBLIC bootgen-lib)

# ##############################################################################
# aie-rt
# ##############################################################################

include(third_party/aie-rt/fal/cmake/collect.cmake)
set(AIERT_SRC_DIR ${PROJECT_SOURCE_DIR}/third_party/aie-rt/driver/src)
# gotta add the subdirectory so the copies to build/include/xaiengine occur...
add_subdirectory(${AIERT_SRC_DIR})

string(TOUPPER "${CMAKE_BUILD_TYPE}" uppercase_CMAKE_BUILD_TYPE)
if(uppercase_CMAKE_BUILD_TYPE STREQUAL "DEBUG")
  set(XAIE_DEBUG "XAIE_DEBUG")
endif()

target_compile_definitions(aienginev2 PUBLIC ${XAIE_DEBUG})
get_target_property(AIERT_SRCS aienginev2 SOURCES)
list(TRANSFORM AIERT_SRCS PREPEND ${AIERT_SRC_DIR}/)
# elf.h
target_include_directories(aienginev2 PUBLIC SYSTEM ${BOOTGEN_SOURCE_DIR})
get_target_property(AIERT_INCLUDE_DIRECTORIES aienginev2 INCLUDE_DIRECTORIES)

add_library(xaie SHARED ${AIERT_SRCS})
target_compile_definitions(xaie PUBLIC ${XAIE_DEBUG} __AIECDO__)
target_include_directories(xaie PUBLIC ${AIERT_INCLUDE_DIRECTORIES})
set_target_properties(xaie PROPERTIES LINKER_LANGUAGE C)
target_link_libraries(xaie PUBLIC cdo_driver)

add_dependencies(xaie _bootgen)

# ##############################################################################
# xclbinutil
# ##############################################################################

set(XRT_SOURCE_DIR ${PROJECT_SOURCE_DIR}/third_party/XRT)
add_subdirectory(${XRT_SOURCE_DIR}/src)
include_directories(${XRT_SOURCE_DIR}/src/runtime_src/core/include)

set(XCLBINUTIL_SOURCE_DIR
    ${PROJECT_SOURCE_DIR}/third_party/XRT/src/runtime_src/tools/xclbinutil)

configure_file(${XRT_SOURCE_DIR}/src/CMake/config/version.h.in
               ${XRT_BINARY_DIR}/src/gen/version.h)

file(
  GLOB
  XCLBINUTIL_SRCS
  "${XCLBINUTIL_SOURCE_DIR}/DTC*.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/FDT*.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/CBOR.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/RapidJsonUtilities.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/KernelUtilities.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/ElfUtilities.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/FormattedOutput.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/ParameterSectionData.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/Section.cxx" # Note: Due to linking dependency
  # issue, this entry needs to be before the other sections
  "${XCLBINUTIL_SOURCE_DIR}/Section*.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/Resources*.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/XclBinClass.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/XclBinSignature.cxx"
  "${XCLBINUTIL_SOURCE_DIR}/XclBinUtilities.cxx")

# shared not static because static will let linker trim SectionMemTopology
# initializers...
add_library(xclbinutil-lib SHARED ${XCLBINUTIL_SRCS})

if(NOT WIN32)
  target_link_libraries(xclbinutil-lib PUBLIC crypto)
  target_compile_definitions(xclbinutil-lib
                             PUBLIC ENABLE_JSON_SCHEMA_VALIDATION)
  target_link_libraries(xclbinutil-lib PUBLIC transformcdo)
else()
  target_compile_options(xclbinutil-lib PUBLIC "/EHsc")
  # if you get LINK : fatal error LNK1104: cannot open file
  # 'libboost_filesystem-vc142-mt-gd-x64-1_74.lib'
  # target_compile_definitions(xclbinutil-lib PUBLIC BOOST_ALL_DYN_LINK)
endif()

set(THREADS_PREFER_PTHREAD_FLAG ON)
target_link_libraries(xclbinutil-lib PUBLIC ${Boost_LIBRARIES} Threads::Threads)
target_include_directories(xclbinutil-lib PUBLIC ${XRT_BINARY_DIR}/gen
                                                 ${Boost_INCLUDE_DIRS})

pybind11_add_module(_xclbinutil xaiepy/xclbinutil.cpp)
target_include_directories(_xclbinutil PUBLIC ${XCLBINUTIL_SOURCE_DIR})
target_link_libraries(_xclbinutil PUBLIC xclbinutil-lib)

add_dependencies(xaie _xclbinutil)

# ##############################################################################
# pyxrt
# ##############################################################################

set_target_properties(
  pyxrt
  PROPERTIES
    # pyxrt and xrt in general do a ridiculous dance with drivers
    # https://github.com/Xilinx/XRT/blob/edcae12640ce96ec597c4c0cc1b2a850cfcc5c8b/src/runtime_src/core/common/module_loader.cpp#L201-L205
    SKIP_BUILD_RPATH ON
    BUILD_WITH_INSTALL_RPATH ON)

add_dependencies(xaie pyxrt)

# ##############################################################################
# finish
# ##############################################################################

set_target_properties(_bootgen _xclbinutil bootgen-lib cdo_driver xaie
                      xclbinutil-lib PROPERTIES POSITION_INDEPENDENT_CODE ON)

set_target_properties(
  _bootgen _xclbinutil pyxrt xaie xclbinutil-lib
  PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})
