
package com.android.server.am;

import com.android.server.am.ActivityManagerService;
import static android.os.Process.*;
import android.os.Process;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.os.Message;
import android.util.Slog;

import java.util.ArrayList;


public class FytProcessMoniter{
    static final String TAG="FYTPROC";
    static final int GETCPUINFO = 11;
    static final boolean DEBUG = true;
    static final int INTERVAL = 1000;
    static final int FYTLEVEL = 70;

    MyHandler mHandler;
    HandlerThread mThread;
    Looper mLooper;

    long mBaseUserTime;
    long mBaseSystemTime;
    long mBaseIoWaitTime;
    long mBaseIrqTime;
    long mBaseSoftIrqTime;
    long mBaseIdleTime;
    long[] sysCpu =new long[7];
    int count=0;

    ArrayList<ProcessRecord> lruProcess;
    ActivityManagerService am;

    private static final int[] SYSTEM_CPU_FORMAT = new int[] {
        PROC_SPACE_TERM|PROC_COMBINE,
        PROC_SPACE_TERM|PROC_OUT_LONG,                  // 1: user time
        PROC_SPACE_TERM|PROC_OUT_LONG,                  // 2: nice time
        PROC_SPACE_TERM|PROC_OUT_LONG,                  // 3: sys time
        PROC_SPACE_TERM|PROC_OUT_LONG,                  // 4: idle time
        PROC_SPACE_TERM|PROC_OUT_LONG,                  // 5: iowait time
        PROC_SPACE_TERM|PROC_OUT_LONG,                  // 6: irq time
        PROC_SPACE_TERM|PROC_OUT_LONG                   // 7: softirq time
    };
    public FytProcessMoniter(ActivityManagerService ams) {
        am = ams;
        lruProcess = am.mLruProcesses;
        mThread = new HandlerThread("fytmoniter");
        mThread.start();
        mLooper = mThread.getLooper();
        mHandler = new MyHandler(mLooper);
        mHandler.schedule();
    }

    class MyHandler extends Handler{
        MyHandler(Looper looper){
            super(looper);
        }
        public void handleMessage(Message msg){
            if(msg.what==GETCPUINFO) {
                if(highCPUusage(FYTLEVEL)) {
                    count++;
                }else{
                    count=0;
                }
                if(count>9) {
                    findAndkill();
                    count =0;
                }
                schedule();
            }
        }

        public void schedule(){
            sendEmptyMessageDelayed(GETCPUINFO,INTERVAL);
        }
    }

    boolean highCPUusage(float level){

        if (Process.readProcFile("/proc/stat", SYSTEM_CPU_FORMAT,null, sysCpu, null)) {
            // Total user time is user + nice time.
            final long usertime = sysCpu[0]+sysCpu[1];
            // Total system time is simply system time.
            final long systemtime = sysCpu[2];
            // Total idle time is simply idle time.
            final long idletime = sysCpu[3];
            // Total irq time is iowait + irq + softirq time.
            final long iowaittime = sysCpu[4];
            final long irqtime = sysCpu[5];
            final long softirqtime = sysCpu[6];

            int mRelUserTime = (int)(usertime - mBaseUserTime);
            int mRelSystemTime = (int)(systemtime - mBaseSystemTime);
            int mRelIoWaitTime = (int)(iowaittime - mBaseIoWaitTime);
            int mRelIrqTime = (int)(irqtime - mBaseIrqTime);
            int mRelSoftIrqTime = (int)(softirqtime - mBaseSoftIrqTime);
            int mRelIdleTime = (int)(idletime - mBaseIdleTime);


            mBaseUserTime = usertime;
            mBaseSystemTime = systemtime;
            mBaseIoWaitTime = iowaittime;
            mBaseIrqTime = irqtime;
            mBaseSoftIrqTime = softirqtime;
            mBaseIdleTime = idletime;

            int total= mRelUserTime+mRelSystemTime+mRelIoWaitTime+mRelIrqTime+mRelSoftIrqTime+mRelIdleTime;
            float ratio = ((mRelUserTime+mRelSystemTime+mRelIoWaitTime+mRelIrqTime+mRelSoftIrqTime)*100)/total;
            if(DEBUG) {
               Slog.i(TAG,"cpu percent "+ratio);
            }
            return ratio > level;
        }
        return false;
    }
    void findAndkill(){
        ActivityRecord top = am.fytresumedAppLocked();
        ProcessRecord topApp = top!=null?top.app:null;
        lruProcess = new ArrayList<ProcessRecord>(am.mLruProcesses);
        int N = lruProcess.size();

        if(DEBUG) {
            Slog.i(TAG,"top activity "+top+"lruproces size "+N);
        }
        for(int i=0;i<N;i++) {
            ProcessRecord pr = lruProcess.get(i);
            if(pr!=topApp&&pr.setAdj>ProcessList.VISIBLE_APP_ADJ) {
                pr.kill("just kill",true);
            }
        }
    }
}
