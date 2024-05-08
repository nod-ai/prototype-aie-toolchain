cmake_minimum_required(VERSION 3.15)
project(xaiepy)

include(collect)

find_package(OpenSSL REQUIRED)
if(OPENSSL_FOUND)
  message(STATUS "OpenSSL found")
  message(STATUS "OpenSSL include directories:" ${OPENSSL_INCLUDE_DIR})
else()
  message(FATAL_ERROR "OpenSSL Not found.")
endif()

set(BOOTGEN_SRC_DIR ${PROJECT_SOURCE_DIR}/third_party/bootgen)
# malloc.h is deprecated and should not be used
# https://stackoverflow.com/a/56463133 If you want to use malloc, then include
# stdlib.h
file(READ ${BOOTGEN_SRC_DIR}/cdo-npi.c FILE_CONTENTS)
string(REPLACE "#include <malloc.h>" "" FILE_CONTENTS "${FILE_CONTENTS}")
file(WRITE ${BOOTGEN_SRC_DIR}/cdo-npi.c "${FILE_CONTENTS}")

file(READ ${BOOTGEN_SRC_DIR}/cdo-alloc.c FILE_CONTENTS)
string(REPLACE "#include <malloc.h>" "" FILE_CONTENTS "${FILE_CONTENTS}")
file(WRITE ${BOOTGEN_SRC_DIR}/cdo-alloc.c "${FILE_CONTENTS}")

# since we explicitly link OpenSSL::applink
file(READ ${BOOTGEN_SRC_DIR}/main.cpp FILE_CONTENTS)
string(REPLACE "#include \"openssl/ms/applink.c\"" "" FILE_CONTENTS
               "${FILE_CONTENTS}")
file(WRITE ${BOOTGEN_SRC_DIR}/main.cpp "${FILE_CONTENTS}")

# objlib
file(GLOB BOOTGEN_SOURCE_SRCS ${BOOTGEN_SRC_DIR}/*.c*)
list(REMOVE_ITEM BOOTGEN_SOURCE_SRCS ${BOOTGEN_SRC_DIR}/main.cpp)
add_library(bootgen_objlib OBJECT ${BOOTGEN_SOURCE_SRCS})
set_property(TARGET bootgen_objlib PROPERTY POSITION_INDEPENDENT_CODE 1)
if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  target_compile_definitions(bootgen_objlib PRIVATE YY_NO_UNISTD_H)
endif()
target_include_directories(bootgen_objlib PRIVATE ${BOOTGEN_SRC_DIR}
                                                  ${OPENSSL_INCLUDE_DIR})
target_link_libraries(bootgen_objlib PUBLIC)

add_library(bootgen_shared SHARED $<TARGET_OBJECTS:bootgen_objlib>)
add_library(bootgen_static STATIC $<TARGET_OBJECTS:bootgen_objlib>)

add_executable(bootgen ${BOOTGEN_SRC_DIR}/main.cpp)
target_include_directories(
  bootgen PUBLIC ${BOOTGEN_SRC_DIR} ${OPENSSL_INCLUDE_DIR}
                 ${CMAKE_CURRENT_BINARY_DIR}/include)
target_compile_definitions(bootgen PRIVATE OPENSSL_USE_APPLINK)
target_link_libraries(bootgen PRIVATE bootgen_static OpenSSL::SSL
                                      OpenSSL::applink)

add_library(cdo_driver STATIC ${BOOTGEN_SRC_DIR}/cdo-driver/cdo_driver.c)
# because primarily this will be linked into libxaie.so... if not you get
# /usr/bin/ld: libcdo_driver.a(cdo_driver.c.o): warning: relocation against
# `hdr' in read-only section `.text' /usr/bin/ld:
# libcdo_driver.a(cdo_driver.c.o): relocation R_X86_64_PC32 against symbol
# `LEfwrite' can not be used when making a shared object; recompile with -fPIC
set_property(TARGET cdo_driver PROPERTY POSITION_INDEPENDENT_CODE 1)

target_include_directories(
  cdo_driver PUBLIC $<BUILD_INTERFACE:${BOOTGEN_SRC_DIR}/cdo-driver>
                    $<INSTALL_INTERFACE:include/cdo_driver>)
if(NOT CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  target_compile_options(cdo_driver PRIVATE -Wno-cast-qual -Wno-sign-compare)
endif()

set(AIERT_SRC_DIR ${PROJECT_SOURCE_DIR}/third_party/aie-rt/driver/src)
# gotta add the subdirectory so the copies to build/include/xaiengine occur...
add_subdirectory(${AIERT_SRC_DIR})

target_compile_options(aienginev2 PRIVATE -Wall -Wextra -D__AIECDO__)
get_target_property(AIERT_SRCS aienginev2 SOURCES)
list(TRANSFORM AIERT_SRCS PREPEND ${AIERT_SRC_DIR}/)
get_target_property(AIERT_INCLUDE_DIRECTORIES aienginev2 INCLUDE_DIRECTORIES)

add_library(xaie SHARED ${AIERT_SRCS})
set_target_properties(xaie PROPERTIES LINKER_LANGUAGE C)
target_compile_options(xaie PRIVATE -D__AIECDO__)
target_link_libraries(xaie cdo_driver)
target_include_directories(xaie PUBLIC ${AIERT_INCLUDE_DIRECTORIES})
target_include_directories(xaie PUBLIC SYSTEM ${BOOTGEN_SRC_DIR})
