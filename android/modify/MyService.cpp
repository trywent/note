
/*
 * Copyright (C) 2006-2007 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#define LOG_TAG "myservice"
//#define LOG_NDEBUG 0

#include <utils/Log.h>
#include <utils/RefBase.h>
#include <binder/IServiceManager.h>
#include <binder/ProcessState.h>
#include "MyService.h"
// ----------------------------------------------------------------------------

namespace android {

enum {
   GET_REMOTE = IBinder::FIRST_CALL_TRANSACTION,
   IS_MAP,
   PROC_NAME,
   SEND_TO,
   NOTIFY,
};


class BpMyService : public BpInterface<IMyService> {
public:
   explicit BpMyService(const sp<IBinder>& impl)
      : BpInterface<IMyService>(impl) {
   }

   virtual void notify(int streamtype, const String16& state) {
      Parcel data, reply;
      data.writeInterfaceToken(IMyService::getInterfaceDescriptor());
      data.writeInt32(streamtype);
      data.writeString16(state);
      remote()->transact(NOTIFY, data, &reply);
      //ALOGI("____notify____");
      //return reply.readInt32();
   }

};
//implement asInterface (return a new Bpxxxx()) and getInterfaceDescriptor
IMPLEMENT_META_INTERFACE(MyService, "com.syu.ipc.IRemoteToolkit");


Mutex MyService::gLock;
sp<IMyService> MyService::myService;


const sp<IMyService> MyService::get_service() {
   sp<IMyService> service;
   {
      Mutex::Autolock _l(gLock);
      if (myService == 0) {
         sp<IServiceManager> sm = defaultServiceManager();
         sp<IBinder> binder;
         binder = sm->getService(String16("syu"));
         if (binder == 0) return NULL;
         //binder->linkToDeath(Client);
         myService = interface_cast<IMyService>(binder);
         service = myService;
      }
      service = myService;
   }
   return service;
}
void MyService::notify() {
   sp<IMyService> service = get_service();
   if (service != NULL) {
      //ALOGI("......notify.......");
      service->notify(1, String16("test"));
   }
}
} // namespace android
