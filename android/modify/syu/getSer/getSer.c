#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int main(void){
	char * path="/sys/bus/mmc/devices/mmc1:0001/cid";
	int fd;
	unsigned char buf[33];
	int i;
	
	fd =open(path,O_RDONLY);
	if(fd<0){
		printf("open file failed.\n");
		return 1;
	}

	if(read(fd,buf,32)!=32){
		printf("read file failed.\n");
		close(fd);
		return 1;	
	}

	for(i=0;i<32;i++)
		printf("%c",buf[i]);

	printf("\n");
	close(fd);
	return 0;	
}
