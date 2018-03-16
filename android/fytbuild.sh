#!/bin/bash
usage()
{
    echo "USAGE: [-o] [-u] [-v VERSION_NAME]"
    echo "No ARGS means use default build option"
    echo "WHERE: -o = generate ota package       "
    echo "       -u = generate update.img        "
    echo "       -g = build with gms"
    echo "       -v = set build version name for output image folder"
    exit 1
}

BUILD_UPDATE_IMG=false
BUILD_OTA=false
BUILD_VERSION="IMAGES"

FYTVER="fytver=y"
GMS=
# check pass argument
while getopts "ougv:" arg
do
    case $arg in
        o)
            echo "will build ota package"
            BUILD_OTA=true
            ;;
        u)
            echo "will build update.img"
            BUILD_UPDATE_IMG=true
            ;;
        v)
            BUILD_VERSION=$OPTARG
            ;;
        g)
	    echo "build with gms"
	    BUILD_OTA=true
            GMS="gms"
            ;;
        ?)
            usage ;;
    esac
done

source build/envsetup.sh >/dev/null && setpaths
TARGET_PRODUCT=`get_build_var TARGET_PRODUCT`

#set jdk version
export JAVA_HOME=/home/build/tools/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib:$JAVA_HOME/lib/tools.jar
# source environment and chose target product
DEVICE=`get_build_var TARGET_PRODUCT`
BUILD_VARIANT=`get_build_var TARGET_BUILD_VARIANT`
UBOOT_DEFCONFIG=px5_kernel4.4_defconfig
KERNEL_DEFCONFIG=rockchip_defconfig
KERNEL_DTS=rk3368-px5-evb-android
PACK_TOOL_DIR=RKTools/linux/Linux_Pack_Firmware
IMAGE_PATH=rockdev/Image-$TARGET_PRODUCT
FYT_PATH=rockdev/Image-$TARGET_PRODUCT-$(date +%F)-$GMS
export PROJECT_TOP=`gettop`
#lunch $DEVICE-$BUILD_VARIANT

PLATFORM_VERSION=`get_build_var PLATFORM_VERSION`
DATE=$(date  +%Y%m%d.%H%M)
STUB_PATH=Image/"$KERNEL_DTS"_"$PLATFORM_VERSION"_"$DATE"_RELEASE_TEST
STUB_PATH="$(echo $STUB_PATH | tr '[:lower:]' '[:upper:]')"
export STUB_PATH=$PROJECT_TOP/$STUB_PATH
export STUB_PATCH_PATH=$STUB_PATH/PATCHES

# build uboot
echo "start build uboot"
cd u-boot && make distclean && make $UBOOT_DEFCONFIG && make ARCHV=aarch64 -j12 && cd -
if [ $? -eq 0 ]; then
    echo "Build uboot ok!"
else
    echo "Build uboot failed!"
    exit 1
fi


# build kernel
echo "Start build kernel"
cd kernel && make ARCH=arm64 $KERNEL_DEFCONFIG && make ARCH=arm64 $KERNEL_DTS.img -j12 && cd -
if [ $? -eq 0 ]; then
    echo "Build kernel ok!"
else
    echo "Build kernel failed!"
    exit 1
fi

if [ "$GMS" == "gms" ] ;then
    export FYT_BUILD_WHITH_GMS="true"
else
    export FYT_BUILD_WHITH_GMS="false"
fi
# build android
echo "start build android"
make installclean && make update-api && make $FYTVER -j12
if [ $? -eq 0 ]; then
    echo "Build android ok!"
else
    echo "Build android failed!"
    exit 1
fi

# mkimage.sh
echo "make and copy android images"
./mkimage.sh
if [ $? -eq 0 ]; then
    echo "Make image ok!"
else
    echo "Make image failed!"
    exit 1
fi

# copy images to rockdev
echo "copy u-boot images"
cp u-boot/uboot.img $IMAGE_PATH/
cp u-boot/RK3368MiniLoaderAll* $IMAGE_PATH/
cp u-boot/trust.img $IMAGE_PATH/

echo "copy kernel images"
cp kernel/resource.img $IMAGE_PATH/
cp kernel/kernel.img $IMAGE_PATH/

if [ "$BUILD_OTA" = true ] ; then
    INTERNAL_OTA_PACKAGE_OBJ_TARGET=obj/PACKAGING/target_files_intermediates/$TARGET_PRODUCT-target_files-*.zip
    INTERNAL_OTA_PACKAGE_TARGET=$TARGET_PRODUCT-ota-*.zip
    echo "generate ota package"
    make otapackage -j4
    ./mkimage.sh ota 
    cp $OUT/$INTERNAL_OTA_PACKAGE_TARGET $IMAGE_PATH/
    cp $OUT/$INTERNAL_OTA_PACKAGE_OBJ_TARGET $IMAGE_PATH/
fi


mkdir -p $PACK_TOOL_DIR/rockdev/Image/
cp -f $IMAGE_PATH/* $PACK_TOOL_DIR/rockdev/Image/

echo "Make update.img"
cd $PACK_TOOL_DIR/rockdev && ./mkupdate.sh
if [ $? -eq 0 ]; then
    echo "Make update image ok!"
else
    echo "Make update image failed!"
    exit 1
fi
cd -

mv $PACK_TOOL_DIR/rockdev/update.img $IMAGE_PATH/
rm $PACK_TOOL_DIR/rockdev/Image -rf
mv $IMAGE_PATH $FYT_PATH
