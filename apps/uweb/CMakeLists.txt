project(uweb)

uvis_install_directories_with_prefix(
  bin
  esgf_auth_backend
  home
  diag
  login
  lib_util
  uvdjango
  TARGET ${PROJECT_NAME}-webContentDirectories
  DESTINATION share/uvis/www/apps/${PROJECT_NAME}
)

set(UVDJANGO_DBFILE "${CMAKE_BINARY_DIR}/uvdjango.db"
  CACHE FILEPATH
  "The uvdjango sqlite database file")

# install local_settings.py to uvdjango/
set(_local_settings_out ${uvis_BINARY_DIR}/share/uvis/www/apps/${PROJECT_NAME}/uvdjango/local_settings.py)
set(_local_settings_in ${CMAKE_CURRENT_SOURCE_DIR}/uvdjango/local_settings.py.template)
add_custom_command(
  OUTPUT "${_local_settings_out}"
  COMMAND ${CMAKE_COMMAND}
              "-DUVDJANGO_DBFILE=${UVDJANGO_DBFILE}"
              "-DSOURCE=${_local_settings_in}"
              "-DDESTINATION=${_local_settings_out}"
              -P "${CMAKE_SOURCE_DIR}/cmake/configure_template.cmake"
  COMMAND ${CMAKE_COMMAND} -E touch "${_local_settings_out}"
  DEPENDS "${_local_settings_in}" "${PROJECT_NAME}-webContentDirectories"
  COMMENT "Configuring ${_local_settings_out}"
)

# Create the database if requested
set(UVDJANGO_CREATE_DATABASE ON CACHE BOOL
  "Create the database file if it doesn't exist"
)

if(UVDJANGO_CREATE_DATABASE)
  set(_dir  "${uvis_BINARY_DIR}/share/uvis/www/apps/${PROJECT_NAME}")
  add_custom_command(
    OUTPUT "${UVDJANGO_DBFILE}"
    COMMAND env "PYTHONPATH=${_dir}" "${PYTHON_EXECUTABLE}" "${_dir}/bin/manage.py" syncdb --noinput
    DEPENDS
    "${_local_settings_out}"
    "${PROJECT_NAME}-webContentDirectories"
    COMMENT
    "Creating ${UVDJANGO_DBFILE}"
  )

  add_custom_target(
    uvdjango_database
    ALL
    DEPENDS "${UVDJANGO_DBFILE}"
  )
endif()

uvis_web_server(${PROJECT_NAME})
