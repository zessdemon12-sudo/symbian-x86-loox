/*
 * Symbian-X86 LOOX OS - Client-Server IPC Architecture
 * File: symbian_ipc.h
 */

#ifndef __SYMBIAN_IPC_H__
#define __SYMBIAN_IPC_H__

#include "../api/include/e32base.h"
#include <string>

class RMessage2 {
public:
    TInt iFunction;
    TInt iArgs[4];
    TInt iClientPid;
    TUint64 iClientCapabilities;
public:
    inline RMessage2() : iFunction(0), iClientPid(0), iClientCapabilities(0) {
        iArgs[0] = iArgs[1] = iArgs[2] = iArgs[3] = 0;
    }
    inline TInt Function() const { return iFunction; }
    inline TInt Int0() const { return iArgs[0]; }
    inline TInt Int1() const { return iArgs[1]; }
    inline TInt Int2() const { return iArgs[2]; }
    inline TInt Int3 = Int32();
    inline TInt Int32() const { return iArgs[3]; }
    
    inline TUint64 Capabilities() const { return iClientCapabilities; }
    inline TBool HasCapability(TUint64 aCap) const {
        return (iClientCapabilities & aCap) == aCap;
    }

    void Complete(TInt aReason);
};

class CSession2 : public CBase {
public:
    CSession2();
    virtual ~CSession2();
    virtual void ServiceL(const RMessage2& aMessage) = 0;
};

class CServer2 : public CActive {
private:
    std::string iServerName;
    int iListenSocketFd;
public:
    CServer2(TPriority aPriority = EPriorityStandard);
    virtual ~CServer2();

    void StartL(const TDesC8& aName);
    virtual CSession2* NewSessionL(const RMessage2& aMessage) = 0;

    virtual void RunL();
    virtual void DoCancel();
};

class RSessionBase {
protected:
    int iSocketFd;
public:
    RSessionBase();
    virtual ~RSessionBase();

    TInt CreateSession(const TDesC8& aServerName);
    void Close();

    TInt SendReceive(TInt aFunction, const TInt aArgs[4] = NULL);
    TInt Send(TInt aFunction, const TInt aArgs[4] = NULL);
};

#endif /* __SYMBIAN_IPC_H__ */
