
/*
 * Copyright (C) 2008 The Android Open Source Project
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

#ifndef ANDROID_MYSERVICE_H_
#define ANDROID_MYSERVICE_H_

#include <stdint.h>
#include <sys/types.h>
#include <utils/Errors.h>
#include <utils/Mutex.h>
#include <utils/RefBase.h>
#include <binder/IInterface.h>
#include <binder/IMemory.h>
#include <utils/String8.h>
#include <binder/Parcel.h>

namespace android {

class String8;

class IMyService : public IInterface {
public:
   DECLARE_META_INTERFACE(MyService);
   virtual void notify(int streamtype, const String16& state) = 0;
};

class MyService
{
public:
    static const sp<IMyService> get_service();
    static void notify(void);
    static Mutex gLock;      // protects gAudioFlinger and gAudioErrorCallback,
    static sp<IMyService> myService;
};  
};// namespace android
#endif  /*ANDROID_MYSERVICE_H_*/
