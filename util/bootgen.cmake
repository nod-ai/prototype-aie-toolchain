file(GLOB BOOTGEN_SOURCES "${BOOTGEN_SOURCE_DIR}/*.c"
     "${BOOTGEN_SOURCE_DIR}/*.cpp")

# malloc.h is deprecated and should not be used
# https://stackoverflow.com/a/56463133 If you want to use malloc, then include
# stdlib.h
file(READ ${BOOTGEN_SOURCE_DIR}/cdo-npi.c FILE_CONTENTS)
string(REPLACE "#include <malloc.h>" "" FILE_CONTENTS "${FILE_CONTENTS}")
file(WRITE ${BOOTGEN_SOURCE_DIR}/cdo-npi.c "${FILE_CONTENTS}")

file(READ ${BOOTGEN_SOURCE_DIR}/cdo-alloc.c FILE_CONTENTS)
string(REPLACE "#include <malloc.h>" "" FILE_CONTENTS "${FILE_CONTENTS}")
file(WRITE ${BOOTGEN_SOURCE_DIR}/cdo-alloc.c "${FILE_CONTENTS}")

find_package(OpenSSL REQUIRED)
if(OPENSSL_FOUND)
  message(STATUS "OpenSSL found")
  message(STATUS "OpenSSL include directories:" ${OPENSSL_INCLUDE_DIR})
else()
  message(FATAL_ERROR "OpenSSL Not found.")
endif()

# since we explicitly link OpenSSL::applink
file(READ ${BOOTGEN_SOURCE_DIR}/main.cpp FILE_CONTENTS)
string(REPLACE "#include \"openssl/ms/applink.c\"" "" FILE_CONTENTS
               "${FILE_CONTENTS}")
file(WRITE ${BOOTGEN_SOURCE_DIR}/main.cpp "${FILE_CONTENTS}")

add_library(bootgen-lib STATIC ${BOOTGEN_SOURCES})
if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
  target_compile_definitions(bootgen-lib PRIVATE YY_NO_UNISTD_H)
endif()
target_include_directories(bootgen-lib PRIVATE ${BOOTGEN_SOURCE_DIR}
                                               ${OPENSSL_INCLUDE_DIR})

add_executable(bootgen ${BOOTGEN_SOURCE_DIR}/main.cpp)
target_include_directories(
  bootgen PUBLIC ${BOOTGEN_SOURCE_DIR} ${OPENSSL_INCLUDE_DIR}
                 ${CMAKE_CURRENT_BINARY_DIR}/include)
target_compile_definitions(bootgen PRIVATE OPENSSL_USE_APPLINK)
target_link_libraries(bootgen PRIVATE bootgen-lib OpenSSL::SSL OpenSSL::applink)

file(READ ${BOOTGEN_SOURCE_DIR}/cdo-driver/cdo_driver.h FILE_CONTENTS)
string(REPLACE "void SectionHeader();" "" FILE_CONTENTS "${FILE_CONTENTS}")
file(WRITE ${BOOTGEN_SOURCE_DIR}/cdo-driver/cdo_driver.h "${FILE_CONTENTS}")
add_library(cdo_driver STATIC ${BOOTGEN_SOURCE_DIR}/cdo-driver/cdo_driver.c)
target_include_directories(cdo_driver PUBLIC ${BOOTGEN_SOURCE_DIR}/cdo-driver)
