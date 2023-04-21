cmake_minimum_required(VERSION 3.8)
# project(Wrapping)


# if (CMAKE_ROLE)
#   message (STATUS ">>>>>>>>>>>>> CMAKE_ROLE >>>>>${CMAKE_ROLE}<<<<<")
# else()
#   message (STATUS ">>>>>>>>>>>>> CMAKE_ROLE not set")
# endif()

find_package(Python COMPONENTS Interpreter Development.Module)
# add_executable(void void.cxx)
message(STATUS "COMMAND ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/cmake/sp_dir.py")
execute_process(COMMAND ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/cmake/sp_dir.py
  OUTPUT_VARIABLE SP_DIR)
  message(STATUS "SP_DIR ${SP_DIR}")
# remove trailing newline  
string(REGEX REPLACE "\n$" "" PYTHON_DEST ${SP_DIR})
if(MSVC)
  # set (python_destination ${PYTHON_DEST}/..)
  cmake_path(GET PYTHON_DEST PARENT_PATH python_destination)
endif()
# message(FATAL_ERROR "python_destination ${python_destination}")


# target_link_libraries(void
#   PRIVATE
#     Python3::Python)



include(GNUInstallDirs)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")

# We just need the CommonCore and Python modules here.
# these must be found earlier in the parent directory
find_package(VTK COMPONENTS CommonCore Python)
if (NOT VTK_FOUND)
  message("Skipping example: ${VTK_NOT_FOUND_MESSAGE}")
  return ()
endif ()

set(_shared_default ON)
get_target_property(_vtk_libtype VTK::CommonCore TYPE)
if (_vtk_libtype STREQUAL "STATIC_LIBRARY")
  set(_shared_default OFF)
endif ()

option(BUILD_SHARED_LIBS "Build shared or static libraries" "${_shared_default}")
include(CTest)

message (STATUS "CURRENT CMAKE_INSTALL_BINDIR ${CMAKE_INSTALL_BINDIR}")

include(GNUInstallDirs)

message (STATUS "CURRENT CMAKE_INSTALL_BINDIR ${CMAKE_INSTALL_BINDIR}")

# First we scan the modules in our project to find out the dependency graph
# between them.
vtk_module_scan(
  # With only 1 module file, this is easier. With more,
  # `vtk_module_find_modules` would be preferred.
  MODULE_FILES      "${CMAKE_CURRENT_SOURCE_DIR}/module/vtk.module"
  # Not building the only module we have is silly.
  REQUEST_MODULES   Wrapping::Wrappable
  # Store the list of provided modules from this scan.
  PROVIDES_MODULES  modules
  # Enable the tests for our modules.
  ENABLE_TESTS      ON)



message(STATUS "Python destination ${python_destination}")
if (MSVC) 
  set (CMAKE_INSTALL_BINDIR "")
endif()
vtk_module_python_default_destination(python_destination)
message(STATUS "Python destination ${python_destination}")
cmake_path(GET python_destination RELATIVE_PART python_destination_rel)
message(STATUS "Relative Python destination ${python_destination_rel}")
set(python_destination ${python_destination_rel})
message(STATUS "Python destination ${python_destination}")

# Build the module we just scanned.
vtk_module_build(MODULES ${modules})

# Wrap it with Python.
vtk_module_wrap_python(
  MODULES         ${modules}
  TARGET          Wrapping::WrappablePython
  WRAPPED_MODULES wrapping_modules
  INSTALL_EXPORT  wrapping_export
  PYTHON_PACKAGE  "wrapping"
  MODULE_DESTINATION  "${python_destination}"
  CMAKE_DESTINATION   "${CMAKE_INSTALL_LIBDIR}/cmake/WrappingPython"
  LIBRARY_DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  # Static Python modules are almost never wanted.
  BUILD_STATIC    OFF
  INSTALL_HEADERS OFF)

# Create an `__init__.py` containing wrapped filters.
set(python_modules)
foreach(module ${modules})
  _vtk_module_get_module_property("${module}"
    PROPERTY  "library_name"
    VARIABLE  library_name)
  list(APPEND python_modules "'${library_name}'")
endforeach()

list(JOIN python_modules ,  python_modules_string)
set(InitContent "__all__ = [${python_modules_string}]\n")
file(GENERATE
  OUTPUT  "${CMAKE_BINARY_DIR}/${python_destination}/wrapping/__init__.py"
  CONTENT "${InitContent}")
install(
  FILES       "${CMAKE_BINARY_DIR}/${python_destination}/wrapping/__init__.py"
  DESTINATION "${python_destination}/wrapping/")

# Install the module
export(
  EXPORT    wrapping_export
  NAMESPACE Wrapping::
  FILE      "${CMAKE_BINARY_DIR}/${python_destination}/wrapping/wrapping_export-targets.cmake")
install(
  EXPORT      wrapping_export
  NAMESPACE   Wrapping::
  FILE        wrapping_export-targets.cmake
  DESTINATION "${python_destination}/cmake/wrapping"
)
