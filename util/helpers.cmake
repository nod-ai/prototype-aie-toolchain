# https://stackoverflow.com/a/34292622/9045206 Get all propreties that cmake
# supports
if(NOT CMAKE_PROPERTY_LIST)
  execute_process(COMMAND ${CMAKE_COMMAND} --help-property-list
                  OUTPUT_VARIABLE CMAKE_PROPERTY_LIST)

  # Convert command output into a CMake list
  list(APPEND CMAKE_PROPERTY_LIST LIBRARY_OUTPUT_DIRECTORY
       ARCHIVE_OUTPUT_DIRECTORY RUNTIME_OUTPUT_DIRECTORY)
  string(REGEX REPLACE ";" "\\\\;" CMAKE_PROPERTY_LIST "${CMAKE_PROPERTY_LIST}")
  string(REGEX REPLACE "\n" ";" CMAKE_PROPERTY_LIST "${CMAKE_PROPERTY_LIST}")
  list(REMOVE_DUPLICATES CMAKE_PROPERTY_LIST)
endif()

function(print_properties)
  message("CMAKE_PROPERTY_LIST = ${CMAKE_PROPERTY_LIST}")
endfunction()

function(print_target_properties target)
  if(NOT TARGET ${target})
    message(STATUS "There is no target named '${target}'")
    return()
  endif()

  foreach(property ${CMAKE_PROPERTY_LIST})
    string(REPLACE "<CONFIG>" "${CMAKE_BUILD_TYPE}" property ${property})

    if(property STREQUAL "LOCATION"
       OR property MATCHES "^LOCATION_"
       OR property MATCHES "_LOCATION$")
      continue()
    endif()

    get_property(
      was_set
      TARGET ${target}
      PROPERTY ${property}
      SET)
    if(was_set)
      get_target_property(value ${target} ${property})
      message("${target} ${property} = ${value}")
    endif()
  endforeach()
endfunction()

macro(configure_python_dev_packages)
  # apparently alma 8 doesn't have the full development lib???
  set(_python_development_component Development.Module)

  find_package(
    Python3 ${PY_VERSION}
    COMPONENTS Interpreter ${_python_development_component}
    REQUIRED)
  unset(_python_development_component)
  message(STATUS "Found python include dirs: ${Python3_INCLUDE_DIRS}")
  message(STATUS "Found python libraries: ${Python3_LIBRARIES}")
  detect_pybind11_install()
  find_package(pybind11 CONFIG REQUIRED)
  message(STATUS "Found pybind11 v${pybind11_VERSION}: ${pybind11_INCLUDE_DIR}")
  message(STATUS "Python prefix = '${PYTHON_MODULE_PREFIX}', "
                 "suffix = '${PYTHON_MODULE_SUFFIX}', "
                 "extension = '${PYTHON_MODULE_EXTENSION}")
endmacro()

# Detects a pybind11 package installed in the current python environment and
# sets variables to allow it to be found. This allows pybind11 to be installed
# via pip, which typically yields a much more recent version than the OS
# install, which will be available otherwise.
function(detect_pybind11_install)
  if(pybind11_DIR)
    message(
      STATUS
        "Using explicit pybind11 cmake directory: ${pybind11_DIR} (-Dpybind11_DIR to change)"
    )
  else()
    message(STATUS "Checking for pybind11 in python path...")
    execute_process(
      COMMAND "${Python3_EXECUTABLE}" -c
              "import pybind11;print(pybind11.get_cmake_dir(), end='')"
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      RESULT_VARIABLE STATUS
      OUTPUT_VARIABLE PACKAGE_DIR
      ERROR_QUIET)
    if(NOT STATUS EQUAL "0")
      message(
        STATUS
          "not found (install via 'pip install pybind11' or set pybind11_DIR)")
      return()
    endif()
    message(STATUS "found (${PACKAGE_DIR})")
    set(pybind11_DIR
        "${PACKAGE_DIR}"
        PARENT_SCOPE)
  endif()
endfunction()
