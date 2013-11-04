uvis_install_files_with_prefix(
  ext/core/autobahn.js
  ext/core/autobahn.min.js
  ext/core/gl-matrix.js
  ext/core/gl-matrix-min.js
  ext/core/hammer.js
  ext/core/hammer.min.js
  ext/core/jquery-1.8.3.min.js
  ext/core/jquery.hammer.js
  ext/core/jquery.hammer.min.js
  ext/jquery-ui/jquery-ui-1.10.0.min.js
  SOURCE "${PARAVIEW_WWW_DIR}"
  TARGET webThirdPartyJsContentFiles
  DESTINATION share/uvis/www/content/js
  STRIP_PATH
)

uvis_install_files_with_prefix(
  ext/jquery-ui/jquery-ui-1.10.0.css
  SOURCE "${PARAVIEW_WWW_DIR}"
  TARGET webThirdPartyCssContentFiles
  DESTINATION share/uvis/www/content/css
  STRIP_PATH
)

uvis_install_files_with_prefix(
  content/index.html
  content/css/bootstrap.css
  content/css/bootstrap.min.css
  content/js/bootstrap.js
  content/js/bootstrap.min.js
  TARGET webContentFiles
  DESTINATION share/uvis/www
)

add_dependencies(webContentFiles
  webThirdPartyJsContentFiles
  webThirdPartyCssContentFiles
  webParaViewContentFiles
)


