find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

# pyxrt and xrt in general do a ridiculous dance with drivers
# https://github.com/Xilinx/XRT/blob/edcae12640ce96ec597c4c0cc1b2a850cfcc5c8b/src/runtime_src/core/common/module_loader.cpp#L201-L205
set(CMAKE_SKIP_BUILD_RPATH ON)
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)

if(WIN32)
  file(READ ${XRT_SOURCE_DIR}/src/runtime_src/core/common/memalign.h
       FILE_CONTENTS)
  string(
    REPLACE
      "defined(_WINDOWS)"
      "defined(_WINDOWS) || defined(_WIN32) || defined(WIN32) || defined(__CYGWIN__) || defined(__MINGW32__)"
      FILE_CONTENTS
      "${FILE_CONTENTS}")
  file(WRITE ${XRT_SOURCE_DIR}/src/runtime_src/core/common/memalign.h
       "${FILE_CONTENTS}")
endif()
add_subdirectory(${XRT_SOURCE_DIR}/src)
set_target_properties(
  pyxrt xclbinutil
  PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             ARCHIVE_OUTPUT_DIRECTORY ${OUTPUT_DIR}
             RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_DIR})
