cmake_minimum_required(VERSION 3.15)
project(xaiepy)

include(collect)

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
set_target_properties(xaie PROPERTIES LINKER_LANGUAGE C)
target_compile_definitions(xaie PUBLIC ${XAIE_DEBUG} __AIECDO__)
target_include_directories(xaie PUBLIC ${AIERT_INCLUDE_DIRECTORIES})
target_include_directories(xaie PUBLIC SYSTEM ${PROJECT_SOURCE_DIR}/include)
if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
  target_link_options(
    xaie
    PUBLIC
    -Wl,-U,_cdo_BlockSet32
    -Wl,-U,_cdo_BlockWrite32
    -Wl,-U,_cdo_MaskPoll
    -Wl,-U,_cdo_MaskWrite32
    -Wl,-U,_cdo_Write32)
endif()
