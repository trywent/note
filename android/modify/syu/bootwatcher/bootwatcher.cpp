#define LOG_TAG "BootWatcher"
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <stdio.h>
#include <utils/Log.h>
#include <utils/SystemClock.h>
#include <utils/Timers.h>
#include <termios.h>

#define KLOG_LEVEL 6
#include <cutils/klog.h>
#include <string.h>


#define ERROR(x...)   KLOG_ERROR(LOG_TAG, x)
#define NOTICE(x...)  KLOG_NOTICE(LOG_TAG, x)
#define INFO(x...)    KLOG_INFO(LOG_TAG, x)



//#define ERROR(x...) log_write(3, "<3>init: " x)  
//#define NOTICE(x...) log_write(5, "<5>init: " x)  
//#define INFO(x...) log_write(6, "<6>init: " x)  
//#define LOG_DEFAULT_LEVEL 7 /* messages <= this level are logged */  



#include "cutils/properties.h"
#include "cutils/android_reboot.h"

//*TODO: adjust this macro to match various project
#define MAX_BOOT_TIME		160  //second

int factory_boot_flag_led(void)
{
	char property_string[PROPERTY_VALUE_MAX];
	int fd;
	char buf[10];
	property_get("persist.sys.factoryboot", property_string, "false");
	if(!strcmp(property_string, "true")) {
		property_set("persist.sys.factoryboot", "false");
		buf[0] = '0';
		buf[6]='e';    //'e'  allways on,  'f' allways off
		fd = open("/sys/fytver/boot_flags", O_RDWR, 666);
		if(fd>0)
		{
			 write(fd, buf, 8);
			 close(fd);
		}	
	}
	
	return 0;
}

static int mcu_cmd(void);
int main(int argc, char **argv) {
	char property_string[PROPERTY_VALUE_MAX];
	char property_string1[PROPERTY_VALUE_MAX];
	char property_string_first_booting[PROPERTY_VALUE_MAX];

	ALOGD("start...");

	sleep(20);
	
	
	while(1) {
		property_get("sys.boot_completed", property_string, "0");
		if(!strcmp(property_string, "1")) {
			ALOGD("boot completed!");

			factory_boot_flag_led();
			break;
		}

		//judge if boot time up to Max time
		nsecs_t boot_time = systemTime(SYSTEM_TIME_BOOTTIME);
		unsigned int boot_sec = boot_time/(1000*1000*1000);

		//fyt add
		//property_get("sys.boot_fyt_updating", property_string1, "false");
		property_get("persist.sys.first_update", property_string1, "false");
		property_get("persist.sys.first_booting", property_string_first_booting, "true");

		ALOGD("boot time is %d, first booting [%s]", boot_sec, property_string_first_booting);

		if(boot_sec > MAX_BOOT_TIME && !strcmp(property_string_first_booting, "false")
			&& !strcmp(property_string1, "false")) {
			//*TODO:write cmd to /cache/recovery/command
			/* cmd : 
			1. "--wipe_data" to  format userdata partition
			2. "--update_package=/mnt/usb_storage/update.zip" to trigger usb ota upgrade
			3. "--fyt_wipe" to delete userdata file*/
			int err = mkdir("/cache/recovery", S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);
			if (err < 0)
				ALOGD("mkdir /cache/recovery faild!");
			int fd = open("/cache/recovery/command", O_CREAT|O_RDWR, S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);
			if(fd < 0) {
				ALOGD("open /cache/recovery/command faild!");
			}else {
				char cmd[] = "--fyt_delete";//"--wipe_data";
				write(fd, cmd, sizeof(cmd));
				close(fd);
			}
			
			ALOGD("reboot to recovery now!!!");
			mcu_cmd();
			android_reboot(ANDROID_RB_RESTART2, 0, "recovery");
		}else {
			sleep(1);
		}
	}

	ALOGD("exit...");
	return 0;
}



static int mcu_cmd(void)
{
	int fd;
	struct termios opt;
	//const char TurnOnLCDCmd[10] =
	//       {0x88,0x55,0x00,0x03,0x01,0xaa,0x60,0x00^0x03^0x01^0xAA^0x60,0,0};
	const char updateCmd[10] =
	       {0x88,0x55,0x00,0x03,0x01,0xaa,0x56,0x00^0x03^0x01^0xAA^0x56,0,0};
	char platform[255]={0};
	char mcuType[255]={0};

	property_get("sys.fyt.platform",platform, "");
	property_get("ro.fyt.mcu_type",mcuType, "");

	fd = open("/dev/ttyS3",O_WRONLY );//O_RDWR
	if(fd<0)
	{
		ALOGE("serial open fail ! \n");
		return -1;
		
	}
	tcgetattr(fd, &opt);
	if(strncmp(platform,"2009",4)==0){
		SLOGI("send update info at 115200 \n");
		cfsetispeed(&opt, B115200);
		cfsetospeed(&opt, B115200);
	}else{
		if (strncmp(mcuType,"1",1)==0) {
                SLOGI("send update info at 115200 \n");
		cfsetispeed(&opt, B115200);
		cfsetospeed(&opt, B115200);
              }else{
                SLOGI("send update info at 38400 \n");
		cfsetispeed(&opt, B38400);
		cfsetospeed(&opt, B38400);
              }
	}
	tcsetattr(fd, TCSANOW,&opt);
 	write(fd, updateCmd, 8); 
	close(fd);
	return 0;
}

