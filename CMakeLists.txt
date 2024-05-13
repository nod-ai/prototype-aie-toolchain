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

include(util/helpers.cmake)

configure_python_dev_packages()
find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)
find_package(Boost REQUIRED COMPONENTS system program_options filesystem)
find_package(RapidJSON REQUIRED)

# ##############################################################################
# bootgen
# ##############################################################################

set(BOOTGEN_SOURCE_DIR ${PROJECT_SOURCE_DIR}/third_party/bootgen)
file(GLOB BOOTGEN_SOURCES "${BOOTGEN_SOURCE_DIR}/*.c"
     "${BOOTGEN_SOURCE_DIR}/*.cpp")

add_library(bootgen-lib STATIC ${BOOTGEN_SOURCES})
if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  target_compile_definitions(bootgen-lib PRIVATE YY_NO_UNISTD_H)
endif()
set_target_properties(bootgen-lib PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_include_directories(bootgen-lib PRIVATE ${BOOTGEN_SOURCE_DIR}
                                               ${OPENSSL_INCLUDE_DIR})
target_compile_definitions(bootgen-lib PRIVATE OPENSSL_USE_APPLINK)
target_link_libraries(bootgen-lib PRIVATE OpenSSL::SSL OpenSSL::applink)

add_library(cdo_driver STATIC ${BOOTGEN_SOURCE_DIR}/cdo-driver/cdo_driver.c)
target_include_directories(cdo_driver PUBLIC ${BOOTGEN_SOURCE_DIR}/cdo-driver)
set_target_properties(cdo_driver PROPERTIES LINKER_LANGUAGE C
                                            POSITION_INDEPENDENT_CODE ON)

pybind11_add_module(_bootgen xaiepy/bootgen.cpp)
target_include_directories(_bootgen PRIVATE ${BOOTGEN_SOURCE_DIR})
target_link_libraries(_bootgen PRIVATE bootgen-lib)
set_target_properties(_bootgen PROPERTIES POSITION_INDEPENDENT_CODE ON)
set_target_properties(
  _bootgen
  PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})

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

# shared not static because static will let linker trim SectionMemTopology initializers...
add_library(xclbinutil-lib SHARED ${XCLBINUTIL_SRCS})
set_target_properties(xclbinutil-lib PROPERTIES POSITION_INDEPENDENT_CODE ON)

if(NOT WIN32)
  target_link_libraries(xclbinutil-lib PRIVATE crypto)
  target_compile_definitions(xclbinutil-lib
                             PRIVATE ENABLE_JSON_SCHEMA_VALIDATION)
  target_link_libraries(xclbinutil-lib PRIVATE transformcdo)
endif()

set(THREADS_PREFER_PTHREAD_FLAG ON)
target_link_libraries(xclbinutil-lib PUBLIC ${Boost_LIBRARIES} Threads::Threads)
target_include_directories(xclbinutil-lib PUBLIC ${XRT_BINARY_DIR}/gen)
set_target_properties(
  xclbinutil-lib
  PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})

pybind11_add_module(_xclbinutil xaiepy/xclbinutil.cpp)
target_include_directories(_xclbinutil PRIVATE ${XCLBINUTIL_SOURCE_DIR})
target_link_libraries(_xclbinutil PUBLIC xclbinutil-lib ${Boost_LIBRARIES})
set_target_properties(_xclbinutil PROPERTIES POSITION_INDEPENDENT_CODE ON)
set_target_properties(
  _xclbinutil
  PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})

add_dependencies(xaie _xclbinutil)

# ##############################################################################
# pyxrt
# ##############################################################################

set_target_properties(
  pyxrt
  PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR}
    ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR}
    RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR}
    # pyxrt and xrt in general do a ridiculous dance with drivers
    # https://github.com/Xilinx/XRT/blob/edcae12640ce96ec597c4c0cc1b2a850cfcc5c8b/src/runtime_src/core/common/module_loader.cpp#L201-L205
    SKIP_BUILD_RPATH ON
    BUILD_WITH_INSTALL_RPATH ON)

add_dependencies(xaie pyxrt)
