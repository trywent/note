LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LOCAL_SRC_FILES:= getSer.c
LOCAL_MODULE_TAGS:= optional
LOCAL_MODULE:= getserialno

include $(BUILD_EXECUTABLE)
