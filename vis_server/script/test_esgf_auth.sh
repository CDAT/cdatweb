#!/bin/bash

# This script tries to generate authentication tokens with MyProxyClient
# and dump the header from an authenticated OpenDAP url.  Have the following
# variables in your environment before running this command:
#
#     OPENID_HOST: the esgf hostname
#     OPENID_USER: your username
#     OPENID_PASSWORD: your password


# e.g.
# OPENID_HOST='pcmdi9.llnl.org'
# OPENID_USER='myusername'
# OPENID_PASSWORD='correct horse battery staple'

# additionally you can set ESGF_EXAMPLE_FILE to set the test OpenDAP url

: ${ESGF_EXAMPLE_FILE:='http://esg.ccs.ornl.gov/thredds/dodsC/acme_dataroot/ACME/h/t341f02.B1850dEdd/v0_0/ocn/T341_f02_t12/all/t341f02.B1850dEdd.pop.h.0001-01.nc'}
: ${TMP:=/tmp}
TESTDIR="${TMP}/esgf"
CADIR="${TESTDIR}/ca"
CERT="${TESTDIR}/cert.pem"
COOKIES="${TESTDIR}/.dods_cookies"
DODS="${TESTDIR}/.dodsrc"

if [[ -z "$OPENID_HOST" || -z "$OPENID_USER" || -z "$OPENID_PASSWORD" ]] ; then
    echo "Invalid environment variables" 1>&2
    exit 1
fi

rm -fr "$TESTDIR"
mkdir -p "$TESTDIR"
mkdir -p "$CADIR"
cat > "$DODS" <<EOF
HTTP.VERBOSE=100
USE_CACHE=0
MAX_CACHE_SIZE=20
MAX_CACHED_OBJ=5
IGNORE_EXPIRES=0
DEFAULT_EXPIRES=86400
ALWAYS_VALIDATE=0
DEFLATE=0
VALIDATE_SSL=0
HTTP.COOKIEJAR=${COOKIES}
HTTP.SSL.VALIDATE=0
HTTP.SSL.CERTIFICATE=${CERT}
HTTP.SSL.KEY=${CERT}
HTTP.SSL.CAPATH=${CADIR}
EOF

echo "${OPENID_PASSWORD}" | myproxyclient logon -S -s "${OPENID_HOST}" -l "${OPENID_USER}" -T -b -o "${CERT}" -C "${CADIR}"
fail=$?

d=$PWD
cd "$TESTDIR" && ncdump -h "${ESGF_EXAMPLE_FILE}" 2> "$d/dump.log"
fail=$(($fail + $?))
exit $fail
