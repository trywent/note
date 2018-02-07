#define LOG_TAG "mcu_cmd"

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <termios.h>
#include <cutils/properties.h>
#include <cutils/log.h>

static int mcu_cmd(void)
{
	int fd;
	struct termios opt;
	//const char TurnOnLCDCmd[10] =
	//       {0x88,0x55,0x00,0x03,0x01,0xaa,0x60,0x00^0x03^0x01^0xAA^0x60,0,0};
	const char updateCmd[10] =
	       {0x88,0x55,0x00,0x03,0x01,0xaa,0x56,0x00^0x03^0x01^0xAA^0x56,0,0};
	char platform[255]={0};
	char nextplatform[255]={0};
	property_get("sys.fyt.platform",platform, "");
	property_get("ro.fyt.platform",nextplatform, "");

	fd = open("/dev/ttyS2",O_WRONLY );//O_RDWR
	if(fd<0)
	{
		SLOGE("serial open fail ! \n");
		return -1;
		
	}
	tcgetattr(fd, &opt);
	
	SLOGI("send update info at 38400 \n");
	cfsetispeed(&opt, B38400);
	cfsetospeed(&opt, B38400);
	
	tcsetattr(fd, TCSANOW,&opt);
 	write(fd, updateCmd, 8); 
	close(fd);
	return 0;
}

int main(void){

	mcu_cmd();
	return 0;	
}
