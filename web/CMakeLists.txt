if (UVIS_ENABLE_PARAVIEW)
  uvis_install_files_with_prefix(
    ext/js-core/autobahn.js
    ext/js-core/autobahn.min.js
    ext/js-core/gl-matrix.js
    ext/js-core/gl-matrix-min.js
    ext/js-core/hammer.js
    ext/js-core/hammer.min.js
    ext/js-core/jquery-1.8.3.min.js
    ext/js-core/jquery.hammer.js
    ext/js-core/jquery.hammer.min.js
    ext/widgets/jquery-ui/jquery-ui-1.10.0.min.js
    lib/js/vtkweb-all.js
    SOURCE "${PARAVIEW_WWW_DIR}"
    TARGET webThirdPartyJsContentFiles
    DESTINATION share/uvis/www/content/js
    STRIP_PATH
  )

  uvis_install_files_with_prefix(
    ext/widgets/jquery-ui/jquery-ui-1.10.0.css
    SOURCE "${PARAVIEW_WWW_DIR}"
    TARGET webThirdPartyCssContentFiles
    DESTINATION share/uvis/www/content/css
    STRIP_PATH
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

add_dependencies(webContentFiles
  webThirdPartyJsContentFiles
  webThirdPartyCssContentFiles
  webParaViewContentFiles
)


