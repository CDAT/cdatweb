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

uvis_web_server(${PROJECT_NAME})
