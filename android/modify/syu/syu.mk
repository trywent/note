CUR_PATH := device/rockchip/px5
REC_PATCH := bootable/recovery

PRODUCT_PACKAGES += \
	libsqlcontrol \
	getserialno \
	libts_op \
	libsyu_jni \
	mcu_command \
	RKUpdateService \
	libfmjni \
	ntfs-3g \
	libfytcamera \
	bootwatcher \
	sqlwarn \
	sqldebug \
	bootwatcher \
	sqlactive \
	libjni_serial \
	libjni_i2c \
	libjni_spectrum \
	libjni_toolkit \
	libfytcamera \
	libusb \
      libsqltouch \

#	tuku
  



PRODUCT_COPY_FILES += \
    $(CUR_PATH)/syu/lib/libBaiduMapSDK_base_v3_7_1.so:system/lib/libBaiduMapSDK_base_v3_7_1.so \
    $(CUR_PATH)/syu/lib/libBaiduMapSDK_cloud_v3_7_1.so:system/lib/libBaiduMapSDK_cloud_v3_7_1.so \
    $(CUR_PATH)/syu/lib/libBaiduMapSDK_map_v3_7_1.so:system/lib/libBaiduMapSDK_map_v3_7_1.so \
    $(CUR_PATH)/syu/lib/libBaiduMapSDK_radar_v3_7_1.so:system/lib/libBaiduMapSDK_radar_v3_7_1.so \
    $(CUR_PATH)/syu/lib/libBaiduMapSDK_search_v3_7_1.so:system/lib/libBaiduMapSDK_search_v3_7_1.so \
    $(CUR_PATH)/syu/lib/libBaiduMapSDK_util_v3_7_1.so:system/lib/libBaiduMapSDK_util_v3_7_1.so \
    $(CUR_PATH)/syu/lib/libbd_etts.so:system/lib/libbd_etts.so \
    $(CUR_PATH)/syu/lib/libBDSpeechDecoder_V1.so:system/lib/libBDSpeechDecoder_V1.so \
    $(CUR_PATH)/syu/lib/libbdtts.so:system/lib/libbdtts.so \
    $(CUR_PATH)/syu/lib/libgnustl_shared.so:system/lib/libgnustl_shared.so \
    $(CUR_PATH)/syu/lib/liblocSDK6a.so:system/lib/liblocSDK6a.so \
    $(CUR_PATH)/syu/kmsg2file:system/bin/kmsg2file \
    $(CUR_PATH)/syu/updateanimation.zip:system/media/updateanimation.zip \
    $(CUR_PATH)/syu/fyt.ogg:system/media/audio/ringtones/fyt.ogg \
    $(CUR_PATH)/syu/8328/libusb.so:system/lib/libusb.so \
    $(CUR_PATH)/syu/8328/switchtocam:system/bin/switchtocam \
    $(CUR_PATH)/syu/shcmd:system/bin/shcmd \
    $(CUR_PATH)/syu/bootanimation.zip:system/media/bootanimation.zip \
    $(CUR_PATH)/syu/bdcf/bdcl:system/bin/bdcl \
    $(CUR_PATH)/syu/bdcf/bdcf:system/app/bdcf \
    $(CUR_PATH)/syu/bdcf/bdcl-guard.sh:system/bin/bdcl-guard.sh \
    $(CUR_PATH)/syu/init.syu.rc:root/init.syu.rc \
    $(CUR_PATH)/syu/uvc/libusb.so:system/lib/libusb.so \
    $(CUR_PATH)/syu/uvc/libusb64.so:system/lib64/libusb.so \
    $(CUR_PATH)/syu/uvc/switchtocam:system/bin/switchtocam \
    $(CUR_PATH)/syu/uvc/rainuvc/librain_uvc32.so:system/lib/librain_uvc.so \
    $(CUR_PATH)/syu/uvc/rainuvc/librain_uvc64.so:system/lib64/librain_uvc.so

#bluetooth
PRODUCT_COPY_FILES += \
    $(CUR_PATH)/syu/8723ds/blink:vendor/bin/blink \
    $(CUR_PATH)/syu/8723ds/blink_config.ini:system/blink_config.ini \
    $(CUR_PATH)/syu/8723ds/blink_ring.mp3:system/blink_ring.mp3 \
    $(CUR_PATH)/syu/8723ds/libwapm.so:vendor/lib/libwapm.so \

#easyconnect
PRODUCT_COPY_FILES += \
    $(CUR_PATH)/syu/easyconnect/adb-ec:system/bin/adb-ec \
    $(CUR_PATH)/syu/easyconnect/adb-ec-server.sh:system/bin/adb-ec-server.sh \
    $(CUR_PATH)/syu/easyconnect/libcshell.so:system/lib/libcshell.so\
    $(CUR_PATH)/syu/easyconnect/libecgl2jni.so:system/lib/libecgl2jni.so\
    $(CUR_PATH)/syu/easyconnect/libmDNSEmbedded.so:system/lib/libmDNSEmbedded.so \
    $(CUR_PATH)/syu/easyconnect/libmediaserver.so:system/lib/libmediaserver.so \
    $(CUR_PATH)/syu/easyconnect/libecgl2jni_vfpv3.so:system/lib/libecgl2jni_vfpv3.so \
    $(CUR_PATH)/syu/easyconnect/libusbconfig.so:system/lib/libusbconfig.so \
    $(CUR_PATH)/syu/easyconnect/usbmuxd:system/bin/usbmuxd \
    $(CUR_PATH)/syu/easyconnect/start_usbmuxd.sh:system/bin/start_usbmuxd.sh \
    $(CUR_PATH)/syu/easyconnect/ec_conn_type:system/etc/ec_conn_type


#carplay
PRODUCT_COPY_FILES += \
    $(CUR_PATH)/syu/carplay/z-link:vendor/bin/z-link \
    $(CUR_PATH)/syu/carplay/z-link.sh:vendor/bin/z-link.sh \
    $(CUR_PATH)/syu/carplay/zj_device.sh:vendor/bin/zj_device.sh\
    $(CUR_PATH)/syu/carplay/zj_host.sh:vendor/bin/zj_host.sh \
    $(CUR_PATH)/syu/carplay/z-mdnsd:vendor/bin/z-mdnsd \
    $(CUR_PATH)/syu/carplay/exit.png:vendor/etc/exit.png \
    $(CUR_PATH)/syu/carplay/airplayutil:vendor/bin/airplayutil \
    $(CUR_PATH)/syu/carplay/libAirPlay.so:vendor/lib64/libAirPlay.so \
    $(CUR_PATH)/syu/carplay/libAirPlaySupport.so:vendor/lib64/libAirPlaySupport.so \
    $(CUR_PATH)/syu/carplay/libAudioStream.so:vendor/lib64/libAudioStream.so \
    $(CUR_PATH)/syu/carplay/libCoreUtils.so:vendor/lib64/libCoreUtils.so \
    $(CUR_PATH)/syu/carplay/libdns_sd.so:vendor/lib64/libdns_sd.so \
    $(CUR_PATH)/syu/carplay/libScreenStream.so:vendor/lib64/libScreenStream.so \
    $(CUR_PATH)/syu/carplay/libautohelper_v1.1.2.so:vendor/lib64/libautohelper_v1.1.2.so \
    $(CUR_PATH)/syu/carplay/z-adb:vendor/bin/z-adb
    
PRODUCT_COPY_FILES += \
    $(CUR_PATH)/syu/adbmodem/fyt-adb_on.sh:system/bin/fyt-adb_on.sh \
    $(CUR_PATH)/syu/adbmodem/fyt-adb_off.sh:system/bin/fyt-adb_off.sh 


#prebuilt app for factory
ifeq ($(strip $(fytpp)),y)
#$(shell python device/rockchip/px5/sql_config_auto.py $(TARGET_PRODUCT) appfile app ppversion hah)
#$(shell python $(CUR_PATH)/app_auto_generator.py $(TARGET_PRODUCT) fapp app app)
PRODUCT_PACKAGES += \
	fyt_prebuilt_apps

PRODUCT_COPY_FILES += \
    $(CUR_PATH)/prebuilt-apps/system/app/todo/fyt.prop:system/app/fyt.prop \
    $(CUR_PATH)/prebuilt-apps/system/app/todo/skipkillapp.prop:system/app/skipkillapp.prop \


#WITH_DEXPREOPT := true
endif
WITH_DEXPREOPT := true

#rk lib
PRODUCT_COPY_FILES += \
    $(CUR_PATH)/syu/libavtone.so:system/lib/libavtone.so 

ifeq ($(FYT_BUILD_WHITH_GMS),true)
$(call inherit-product-if-exists, vendor/google/gms.mk)
else
PRODUCT_PACKAGES += \
    GooglePinyinIME 

endif

#bluetooth
#PRODUCT_PACKAGES += \
	Bluetooth


