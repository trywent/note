package com.android.server;

import com.syu.ipc.FinalBsp;
import com.syu.ipc.IRemoteToolkit;
import com.syu.ipc.IRemoteModule;
import com.syu.ipc.RemoteModuleBsp;
import com.syu.ipc.DataSyu;
import com.syu.ipc.ModuleCallbackList;
import com.syu.ipc.FinalBsp;

import android.os.RemoteException;

import android.annotation.SdkConstant;
import android.annotation.SdkConstant.SdkConstantType;
import android.content.Context;
import android.net.DhcpInfo;
import android.os.Binder;
import android.os.IBinder;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.os.RemoteException;
import android.os.WorkSource;
import android.os.Messenger;
import android.os.SystemProperties;
import android.util.SparseArray;
import android.util.Log;
import com.android.internal.util.AsyncChannel;
import com.android.internal.util.Protocol;
import android.os.RemoteCallbackList;
import java.util.List;
import android.media.IAudioService;
import com.android.server.audio.AudioService;
import android.os.ServiceManager;

import android.os.HandlerThread;
import android.view.IWindowManager; //for inputEvent
import android.view.InputChannel;
import android.view.InputEventReceiver;
import android.view.WindowManagerImpl;
import android.view.WindowManagerPolicy;
import android.view.WindowManagerPolicy.WindowManagerFuncs;
import android.view.WindowManagerPolicy.PointerEventListener;
import android.view.MotionEvent;
import android.view.InputEvent;
import android.os.Process;

import java.io.FileInputStream;

public class RemoteToolkitBsp extends IRemoteToolkit.Stub {

    private Context mContext;
    private static IAudioService sService;
    private static final String TAG = "RemoteToolkitBsp";
    // private native void native_start();

    WindowManagerFuncs mWM; 

    private static Handler mHandler;
    private PointerEventListener mReciver;

    static class SyuData {
        int[] mints;
        float[] mflts;
        String[] mstrs;
        public SyuData( int[] ints, float[] flts, String[] strs){
            mints = ints;
            mflts = flts;
            mstrs = strs;
        }
    }

    public RemoteToolkitBsp(Context context,WindowManagerFuncs m) {
        mContext = context;

        mWM = m;        
        createHandler();        
        monitorInput();
        //native_start();
    }

    private static IAudioService getService()
    {
        if (sService != null) {
            return sService;
        }
        IBinder b = ServiceManager.getService(Context.AUDIO_SERVICE);
        sService = IAudioService.Stub.asInterface(b);
        return sService;
    }

    @Override
    public IRemoteModule getRemoteModule(int moduleCode) throws RemoteException {
        Log.i("syu_service","-----ConstSyu.U_VOL_OPERATION----");
        switch (moduleCode) {
        case FinalBsp.MODULE_CODE_BSP: return RemoteModuleBsp.getInstance();
        }
        return null;
    }
    public int findnavi(String pidname){ 
        int res=0;
        String[] naviName = new String[]{"cld.navi.mobile.mainframe","title.navi","cld.navi.c2802.mainframe","com.navngo.igo.javaclient",
            "com.autonavi.xmgd.navigator", "com.autonavi.xmgd.navigator", "cn.com.tiros.android.navidog", "cn.com.tiros.android.navidog", 
            "cn.com.tiros.android.navidog4x", "com.mapbar.android.mapnavi", "com.mapbar.android.mapnavi", "com.pdager", "com.raxtone.flynavi",
            "com.uu.uunavi", "com.baidu.navi", "com.mapbar.android.mapbarmap", "cld.navi.c3280.mainframe","cld.navi","com.google.android.apps.maps",
        };
        for (String s : naviName) {
            if (pidname.startsWith(s)) {
                res = 1;
                break;
            }
        }
        if (res==0) {
            String prop_navi = SystemProperties.get("persist.sys.navi.packagename");
            String prop_navi1 = SystemProperties.get("sys.navi.packagename");
            if (pidname.equals(prop_navi)||pidname.equals(prop_navi1)) {
                res = 1;
            }
        }
        return res;
    }
    public int ismapapplication(int pid){
        String procPath = "/proc/"+pid+"/cmdline";
        String procName = null;
        try {

            FileInputStream is = new FileInputStream(procPath);
            byte[] mBuffer = new byte[256];
            int len = is.read(mBuffer);
            for (int i=0; i<len; i++) {
                if (mBuffer[i]==0) {
                    len = i;
                    break;
                }
            }
            is.close();
            procName = new String(mBuffer, 0, len);
            //  Log.e(TAG, ">>>>>>>>>>> calling pid name is " + procName);
        } catch (java.io.FileNotFoundException e) {
            Log.e(TAG, "ismapapplication FileNotFound!");
        } catch (java.io.IOException e) {
            Log.e(TAG, "ismapapplication IOException");
        }
        //if(procName.equals("com.basarsoft.igo.javaclient"))
        //              return 3;

        if (findnavi(procName)==1)
            return 1;
        String prop_navi = SystemProperties.get("persist.sys.navi.packagename");
        String prop_navi1 = SystemProperties.get("sys.navi.packagename");
        if (procName.equals(prop_navi)||procName.equals(prop_navi1)) {
            return 1;
        } else {
            return 0;
        }
    }

    public String procName(int pid){
        String procPath = "/proc/"+pid+"/cmdline";
        String procName = null;
        String prop_navi =null;
        try {

            FileInputStream is = new FileInputStream(procPath);
            byte[] mBuffer = new byte[256];
            int len = is.read(mBuffer);
            for (int i=0; i<len; i++) {
                if (mBuffer[i]==0) {
                    len = i;
                    break;
                }
            }
            is.close();
            procName = new String(mBuffer, 0, len);
        } catch (java.io.FileNotFoundException e) {
            Log.e(TAG, "procName FileNotFound!");
        } catch (java.io.IOException e) {
            Log.e(TAG, "procName IOException");
        }
        return procName;
    }


    public synchronized void sendToSyuServiceAudioInformation(int flag,  int[] intData,  float[] fltData,  String[] strData)
    {
		switch(flag) {
			case com.syu.ipc.FinalBsp.U_SET_VOL_STREAM:
			case com.syu.ipc.FinalBsp.U_AUDIO_STATUS:
			case com.syu.ipc.FinalBsp.U_BUTTON_EVENT:
			case com.syu.ipc.FinalBsp.U_BUTTON_FEEDBACK:
			case com.syu.ipc.FinalBsp.U_AUDIO_FOCUS:
				/*com.syu.ipc.ModuleCallbackList.update(
						com.syu.ipc.DataSyu.MCLS ,
                        flag,
                        intData, fltData, strData);*/
                            callClient(flag,intData, fltData, strData);
				break;
		}
    }
    public void notify(int stream,String state)
    {
        Log.i(TAG,"notify: "+stream +" "+state);
        //callClient(FinalBsp.U_AUDIO_STATUS, new int[]{stream}, null, new String[]{state});
    }

    void createHandler(){
        if (mHandler ==null) {
            HandlerThread mThread = new HandlerThread(TAG,Process.THREAD_PRIORITY_AUDIO);
            mThread.start();  
            mHandler = new Handler(mThread.getLooper()){
                public void handleMessage(Message msg){
                    int[] i = ((SyuData)msg.obj).mints;
                    float[] f = ((SyuData)msg.obj).mflts;
                    String[] s= ((SyuData)msg.obj).mstrs;

                    ModuleCallbackList.update(DataSyu.MCLS, msg.what, i,f,s);
                }
            };
        }
    }

    void monitorInput(){
        mReciver = new PointerEventListener(){
            public void onPointerEvent(MotionEvent event) {
                int action= 0;
                float mx= 0;
                float my= 0;
                int eventAction = event.getActionMasked();
                if (eventAction==MotionEvent.ACTION_DOWN||eventAction==MotionEvent.ACTION_UP||eventAction==MotionEvent.ACTION_CANCEL) {
                    action=eventAction==MotionEvent.ACTION_DOWN?0:1;
                    mx= ((MotionEvent)event).getRawX();
                    my= ((MotionEvent)event).getRawY();
                } else if (eventAction  == MotionEvent.ACTION_POINTER_DOWN||eventAction  == MotionEvent.ACTION_POINTER_UP) {

                    action=eventAction  == MotionEvent.ACTION_POINTER_DOWN?0:1;
                    int index = ((MotionEvent)event).getActionIndex();
                    mx= ((MotionEvent)event).getX(index);
                    my= ((MotionEvent)event).getY(index);
                } else {
                    return;
                }               

                //Log.i(TAG,"get a motion event"+"x:"+mx +" y:"+my+"action:"+action);
                callClient(FinalBsp.U_TOUCH_STATUS, new int[]{action}, new float[]{mx,my}, null);
                //last keyevent 236 . down 0  up1
            }
        };

        mWM.registerPointerEventListener(mReciver);
    }

    public static void callClient(int what,int[] ints, float[] flts, String[] strs){
        if (mHandler == null) {
            return;
        }
        Message msg = mHandler.obtainMessage(what,new SyuData(ints, flts, strs));
        mHandler.sendMessage(msg);
    }

    //call from native
    public void stateNotify(String state){
        DataSyu.vechile = state;
        callClient(FinalBsp.U_BACK_CAR, null, null, new String[]{state});
    }

}
