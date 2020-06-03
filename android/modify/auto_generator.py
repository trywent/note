#!/usr/bin/env python
import sys
import os
import re
import zipfile
import shutil

templet = """include $(CLEAR_VARS)
LOCAL_MODULE := %s
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_PATH := $(TARGET_OUT_OEM)/%s
LOCAL_SRC_FILES := $(LOCAL_MODULE)$(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED
#LOCAL_DEX_PREOPT := false
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_JNI_SHARED_LIBRARIES_ABI := %s
MY_LOCAL_PREBUILT_JNI_LIBS := %s
MY_APP_LIB_PATH := $(TARGET_OUT_OEM)/%s/$(LOCAL_MODULE)/lib/$(LOCAL_JNI_SHARED_LIBRARIES_ABI)
ifneq ($(LOCAL_JNI_SHARED_LIBRARIES_ABI), None)
$(warning MY_APP_LIB_PATH=$(MY_APP_LIB_PATH))
LOCAL_POST_INSTALL_CMD := \
    mkdir -p $(MY_APP_LIB_PATH) \
    $(foreach lib, $(MY_LOCAL_PREBUILT_JNI_LIBS), ; cp -f $(LOCAL_PATH)/$(lib) $(MY_APP_LIB_PATH)/$(notdir $(lib)))
endif
include $(BUILD_PREBUILT)

"""

copy_app_templet = """LOCAL_PATH := $(my-dir)
include $(CLEAR_VARS)
LOCAL_APK_NAME := %s
LOCAL_POST_PROCESS_COMMAND := $(shell mkdir -p $(TARGET_OUT_OEM)/%s/$(LOCAL_APK_NAME) && cp $(LOCAL_PATH)/$(LOCAL_APK_NAME).apk $(TARGET_OUT_OEM)/%s/$(LOCAL_APK_NAME)/)
"""
copy_res_templet = """LOCAL_PATH := $(my-dir)
include $(CLEAR_VARS)
LOCAL_APK_NAME := %s
LOCAL_POST_PROCESS_COMMAND := $(shell mkdir -p $(TARGET_OUT_OEM)/res && cp $(LOCAL_PATH)/$(LOCAL_APK_NAME).apk $(TARGET_OUT_OEM)/res/)
"""

def unpackApp():
	os.system('rm -rf preinstall/*')
	os.system('./unpack Allapp.pkg  preinstall')
	os.system('rm -rf preinstall/*so')
	return

#SystemUI Settings comiple to 	/oem/priv-app/
#ResHolder copy to 		/oem/res/
#config.txt copy to 		/oem/app/
#all other fiel comipile to 	/oem/app/
#auto_generator.py src target
#python auto_generator.py ./ preinstall
def main(argv):
    unpackApp()
    preinstall_dir = os.path.join(argv[1],argv[2])
    appdir='app'
    vital = 'vital-app'
    if os.path.exists(preinstall_dir):
        #Use to include modules
        isfound = 'not_found_lib'
        include_path = preinstall_dir + '/preinstall.mk'
        android_path = preinstall_dir + '/Android.mk'

        if os.path.exists(include_path):
            os.remove(include_path)
        if os.path.exists(android_path):
            os.remove(android_path)

        includefile = file(include_path, 'w')
        androidfile = file(android_path, 'w')

        androidfile.write("include $(call all-subdir-makefiles)\n\n")

        MY_LOCAL_PREBUILT_JNI_LIBS = '\\' + '\n'

        for root, dirs, files in os.walk(preinstall_dir):
            for file_name in files:
                p = re.compile(r'\S*(?=.apk\b)')
                found = p.search(file_name)
                if found:
                    include_apk_path = preinstall_dir + '/' + found.group()
                    makefile_path = include_apk_path + '/Android.mk'
                    apk = preinstall_dir + '/' + found.group() + '.apk'
		    priv = found.group().find('SystemUI')>=0 or found.group().find('Setting')>=0
                    try:
                        zfile = zipfile.ZipFile(apk,'r')
                    except:
                        if os.path.exists(include_apk_path):
                            shutil.rmtree(include_apk_path)
                        os.makedirs(include_apk_path)
                        apkpath = preinstall_dir + '/' + found.group() + '/'
                        shutil.move(apk,apkpath)
                        makefile = file(makefile_path,'w')
                        makefile.write("LOCAL_PATH := $(my-dir)\n\n")
                        makefile.write(templet % (found.group(),appdir,'None',MY_LOCAL_PREBUILT_JNI_LIBS,appdir))
                        continue
                    for lib_name in zfile.namelist():
                        include_apklib_path = include_apk_path + '/lib' + '/arm'
                        if os.path.exists(include_apk_path):
                            shutil.rmtree(include_apk_path)
                        os.makedirs(include_apklib_path)
                        makefile = file(makefile_path,'w')
                        makefile.write("LOCAL_PATH := $(my-dir)\n\n")
                        apkpath = preinstall_dir + '/' + found.group() + '/'
                    for lib_name in zfile.namelist():
                        lib = re.compile(r'\A(lib/armeabi-v7a/)+?')
                        find_name = 'lib/armeabi-v7a/'
                        if not cmp(lib_name,find_name):
                            continue
                        libfound = lib.search(lib_name)
                        if libfound:
                            isfound = 'armeabi-v7a'
                            data = zfile.read(lib_name)
                            string = lib_name.split(libfound.group())
                            libfile = include_apklib_path + '/' + string[1]
                            MY_LOCAL_PREBUILT_JNI_LIBS += '\t' + 'lib/arm' + '/' + string[1] + '\\' + '\n'
                            if(os.path.isdir(libfile)):
                                continue
                            else:
                                includelib = file(libfile,'w')
                                includelib.write(data)
                    if not cmp(isfound,'not_found_lib'):
                        for lib_name in zfile.namelist():
                            lib = re.compile(r'\A(lib/armeabi/)+?')
                            find_name = 'lib/armeabi/'
                            if not cmp(lib_name,find_name):
                                continue
                            libfound = lib.search(lib_name)
                            if libfound:
                                data = zfile.read(lib_name)
                                string = lib_name.split(libfound.group())
                                libfile = include_apklib_path + '/' + string[1]
                                MY_LOCAL_PREBUILT_JNI_LIBS += '\t' + 'lib/arm' + '/' + string[1] + '\\' + '\n'
                                if(os.path.isdir(libfile)):
				    continue
				else:
                                    includelib = file(libfile,'w')
                                    includelib.write(data)
                    tmp_jni_libs = '\\' + '\n'
		    #apk Andoid.mk
		    nolib = MY_LOCAL_PREBUILT_JNI_LIBS==tmp_jni_libs
		    lib = 'None' if nolib else 'arm';
                    if nolib:#no libs apk
                        nolibpath = preinstall_dir + '/' + found.group() + '/lib'
                        shutil.rmtree(nolibpath)
		    if found.group().find('ResHolder')>=0:
			makefile.write(copy_res_templet % (found.group()))
		    elif priv:
                       	makefile.write(templet % (found.group()+'1','priv-'+appdir,lib,MY_LOCAL_PREBUILT_JNI_LIBS,appdir))
		    else:
			makefile.write(templet % (found.group(),appdir,lib,MY_LOCAL_PREBUILT_JNI_LIBS,appdir))

                    shutil.move(apk,apkpath+found.group()+'1.apk' if priv else apkpath)
                    isfound = 'not_found_lib'
                    MY_LOCAL_PREBUILT_JNI_LIBS = '\\' + '\n'
                    makefile.close()
            break
	#apk product.mk
        for root, dirs,files in os.walk(preinstall_dir):
            for dir_file in dirs:
		if dir_file=='uninstallable':
			continue
		if dir_file=='SystemUI' or dir_file=='Settings':
			dir_file+='1'
                includefile.write('PRODUCT_PACKAGES += %s\n' %dir_file)
            break

	#vital file
	vitaldir = preinstall_dir+'/uninstallable'
	vitalmkfile = file(vitaldir+'/Android.mk', 'w')
	vitalmkfile.write("include $(call all-subdir-makefiles)\n\n")
        for root, dirs,files in os.walk(vitaldir):
            for filename in files:
		print(filename)
		p = re.compile(r'\S*(?=.apk\b)')
		found = p.search(filename)
		if filename!='Android.mk' and found:
			include_apk_path = vitaldir + '/' + found.group()
                    	makefile_path = include_apk_path + '/Android.mk'			
                   	apk = vitaldir + '/' + found.group() + '.apk'
			if os.path.exists(include_apk_path):
                            shutil.rmtree(include_apk_path)
                        os.makedirs(include_apk_path)

			makefile = file(makefile_path,'w')
			makefile.write(copy_app_templet % (found.group(), vital, vital))			
			makefile.close()
			shutil.move(apk,include_apk_path)
			includefile.write('PRODUCT_PACKAGES += %s \n' % (found.group()))
            break

	#config file
        for root, dirs,files in os.walk(preinstall_dir):
            for filename in files:
		print(filename)
		if filename!='Android.mk' and filename!='preinstall.mk':
	                includefile.write('PRODUCT_COPY_FILES +=$(CUR_PATH)/syu/preinstall/%s:oem/app/%s \n' % (filename, filename))
            break
        includefile.close()

if __name__=="__main__":
  main(sys.argv)
