
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := ec.conf
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_STEM := $(LOCAL_MODULE)
LOCAL_MODULE_CLASS := ETC
LOCAL_SRC_FILES := $(LOCAL_MODULE)
LOCAL_MODULE_PATH := $(TARGET_OUT)/app
include $(BUILD_PREBUILT)

SRC_FILE := $(LOCAL_MODULE)
SYMLINKS := $(TARGET_OUT)/system/etc/$(SRC_FILE)
#didiMiudriveScreen: TARGET_FILE := $(TARGET_OUT)/vendor/etc/$(LOCAL_MODULE)
$(SYMLINKS):
	@echo "Symlink: $@ -> /system/app/$(SRC_FILE)"
	@mkdir -p $(dir $@)
	@rm -rf $@
	$(hide) ln -sf /system/app/$(SRC_FILE) $@

ALL_DEFAULT_INSTALLED_MODULES += $(SYMLINKS)

ALL_MODULES.$(LOCAL_MODULE).INSTALLED := \
	$(ALL_MODULES.$(LOCAL_MODULE).INSTALLED) $(SYMLINKS) 

