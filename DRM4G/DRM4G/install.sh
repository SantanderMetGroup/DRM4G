#!/bin/bash

BASE_URL="https://www.meteo.unican.es/work/DRM4G"
DRM4G_VERSION=2.3.0
DRM4G_DIR_INSTALATION=$PWD
DRM4G_HARDWARE=$(uname -m)

have_command () {
    type "$1" >/dev/null 2>/dev/null
}

require_command () {
    have_command "$1" 
    rc=$?
    if [ $rc -ne 0 ]
    then
        echo "Could not find required command '$1' in system PATH. Aborting."
        exit 1
    fi
}

require_python () {
    require_command "python"
    # Support 2.5 >= python < 3.0 
    python_version=$(python <<EOF
import sys
print(sys.version_info[0]==2 and sys.version_info[1] >= 5 )
EOF
)

    if [ "$python_version" != "True" ] 
    then
        echo "Wrong version of python is installed" 
        echo "DRM4G requires Python version 2.5+"
        echo "It does not support your version of python: $(python -V 2>&1|sed 's/python//gi')"
        exit 1
    fi
}

download_drm4g() {
    wget -nv --no-check-certificate -O $DRM4G_BUNDLE $BASE_URL/$DRM4G_BUNDLE
    rc=$?
    if [ $rc -ne 0 ]
    then
        echo "Unable to download bunble $DRM4G_BUNDLE ..."
        exit 1
    fi
}

unpack_drm4g() {
    tar xzf $DRM4G_BUNDLE -C $DRM4G_DIR_INSTALATION
    rc=$?
    if [ $rc -ne 0 ]
    then
        echo "Unable to unpack the bunble $DRM4G_BUNDLE in $DRM4G_DIR_INSTALATION"
        exit 1
    fi
}


usage () {
    cat <<EOF
This program installs DRM4G.

usage:
$0 [OPTIONS]

Options:

      -d, --dir DIRECTORY    Install DRM4G into a directory.
                             (Default: $DRM4G_DIR_INSTALATION)

      -V, --version          Version to install.
                             (Default: $DRM4G_VERSION)

      -h, --help             Print this help text.

EOF
}

while test -n "$1"
do
    case "$1" in
        -d|--dir)
            shift
            DRM4G_DIR_INSTALATION=$1
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -V|--version)
            DRM4G_VERSION=$1       
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
    shift
done

cat <<EOF
==========================
DRM4G installation script
==========================

This script will install DRM4G $DRM4G_VERSION 

EOF

# Check gcc and python  
require_command gcc

require_python

DRM4G_BUNDLE="drm4g-${DRM4G_VERSION}-${DRM4G_HARDWARE}.tar.gz"
echo ""
echo "--> Downloading $DRM4G_BUNDLE from $BASE_URL ..."
echo ""

if [ -f $DRM4G_BUNDLE ]
then
    echo "WARNING: $DRM4G_BUNDLE already exists"
    read -r -p "Are you sure you want to download it? [y/N] " response
    echo $response
    if [[ $prompt =~ [yY](es)* ]]
    then
        download_drm4g
    fi
else
     download_drm4g
fi

echo ""
echo "--> Unpacking $DRM4G_BUNDLE in directory $DRM4G_DIR_INSTALATION ..."
echo ""

if [ -d "$DRM4G_DIR_INSTALATION/drm4g" ]
then
    echo "WARNING: $DRM4G_DIR_INSTALATION/drm4g directory already exists"
    read -r -p "Are you sure you want to install it there? [y/N] " response
    echo $response
    if [[ $prompt =~ [yY](es)* ]]
    then
        unpack_drm4g
    fi
else
    unpack_drm4g
fi

cat <<EOF
===============================
Installation of DRM4G is done!
===============================

In order to work with DRM4G you have to enable its 
environment with the command:

    . $DRM4G_DIR_INSTALATION/drm4g/bin/drm4g_init.sh

You need to run the above command on every new shell you 
open before using DRM4G, but just once per session.

EOF

