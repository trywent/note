#include "utils/CallStack.h"
extern "C" void dumping_callstack(void);
void dumping_callstack(void)
{
    android::CallStack cs("test");
}
