#!/bin/bash

BSPDIR=bsp_userdebug
OUTDIR=out_userdebug
DEVICE=ums512_1h10_Natv-userdebug-native

usage()
{
    echo "USAGE: [-d] [-u] [-g] [-m] [-r] [-p] [-h] [-v] [-c] [-i] [j] [s] [k]"
    echo "No ARGS means use default build option userdebug"
    echo "WHERE: -d = userdebug       "
    echo "       -u = user        "
    echo "       -g = build with gms"
    echo "       -r = set build ota with u-boot-spl-16k.bin"
    echo "       -p = build product software"
    echo "       -v = build version add"
    echo "       -c = build pp with config.txt"
    echo "       -i = pack mipi6315lcdconfig.cfg for use"   
    echo "       -j = multi thread build" 
    exit 1
}

for arg in "$@"
do
	if [[ $arg =~ dtb ]]
	then
	DTB=$arg
	elif [ "${arg:0:6}" == "fytver" ]
	then
	FYTVER=$arg
	elif [ "${arg:0:2}" == "-j" ]
	then
	THREAD=$arg
	elif [ "${arg:0:5}" == "fytpp" ]
	then
	FYTPP=$arg
	elif [ "$arg" == "ota" ]
	then
	OTA=$arg
	elif [ "${arg:0:6}" == "upapp=" ]
	then
	UPAPP=${arg}
	fi
done

while getopts "dugrpvci:j" arg
do
    case $arg in
        d)
            echo "user debug"
            BSPDIR=bsp_userdebug
            OUTDIR=out_userdebug
	    DEVICE=ums512_1h10_Natv-userdebug-native
            ;;
        u)
	    echo "user "
            BSPDIR=bsp_user
            OUTDIR=out_user
	    DEVICE=ums512_1h10_Natv-user-native
            ;;
        g)
	    echo "build with gms"
            GMS="gms"
            ;;
        r)
           echo "build ota with u-boot-spl-16k.bin"
	   echo ${OPTARG}
           export ramtype=${OPTARG}
	   ;;
        p)
	    echo "build product"
	    cd device/sprd/sharkl5Pro/ums512_1h10/syu
	    #./oem.sh
	    python ./auto_generator.py ./ preinstall
	    cd -
	    export fytpp="y"
            ;;
        v)
	    echo "build version add"
	    export fytver="y"	 
            ;;
        c)
	    echo "build pp with config.txt"
	    export haveconfig="y"	 
            ;;
	i)
	   echo "build pac with mipi6315lcdconfig"
	   export USEMIPI="y"
		;;
	j)
	   echo "build thread"
		;;
        ?)
            usage ;;
    esac
done

source build/envsetup.sh >/dev/null
lunch $DEVICE

kheader
make installclean

if [ -d "out" ];then
cp -rf $OUTDIR/* out
else
cp -rf $OUTDIR out
fi

if [ -d "bsp" ];then
cp -rf $BSPDIR/* bsp
else
cp -rf $BSPDIR bsp
fi

if [ "$GMS" == "gms" ] ;then
    echo "Build Gms Package"
    export FYT_BUILD_WHITH_GMS="true"
fi


#make api-stubs-docs-update-current-api
#make test-api-stubs-docs-update-current-api
#make systemimage
#m oem_image && make -j8
make -j8 && make otapackage -j4
#source build/lsecpac.sh

#move
otapkg=out/target/product/ums512_1h10/ums512_1h10_Natv*.zip
updatepkg=6315_1.zip
if [ -e $otapkg ]; then
	target=sps.image/$(date +%Y%m%d_%H%M)$GMS
	echo "mkdir $target"
	mkdir -p $target
	mv $otapkg $target/$updatepkg
fi

