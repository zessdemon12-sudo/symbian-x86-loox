/*
 * Symbian-X86 LOOX OS - Active Objects and Cleanup Architecture
 * File: e32base.h
 */

#ifndef __E32BASE_H__
#define __E32BASE_H__

#include "e32def.h"
#include "e32des.h"
#include <stdlib.h>
#include <vector>
#include <exception>

/* Base class for all heap-allocated objects in Symbian */
class CBase {
public:
    inline CBase() {}
    virtual ~CBase() {}
    void* operator new(size_t aSize) {
        void* ptr = calloc(1, aSize); // Symbian zeroes all heap objects on allocation
        return ptr;
    }
    void operator delete(void* aPtr) {
        free(aPtr);
    }
};

/* Symbian Leave Exception */
class XLeaveException : public std::exception {
public:
    TInt iReason;
    XLeaveException(TInt aReason) : iReason(aReason) {}
    virtual const char* what() const throw() { return "Symbian User::Leave"; }
};

class User {
public:
    static inline void Leave(TInt aReason) {
        throw XLeaveException(aReason);
    }
    static inline void LeaveIfError(TInt aError) {
        if (aError < 0) Leave(aError);
    }
    static inline void LeaveIfNull(const void* aPtr) {
        if (!aPtr) Leave(KErrNoMemory);
    }
    static void After(TInt aMicroSeconds);
};

/* Cleanup Stack for Leave-Safe Exception Handling */
class CleanupStack {
private:
    static std::vector<TAny*>& GetStack();
public:
    static void PushL(TAny* aPtr);
    static void Pop();
    static void Pop(TInt aCount);
    static void PopAndDestroy();
    static void PopAndDestroy(TInt aCount);
};

#define TRAP(r, statements) \
    try { statements; r = KErrNone; } \
    catch (const XLeaveException& e) { r = e.iReason; } \
    catch (...) { r = KErrGeneral; }

#define TRAPD(r, statements) \
    TInt r = KErrNone; \
    TRAP(r, statements)

/* Request Status for Asynchronous Operations */
class TRequestStatus {
private:
    TInt iStatus;
public:
    inline TRequestStatus() : iStatus(KErrNone) {}
    inline TRequestStatus(TInt aVal) : iStatus(aVal) {}
    inline TInt Int() const { return iStatus; }
    inline void Set(TInt aVal) { iStatus = aVal; }
    inline bool operator==(TInt aVal) const { return iStatus == aVal; }
    inline bool operator!=(TInt aVal) const { return iStatus != aVal; }
};

/* Active Object Base Class */
class CActive : public CBase {
public:
    enum TPriority {
        EPriorityIdle = -100,
        EPriorityLow = -20,
        EPriorityStandard = 0,
        EPriorityUserInput = 10,
        EPriorityHigh = 20
    };
public:
    TRequestStatus iStatus;
protected:
    TPriority iPriority;
    TBool iActive;
public:
    CActive(TPriority aPriority = EPriorityStandard);
    virtual ~CActive();
    
    inline TBool IsActive() const { return iActive; }
    void SetActive();
    void Cancel();

    virtual void RunL() = 0;
    virtual void DoCancel() = 0;
    virtual TInt RunError(TInt aError) { return aError; }
    
    inline TPriority Priority() const { return iPriority; }
};

/* Active Scheduler Event Dispatcher */
class CActiveScheduler : public CBase {
private:
    std::vector<CActive*> iActiveObjects;
    TBool iRunning;
    static CActiveScheduler* iCurrent;
public:
    CActiveScheduler();
    virtual ~CActiveScheduler();

    static void Install(CActiveScheduler* aScheduler);
    static CActiveScheduler* Current();

    static void Add(CActive* aActiveObject);
    static void Remove(CActive* aActiveObject);
    static void Start();
    static void Stop();

    void RunOneStep();
};

#endif /* __E32BASE_H__ */
