
err=''
wrn=''
rst=''
if [ -t 2 ] ; then
    err="$(tput setaf 1)"
    rst="$(tput sgr0)"
    wrn="$(tput setaf 3)"
fi

if [ -z "${UVCDAT_SETUP_PATH}" ] ; then
    echo -e "${err}ERROR: UVCDAT environment not sourced.${rst}" 1>&2
    exit 1
fi

clientpath="${UVCDAT_SETUP_PATH}/Externals/lib/www"

if [ ! -d "${clientpath}" ] ; then
    echo -e "${err}ERROR: Cannot find vtkweb client files.${rst}" 1>&2
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

# start up the server
"${UVCDAT_SETUP_PATH}/Externals/lib/python2.7/site-packages/vtk/web/launcher.py" config.json
