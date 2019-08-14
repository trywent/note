#!/usr/bin/env bash

PREFIX=/$PWD/out

build(){
    PLATFORM=$1
    echo "======== > Start build $PLATFORM"
    case ${PLATFORM} in
    android )
	ARCH="x86_64"
    ;;
    linux )
        ARCH="x86_64"
    ;;
    esac
    
    echo "-------- > Start clean workspace"
    make clean

    echo "-------- > Start build configuration"
    CONFIGURATION="$CONFIGURATION --prefix=$PREFIX"
    CONFIGURATION="$CONFIGURATION --exec-prefix=$PREFIX"

    echo "-------- > Start config makefile with $CONFIGURATION "
    ./configure ${CONFIGURATION}

    echo "-------- > Start make "
    make

    echo "-------- > Start install"
    make install
    echo "-------- >  make and install complete."

}


echo "-------- Start --------"

build

echo "-------- End --------"
