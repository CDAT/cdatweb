cmake_minimum_required(VERSION 2.8.8)

if(WIN32)
  message(FATAL_ERROR "Windows is not supported")
endif()

project(uvis)

include(cmake/functions.cmake)

list(APPEND CMAKE_MODULE_PATH "${uvis_SOURCE_DIR}/cmake")

option(UVIS_ENABLE_UVCDAT "UVIS uses UVCDAT" ON)
option(UVIS_ENABLE_PARAVIEW "UVIS uses UVCDAT" ON)
option(UVIS_ENABLE_DJANGO "UVIS uses Django" ON)

# Variable used for configuring runtime scripts
set(SOURCE_UVCDAT)

# Find UVCDAT
if(UVIS_ENABLE_UVCDAT)
  find_package(UVCDAT REQUIRED)

  if (UNIX)
    set(SOURCE_UVCDAT ". ${UVCDAT_DIR}/bin/setup_runtime.sh")
  endif()

  message("[uvis:info] Using UVCDAT ${UVCDAT_DIR}")
endif()

# Find ParaView
if(UVIS_ENABLE_PARAVIEW)
  # For now run another query to look for ParaView
  find_package(ParaView REQUIRED)
  include(${PARAVIEW_USE_FILE})

  message("[uvis:info] Using ParaView ${ParaView_DIR}")
endif()

# Find Django
if(UVIS_ENABLE_DJANGO)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)

add_subdirectory(web)
add_subdirectory(apps)
add_subdirectory(modules)


