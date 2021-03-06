#!/usr/bin/env python
import sys
import os
import re
import zipfile
import shutil
import time
import struct

#templet1 name appdir lib
templet1 = """LOCAL_PATH := $(my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := %s
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_PATH := $(TARGET_OUT_OEM)/%s
LOCAL_SRC_FILES := $(LOCAL_MODULE)$(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
libsrc := %s
ifneq ($(libsrc), '')
LOCAL_POST_INSTALL_CMD := \
    mkdir -p $(MY_APP_LIB_PATH) \
    && cp -f $(libsrc) $(LOCAL_MODULE_PATH)
endif
include $(BUILD_PREBUILT)

"""

# templet modluelname appdst arch libsrc appdst
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

SIGNATURE_INFO = 0x53514C42
BOARDCFG_ADDR = 0x238
TOUCH_ADDR= 0x600
GAMMA_ADDR= 0x1000
T132_ADDR= 0x2000
APPTIME_ADDR= 0x100400
CFGFILESIZE = 0x1c8
NAVICOPY_FLAG=0X101000
SIMFLAG_ADDR =0X101C00

SIG_UPDATE_CLEAR=0x55434c52
SIG_NEEDUBOOTUSB=0X42555342
NEEDUBOOTUSB_CNT=5
UCLEAR_ADDR=0x6000

PANCFG_ADDR = 0x70
PANCFGSIZE  = 0X1C8

pad_data = [0x00 for i in range(0x200000)] 
def lsecconf(val):
    cur_dir = './'
    unpack_dir = cur_dir+ 'config'

    packagefile_path = cur_dir + '/AllAppUpdate.bin'    
    partitionfile = cur_dir + 'sql_config.pkg'
    
    tchfile = unpack_dir + '/gtsql_config'
    boardcfgfile = unpack_dir + '/6315boardcfg.cfg'
    panelcfgfile = unpack_dir + '/6315lcdconfig.cfg'
 
    statinfo=os.stat(packagefile_path)


    thislocal=time.localtime(statinfo.st_mtime)
    if os.path.exists(partitionfile):
        os.remove(partitionfile)

    f=open(partitionfile,"wb+")
    f.write(bytearray(pad_data)) 
    f.seek(0)   
    f.write(struct.pack("i", SIGNATURE_INFO))


    if not os.path.isfile(panelcfgfile):
        print("ERROR: %s is not a valid file." % (panelcfgfile))
    else:
        print("write %s ." % (panelcfgfile))
        s=open(panelcfgfile,"rb")
        data = s.read(PANCFGSIZE)
        s.close()
        f.seek(PANCFG_ADDR)
        f.write(data) 


    if not os.path.isfile(boardcfgfile):
        print("ERROR: %s is not a valid file." % (boardcfgfile))
    else: 
        print("write %s ." % (boardcfgfile))  
        b=open(boardcfgfile,"rb")
        data = b.read(CFGFILESIZE)
        b.close()
        f.seek(BOARDCFG_ADDR)
        f.write(data)

    f.seek(APPTIME_ADDR)
    f.write(struct.pack("i", 0x66556655))  
    f.write(struct.pack("6B", 0x00,thislocal.tm_min,thislocal.tm_hour,thislocal.tm_mday,thislocal.tm_mon,thislocal.tm_year-1900))
    print("arg "+val)
    if  val=='1':  
	f.seek(UCLEAR_ADDR)
	f.write(struct.pack("i", SIG_UPDATE_CLEAR))  
	f.write(struct.pack("i", SIG_NEEDUBOOTUSB))  
	f.write(struct.pack("i", NEEDUBOOTUSB_CNT))  
	 	
        f.seek(NAVICOPY_FLAG)
        f.write("needcopynavi")  

    f.close()
    os.remove('../'+partitionfile)
    shutil.move(partitionfile,'../')
    return

#SystemUI Settings comiple to 	/oem/priv-app/
#ResHolder copy to 		/oem/res/
#config.txt copy to 		/oem/app/
#all other fiel comipile to 	/oem/app/
#auto_generator.py src target
#python auto_generator.py ./ preinstall
def app1(argv):
    unpackApp()
    lsecconf(0)
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
	                includefile.write('PRODUCT_COPY_FILES +=$(CUR_PATH)/syu/product/preinstall/%s:oem/app/%s \n' % (filename, filename))
            break
        includefile.close()


def app2(argv):
    os.system('rm -rf preinstall')
    os.system('mkdir preinstall')
    os.system('unzip -q -P 048a02243bb74474b25233bda3cd02f8 AllAppUpdate.bin -d preinstall')
    os.system('cp config.txt preinstall/')
    lsecconf('1')
    preinstall_dir = os.path.join(argv[1],argv[2])
    if os.path.exists(preinstall_dir):
        #Use to include modules
        include_path = preinstall_dir + '/preinstall.mk'
        android_path = preinstall_dir + '/Android.mk'

        if os.path.exists(include_path):
            os.remove(include_path)
        if os.path.exists(android_path):
            os.remove(android_path)

        includefile = file(include_path, 'w')
        androidfile = file(android_path, 'w')
	#top andoid.mk
        androidfile.write("include $(call all-subdir-makefiles)\n\n")
	androidfile.close()

	#app file
	appdir=preinstall_dir+'/app'
	appmkfile = file(appdir+'/Android.mk', 'w')
	appmkfile.write("include $(call all-subdir-makefiles)\n\n")
	appmkfile.close()
        for root, dirs, files in os.walk(appdir):
	    for fn in files:
		if fn!='Android.mk' and fn!='preinstall.mk':
		  includefile.write('PRODUCT_COPY_FILES +=$(CUR_PATH)/syu/product/preinstall/app/%s:oem/app/%s \n' % (fn , fn))
            for filename in dirs:
		if filename =='RKUpdateService':
			continue
                apk = appdir+'/'+filename+'/'+filename+'.apk'
		libsrc = ''
                if os.path.exists(apk):
		    print(apk)
		    #rename systemui settings launcher3
		    if filename=='SystemUI' or filename=='Settings' or filename=='Launcher3':
			shutil.move(apk,appdir+'/'+filename+'/'+filename+'1.apk')
			shutil.move(appdir+'/'+filename,appdir+'/'+filename+'1')
			filename +='1'
		    makefile_path = appdir+'/'+filename + '/Android.mk'
		    makefile = file(makefile_path,'w')
		    #find lib
                    if os.path.exists(filename+'/lib'):
			libsrc=filename+'/lib'
		    if filename=='ResHolder':
			makefile.write(copy_res_templet % (filename))
		    else:
			makefile.write(templet1 % (filename,'app',libsrc))
                    makefile.close()
		    includefile.write('PRODUCT_PACKAGES += %s \n' % (filename))
            break

	#priv file.systemui setting
	privdir = preinstall_dir+'/priv-app'
	privmkfile = file(privdir+'/Android.mk', 'w')
	privmkfile.write("include $(call all-subdir-makefiles)\n\n")
	privmkfile.close()
	for root, dirs,files in os.walk(privdir):
	    for filename in dirs:
		apk = privdir+'/'+filename+'/'+filename+'.apk'
		libsrc = ''
		if os.path.exists(apk):
		   print(apk)
		   #rename systemui settings launcher3
		   if filename=='SystemUI' or filename=='Settings' or filename=='Launcher3':
			shutil.move(apk,privdir+'/'+filename+'/'+filename+'1.apk')
			shutil.move(privdir+'/'+filename,privdir+'/'+filename+'1')
			filename +='1'
		   makefile_path = privdir+'/'+filename + '/Android.mk'
		   makefile = file(makefile_path,'w')
		   makefile.write(templet1 % (filename,'priv-app',libsrc))
		   makefile.close()
		   includefile.write('PRODUCT_PACKAGES += %s \n' % (filename))
	    break
	#vital file
	vitaldir = preinstall_dir+'/vital-app'
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
			makefile.write(copy_app_templet % (found.group(), 'vital-app', 'vital-app'))			
			makefile.close()
			shutil.move(apk,include_apk_path)
			includefile.write('PRODUCT_PACKAGES += %s \n' % (found.group()))
            break

	#config file
        for root, dirs,files in os.walk(preinstall_dir):
            for filename in files:
		print(filename)
		if filename!='Android.mk' and filename!='preinstall.mk':
	                includefile.write('PRODUCT_COPY_FILES +=$(CUR_PATH)/syu/product/preinstall/%s:oem/app/%s \n' % (filename, filename))
            break
        includefile.close()

def app3(argv):
    os.system('rm -rf preinstall')
    os.system('mkdir preinstall')
    os.system('unzip -q -P 048a02243bb74474b25233bda3cd02f8 AllAppUpdate.bin -d preinstall')
    os.system('cp config.txt preinstall/')
    lsecconf('1')
    preinstall_dir = os.path.join(argv[1],argv[2])
    if os.path.exists(preinstall_dir):
        #Use to include modules
        include_path = preinstall_dir + '/preinstall.mk'

        if os.path.exists(include_path):
            os.remove(include_path)

        includefile = file(include_path, 'w')

	#config file
        for root, dirs,files in os.walk(preinstall_dir):
            for filename in files:
		print(filename)
		if filename!='Android.mk' and filename!='preinstall.mk':
	                includefile.write('PRODUCT_COPY_FILES +=$(CUR_PATH)/syu/product/preinstall/%s:oem/app/%s \n' % (filename, filename))
            break
        includefile.close()

def main(argv):
    #app1(argv)
    #app2(argv)
    app3(argv)
if __name__=="__main__":
  main(sys.argv)
