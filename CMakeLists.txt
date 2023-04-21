cmake_minimum_required(VERSION 3.12 FATAL_ERROR)

project(WrapExample)

# How to find the required components?
# these come from the CylinderExample
# https://kitware.github.io/vtk-examples/site/Cxx/GeometricObjects/CylinderExample/
find_package(VTK COMPONENTS 
  CommonColor
  CommonCore
  FiltersSources
  InteractionStyle
  RenderingContextOpenGL2
  RenderingCore
  RenderingFreeType
  RenderingGL2PSOpenGL2
  RenderingOpenGL2
  Python
)

if (NOT VTK_FOUND)
  message(FATAL_ERROR "WrapExample: Unable to find the VTK build folder.")
endif()

add_subdirectory(src)
