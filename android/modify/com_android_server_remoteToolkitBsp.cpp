/*
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <utils/threads.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <asm/types.h>
#include <linux/netlink.h>
#include <linux/socket.h>*/

#define LOG_TAG "SYU"

#include "JNIHelp.h"
#include "jni.h"

#include <ScopedUtfChars.h>

#include <limits.h>

#include <android_runtime/AndroidRuntime.h>
#include <android_runtime/Log.h>
#include <utils/Timers.h>
#include <utils/misc.h>
#include <utils/String8.h>
#include <utils/Log.h>


#include <sys/socket.h>
//#include <sys/types.h>
#include <linux/netlink.h>
#include <string.h>
#define NETLINK_TEST 25
#define MAX_PAYLOAD 1024 // maximum payload size
/*
 * com_android_server_remoteToolkitBsp
 * 
 * 
 */


namespace android
{

class ListenThread:public Thread {
public:
    ListenThread();
    virtual ~ListenThread();

private:
    virtual bool threadLoop();
};

static struct {
    jmethodID stateNotify;
} gSyuServiceInfo;
static jobject gSyuServiceObj;

static bool checkAndClearExceptionFromCallback(JNIEnv* env, const char* methodName) {
    if (env->ExceptionCheck()) {
        ALOGE("An exception was thrown by callback '%s'.", methodName);
        LOGE_EX(env);
        env->ExceptionClear();
        return true;
    }
    return false;
}

void android_server_SyuService_start(JNIEnv* env, jobject obj){
   gSyuServiceObj = env->NewGlobalRef(obj);
   ListenThread* mThread = new ListenThread();
   mThread->run("vehicle_detect", ANDROID_PRIORITY_NORMAL);
}

void stateNotify(char *str){
         JNIEnv* env = AndroidRuntime::getJNIEnv();
        jstring state = env->NewStringUTF(str);
        env->CallVoidMethod(gSyuServiceObj, gSyuServiceInfo.stateNotify,state);
        env->DeleteLocalRef(state);
        checkAndClearExceptionFromCallback(env, "StateNotify");
}

static JNINativeMethod method_table[] = {
    { "native_start",                "()V",(void*)android_server_SyuService_start },
};
int register_android_server_SyuService(JNIEnv *env){
    int ret = jniRegisterNativeMethods(env, "com/android/server/RemoteToolkitBsp",method_table, NELEM(method_table));

    jclass clazz = env->FindClass("com/android/server/RemoteToolkitBsp");
    LOG_FATAL_IF(! var, "Unable to find class com/android/server/RemoteToolkitBsp");
    gSyuServiceInfo.stateNotify = env->GetMethodID(clazz, "stateNotify", "(Ljava/lang/String;)V"); 
    LOG_FATAL_IF(! var, "Unable to find method stateNotify");
    return ret;
}




ListenThread::ListenThread() : Thread(/*canCallJava*/ true) {
}

ListenThread::~ListenThread() {
}

bool ListenThread::threadLoop() {
    int state;
    struct sockaddr_nl src_addr, dest_addr;
    struct nlmsghdr *nlh = NULL;
    struct iovec iov;
    struct msghdr msg;
    int sock_fd, retval;
    int state_smg = 0;    
	
    // Create a socket

    sock_fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_TEST);
    if(sock_fd == -1){
        ALOGE("error getting socket: %s", strerror(errno));
        return -1;
    }

    // To prepare binding

    memset(&msg,0,sizeof(msg));
    memset(&src_addr, 0, sizeof(src_addr));
    src_addr.nl_family = AF_NETLINK;
    src_addr.nl_pid = getpid(); // self pid

    src_addr.nl_groups = 0; // multi cast


    retval = bind(sock_fd, (struct sockaddr*)&src_addr, sizeof(src_addr));
    if(retval < 0){
        ALOGE("bind failed: %s", strerror(errno));
        close(sock_fd);
        return -1;
    }

    // To prepare recvmsg

    nlh = (struct nlmsghdr *)malloc(NLMSG_SPACE(MAX_PAYLOAD));
    if(!nlh){
        ALOGE("malloc nlmsghdr error!\n");
        close(sock_fd);
        return -1;
    }

    memset(&dest_addr,0,sizeof(dest_addr));
    dest_addr.nl_family = AF_NETLINK;
    dest_addr.nl_pid = 0;
    dest_addr.nl_groups = 0;

    nlh->nlmsg_len = NLMSG_SPACE(MAX_PAYLOAD);
    nlh->nlmsg_pid = getpid();
    nlh->nlmsg_flags = 0;
    strcpy((char*)NLMSG_DATA(nlh),":---");

    iov.iov_base = (void *)nlh;
   iov.iov_len = NLMSG_SPACE(MAX_PAYLOAD);
    // iov.iov_len = nlh->nlmsg_len;

    memset(&msg, 0, sizeof(msg));
   
    msg.msg_name = (void *)&dest_addr;
    msg.msg_namelen = sizeof(dest_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    ALOGI("state_smg\n");
    state_smg = sendmsg(sock_fd,&msg,0);

    if(state_smg == -1)
    {
        ALOGE("get error sendmsg = %s\n",strerror(errno));
    }

    memset(nlh,0,NLMSG_SPACE(MAX_PAYLOAD));
    ALOGI("waiting received!\n");
    // Read message from kernel

    while(1){
        state = recvmsg(sock_fd, &msg, 0);
        if (state < 0) 
        {
            ALOGE("state<1");
        }
        stateNotify((char *) NLMSG_DATA(nlh));
        ALOGE("Received message: %s\n",(char *) NLMSG_DATA(nlh));
    }

    close(sock_fd);

    return 0;
}
};
