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

# setup python
find_package(PythonInterp 2.7 REQUIRED)

# Find UVCDAT
if(UVIS_ENABLE_UVCDAT)
  set(UVCDAT_DIR "$ENV{UVCDAT_SETUP_PATH}")
  find_package(UVCDAT REQUIRED)

  if (UNIX)
    set(SOURCE_UVCDAT ". ${UVCDAT_DIR}/bin/setup_runtime.sh")
  endif()

  message("[uvis:info] Using UVCDAT ${UVCDAT_DIR}")
endif()

# Find ParaView
if(UVIS_ENABLE_PARAVIEW)

  find_path(
    PARAVIEW_WWW_DIR
    ext
    PATHS
    ${UVCDAT_DIR}/Externals/share/paraview-4.1/www
    ${UVCDAT_DIR}/Externals/share/paraview-4.2/www
    NO_DEFAULT_PATH
  )

  if(PARAVIEW_WWW_DIR-NOTFOUND)
    message(FATAL_ERROR "Could not find ParaViewWeb web root")
  endif()

  message("[uvis:info] Using ParaView ${ParaView_DIR}")
endif()

# Find Django
if(UVIS_ENABLE_DJANGO)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)

add_subdirectory(web)
add_subdirectory(apps)
add_subdirectory(modules)


