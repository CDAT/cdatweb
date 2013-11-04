include(FindPackageHandleStandardArgs)

# Look for UVCDAT
find_path(UVCDAT_DIR uvcdat
  NO_DEFAULT_PATH
  PATH_SUFFIXES bin
)
if(UVCDAT_DIR-NOTFOUND)
  message(FATAL_ERROR "Package UVCDAT not found")
endif()

find_package_handle_standard_args(UVCDAT DEFAULT_MSG UVCDAT_DIR)
