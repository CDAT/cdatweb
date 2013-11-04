# Function to extract first argument into named variable
function(shift_arg variable value)
  set(${variable} "${value}" PARENT_SCOPE)
  set(ARGN "${ARGN}" PARENT_SCOPE)
endfunction()

# Helper macro to parse template argument of extract_flags, extract_args
macro(__parse_extract_template template)
  set(_vars "")
  set(_extra "")

  foreach(pair ${template})
    string(REGEX MATCH "^[^=]+" varname "${pair}")
    string(REGEX REPLACE "^[^=]+=" "" token "${pair}")
    if("x_${varname}" STREQUAL "x_" OR "x_${token}" STREQUAL "x_")
      message(FATAL_ERROR "extract_args: bad variable/token pair '${pair}'")
    endif()
    set(${varname} "")
    set(__var_for_token_${token} "${varname}")
    list(APPEND _vars "${varname}")
  endforeach()
endmacro()

# Function to extract named flags
function(extract_flags template)
  __parse_extract_template("${template}")
  foreach(_var ${_vars})
    # Initially set all flags to FALSE
    set(${_var} FALSE PARENT_SCOPE)
  endforeach()

  foreach(arg ${ARGN})
    # Skip empty args
    if(NOT "x_${arg}" STREQUAL "x_")
      # Test if arg is a token
      if(NOT "x_${__var_for_token_${arg}}" STREQUAL "x_")
        # Yes; set flag to TRUE
        set(${__var_for_token_${arg}} TRUE PARENT_SCOPE)
      else()
        # No; add to leftovers list
        list(APPEND _extra "${arg}")
      endif()
    endif()
  endforeach()

  # Shift ARGN
  set(ARGN "${_extra}" PARENT_SCOPE)
endfunction()

# Function to extract named arguments
function(extract_args template)
  __parse_extract_template("${template}")
  set(_var "")

  foreach(arg ${ARGN})
    # Skip empty args
    if(NOT "x_${arg}" STREQUAL "x_")
      # Test if arg is a token
      if(NOT "x_${__var_for_token_${arg}}" STREQUAL "x_")
        set(_var "${__var_for_token_${arg}}")
      # Not a token; test if we have a current token
      elseif(NOT "x_${_var}" STREQUAL "x_")
        # Add arg to named list
        list(APPEND ${_var} "${arg}")
      else()
        # Add arg to leftovers list
        list(APPEND _extra "${arg}")
      endif()
    endif()
  endforeach()

  # Raise lists to parent scope
  foreach(varname ${_vars})
    set(${varname} "${${varname}}" PARENT_SCOPE)
  endforeach()

  # Shift ARGN
  set(ARGN "${_extra}" PARENT
_SCOPE)
endfunction()

# Function to install files with (optionally) their respective path prefixes
function(uvis_install_files_with_prefix)
  cmake_parse_arguments(_install
    "STRIP_PATH"
    "SOURCE;TARGET;DESTINATION"
    "FILES"
    ${ARGN}
  )
  list(APPEND _install_FILES ${_install_UNPARSED_ARGUMENTS})

  set(_path)
  set(_in_prefix)
  if(_install_SOURCE)
    set(_in_prefix "${_install_SOURCE}/")
  endif()

  set(_target_depends)
  foreach(file ${_install_FILES})
    get_filename_component(_in "${_in_prefix}${file}" REALPATH)
    get_filename_component(_name "${file}" NAME)
    if(NOT _install_STRIP_PATH)
      get_filename_component(_path "${file}" PATH)
    endif()
    set(_out "${uvis_BINARY_DIR}/${_install_DESTINATION}/${_path}/${_name}")

    add_custom_command(OUTPUT "${_out}" DEPENDS "${_in}"
                       COMMAND ${CMAKE_COMMAND} -E copy "${_in}" "${_out}")
    list(APPEND _target_depends "${_out}")

    install(FILES "${_in_prefix}${file}"
      DESTINATION ${_install_DESTINATION}/${_path}
      COMPONENT Web
    )
  endforeach()

  add_custom_target(${_install_TARGET} ALL DEPENDS ${_target_depends})
endfunction()

set(UVIS_RUN_SERVER_SCRIPT_TEMPLATE "${uvis_SOURCE_DIR}/web/uvis.sh.in" CACHE PATH INTERNAL)

# Function to create and install a script to run an application's web server
function(uvis_web_server NAME)
  set(_configure_file_script
    "${uvis_SOURCE_DIR}/cmake/configure-file-script.cmake"
  )
  set(_out "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${NAME}-server")
  add_custom_command(
    OUTPUT "${_out}"
    DEPENDS "${UVIS_RUN_SERVER_SCRIPT_TEMPLATE}" "${_configure_file_script}"
    COMMAND "${CMAKE_COMMAND}"
      "-DINPUT_FILE=${UVIS_RUN_SERVER_SCRIPT_TEMPLATE}"
      "-DOUTPUT_FILE=${_out}"
      "-DLIB_SUFFIX=${LIB_SUFFIX}"
      "-DPYTHON_SHORT=${PYTHON_SHORT}"
      "-DAPPLICATION=${NAME}"
      "-DSERVER_PYTHON_SCRIPT=${NAME}.py"
      "-DSOURCE_UVCDAT=${SOURCE_UVCDAT}"
      "-DCONFIGURE_ARGS=ESCAPE_QUOTES @ONLY"
      -P "${_configure_file_script}"
  )
  add_custom_target(${NAME}-server ALL DEPENDS "${_out}")
  install(PROGRAMS "${_out}" DESTINATION bin COMPONENT Web)
endfunction()
