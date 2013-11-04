project(uweb)

uvis_install_files_with_prefix(
  bin/uweb.py
  content/index.html
  TARGET ${PROJECT_NAME}-webContentFiles
  DESTINATION share/uvis/www/apps/${PROJECT_NAME}
)

uvis_web_server(${PROJECT_NAME})
