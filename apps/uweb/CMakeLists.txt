project(uweb)

#uvis_install_files_with_prefix(
#  bin/uweb.py
#  home
#  login
#  TARGET ${PROJECT_NAME}-webContentFiles
#  DESTINATION share/uvis/www/apps/${PROJECT_NAME}
#)

uvis_install_directories_with_prefix(
  bin
  esgf_auth_backend
  home
  login
  util  
  uvdjango
  TARGET ${PROJECT_NAME}-webContentDirectories
  DESTINATION share/uvis/www/apps/${PROJECT_NAME}
)

uvis_web_server(${PROJECT_NAME})
