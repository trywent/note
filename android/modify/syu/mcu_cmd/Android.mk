LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LOCAL_SRC_FILES:= mcu.c
LOCAL_MODULE_TAGS:= optional
LOCAL_SHARED_LIBRARIES := libc libcutils liblog
LOCAL_MODULE:= mcu_command

include $(BUILD_EXECUTABLE)
