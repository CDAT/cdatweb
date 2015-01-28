
err=''
wrn=''
rst=''
tput -V &> /dev/null
if [ -t 2 -a $? -eq 0 ] ; then
    err="$(tput setaf 1)"
    rst="$(tput sgr0)"
    wrn="$(tput setaf 3)"
fi

python_program="vtkpython"

vtkpython --version &> /dev/null
if [ $? -ne 0 ] ; then
    python_program="python"
fi

VTK_PYTHON_PATH="$(${python_program} -c "import os, vtk; print os.path.abspath(os.path.dirname(vtk.__file__))" 2> /dev/null)"
if [ ! -d "${VTK_PYTHON_PATH}" ] ; then
    echo ${VKT_PYTHON_PATH}
    echo -e "${err}ERROR: Cannot find vtk's python path.${rst}"
    exit 1
fi

clientpath="${VTKWEB_CLIENT_PATH:-${VTK_PYTHON_PATH}/../../../www}"
if [ ! -d "${clientpath}" ] ; then
    echo -e "${err}ERROR: Cannot find vtkweb client files.${rst}" 1>&2
    echo -e "${wrn}Is vtk compiled with vtkWeb support?${rst}" 1>&2
    echo -e "${wrn}Try setting VTKWEB_CLIENTPATH to the vtk webroot path.${rst}" 1>&2
    exit 1
fi

staticpath="$(dirname $0)/../static"
if [ ! -d "${staticpath}" ] ; then
    echo -e "${err}ERROR: Cannot find django project static root.${rst}" 1>&2
    exit 1
fi

# update client side scripts
rm -fr "${staticpath}/vtkweb"
ln -sf "${clientpath}" "${staticpath}/vtkweb"
rm -f ../tmp/logs/* &> /dev/null
mkdir -p ../tmp/logs &> /dev/null

# create a fake file tree
rm -fr ../tmp/test &> /dev/null
mkdir -p ../tmp/test &> /dev/null
export PYTHONPATH="${PYTHONPATH}:${VTK_PYTHON_PATH}"
${python_program} testing.py ../tmp/test test_files/test_files.json

# start up the server
${python_program} "${VTK_PYTHON_PATH}/web/launcher.py" test_files/test.json
