
package com.custom;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.os.HandlerThread;
import android.os.Process;
import android.os.Binder;
import android.os.IBinder;
import android.os.RemoteCallbackList;
import android.util.Log;

import android.content.Intent;
import android.app.NotificationManager;
import android.app.Notification;
import android.app.PendingIntent;
import android.os.ServiceManager;
import android.app.Service;

public class MyService extends IRemoteService.stub {

	public static final String TAG = "MYSERVICE";
        public static final int H_MESSGAE =1;

        private MyHandler mHandler;
        private RemoteCallbackList rcl;

	private class MyHandler extends Handler{
		MyHandler(Looper looper){
		 super(looper);
		}
		public void handleMessage(Message msg){
			switch(msg.what){
                        case 
                        }
		}
	}
        public MyService(Context context){
            HandlerThread mThread = new HandlerThread(TAG,Process.THREAD_PRIORITY_AUDIO);
            mThread.start();  
            mHandler = new MyHandler(mThread.getLooper());
        }
        public static void callClient(int what){
            if(mHandler == null) {
                return;
            }
            Message msg = mHandler.obtainMessage(what);
            mHandler.sendMessage(msg);
        }

	void inputEvent(){

		
		IBinder b = ServiceManager.getService("syu");
		IRemote service = IRemote.Stub.asInterface(b);

		try{
		service.monitorInput("mymonitor",mInput);
		}catch(android.os.RemoteException e){}		
		

		mReceiver = new MyInputEventReceiver(mInput,Looper.myLooper());
		(new Thread(){
			public void run(){
				int i=0;
				for(;;){
					Log.i("MYSERVICE-","X:"+mx+" Y:"+my);
					try{
					sleep(200);
					}catch(java.lang.InterruptedException e){}
				}
			}
		}).start();
	}
}
