LOCAL_PATH:= $(call my-dir)

include $(CLEAR_VARS)

LOCAL_SRC_FILES := bootwatcher.cpp
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE := bootwatcher
LOCAL_MODULE_PATH := $(TARGET_ROOT_OUT_SBIN)
LOCAL_FORCE_STATIC_EXECUTABLE := true

LOCAL_PACKAGE_NAME := bootwatcher


LOCAL_STATIC_LIBRARIES := libutils libcutils libc liblog

include $(BUILD_EXECUTABLE)

