
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

rm -f ../tmp/logs/* &> /dev/null
mkdir -p ../tmp/logs &> /dev/null

# start up the server
python launcher.py config-local.json
