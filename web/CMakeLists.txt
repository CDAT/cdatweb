if (UVIS_ENABLE_PARAVIEW)
  uvis_install_files_with_prefix(
    ext/core/autobahn.min.js
    ext/core/gl-matrix-min.js
    ext/core/hammer.min.js
    ext/core/jquery-1.8.3.min.js
    ext/core/jquery.hammer.min.js
    ext/jquery-ui/jquery-ui-1.10.0.min.js
    lib/core/vtkweb-all.js
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
    content/js/vgl.min.js
    TARGET webVGLoverwrite
    DESTINATION share/uvis/www
  )

endif()

uvis_install_files_with_prefix(
  content/css/bootstrap.css
  content/css/bootstrap.min.css
  content/js/bootstrap.js
  content/js/bootstrap.min.js
  TARGET webContentFiles
  DESTINATION share/uvis/www
)

uvis_install_files_with_prefix(
  content/data/test.nc
  TARGET webContentData
  DESTINATION share/uvis/www
)

add_dependencies(webContentFiles
  webThirdPartyJsContentFiles
  webThirdPartyCssContentFiles
  webParaViewContentFiles
)


