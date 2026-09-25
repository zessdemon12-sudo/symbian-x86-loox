/*
 * Symbian-X86 LOOX OS - Core Runtime Implementation
 * File: e32base.cpp
 */

#include "e32base.h"
#include "e32property.h"
#include "centralrepository.h"

#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <fstream>
#include <sstream>
#include <iostream>

/* ----------------- User Implementations ----------------- */
void User::After(TInt aMicroSeconds) {
    if (aMicroSeconds > 0) {
        usleep(aMicroSeconds);
    }
}

/* ------------- CleanupStack Implementations ------------- */
static std::vector<TAny*> gCleanupStack;

std::vector<TAny*>& CleanupStack::GetStack() {
    return gCleanupStack;
}

void CleanupStack::PushL(TAny* aPtr) {
    if (!aPtr) User::Leave(KErrNoMemory);
    GetStack().push_back(aPtr);
}

void CleanupStack::Pop() {
    if (!GetStack().empty()) {
        GetStack().pop_back();
    }
}

void CleanupStack::Pop(TInt aCount) {
    while (aCount-- > 0 && !GetStack().empty()) {
        GetStack().pop_back();
    }
}

void CleanupStack::PopAndDestroy() {
    if (!GetStack().empty()) {
        TAny* ptr = GetStack().back();
        GetStack().pop_back();
        CBase* obj = static_cast<CBase*>(ptr);
        delete obj;
    }
}

void CleanupStack::PopAndDestroy(TInt aCount) {
    while (aCount-- > 0 && !GetStack().empty()) {
        PopAndDestroy();
    }
}

/* ---------------- CActive Implementations --------------- */
CActive::CActive(TPriority aPriority) 
    : iStatus(KErrNone), iPriority(aPriority), iActive(EFalse) {
}

CActive::~CActive() {
    Cancel();
}

void CActive::SetActive() {
    iActive = ETrue;
}

void CActive::Cancel() {
    if (iActive) {
        DoCancel();
        iActive = EFalse;
        iStatus.Set(KErrCancel);
    }
}

/* ----------- CActiveScheduler Implementations ----------- */
CActiveScheduler* CActiveScheduler::iCurrent = NULL;

CActiveScheduler::CActiveScheduler() : iRunning(EFalse) {
}

CActiveScheduler::~CActiveScheduler() {
    if (iCurrent == this) {
        iCurrent = NULL;
    }
}

void CActiveScheduler::Install(CActiveScheduler* aScheduler) {
    iCurrent = aScheduler;
}

CActiveScheduler* CActiveScheduler::Current() {
    return iCurrent;
}

void CActiveScheduler::Add(CActive* aActiveObject) {
    if (iCurrent && aActiveObject) {
        iCurrent->iActiveObjects.push_back(aActiveObject);
    }
}

void CActiveScheduler::Remove(CActive* aActiveObject) {
    if (!iCurrent || !aActiveObject) return;
    for (size_t i = 0; i < iCurrent->iActiveObjects.size(); ++i) {
        if (iCurrent->iActiveObjects[i] == aActiveObject) {
            iCurrent->iActiveObjects.erase(iCurrent->iActiveObjects.begin() + i);
            break;
        }
    }
}

void CActiveScheduler::RunOneStep() {
    CActive* highest = NULL;
    for (size_t i = 0; i < iActiveObjects.size(); ++i) {
        CActive* ao = iActiveObjects[i];
        if (ao->IsActive() && ao->iStatus.Int() != KRequestPending) {
            if (!highest || ao->Priority() > highest->Priority()) {
                highest = ao;
            }
        }
    }

    if (highest) {
        highest->Cancel();
        try {
            highest->RunL();
        } catch (const XLeaveException& e) {
            highest->RunError(e.iReason);
        } catch (...) {
            highest->RunError(KErrGeneral);
        }
    } else {
        usleep(1000); // 1ms sleep to conserve CPU on Intel Atom
    }
}

#define KRequestPending 0x80000000

void CActiveScheduler::Start() {
    if (!iCurrent) return;
    iCurrent->iRunning = ETrue;
    while (iCurrent->iRunning) {
        iCurrent->RunOneStep();
    }
}

void CActiveScheduler::Stop() {
    if (iCurrent) {
        iCurrent->iRunning = EFalse;
    }
}

/* ---------------- RProperty Implementations ------------ */
static std::map<uint64_t, std::string> gProperties;

static uint64_t MakePropKey(TUid aCategory, TUint aKey) {
    return ((uint64_t)aCategory.iUid << 32) | (uint64_t)aKey;
}

TInt RProperty::Define(TUid aCategory, TUint aKey, TInt /*aAttr*/) {
    uint64_t k = MakePropKey(aCategory, aKey);
    gProperties[k] = "0";
    return KErrNone;
}

TInt RProperty::Delete(TUid aCategory, TUint aKey) {
    uint64_t k = MakePropKey(aCategory, aKey);
    gProperties.erase(k);
    return KErrNone;
}

TInt RProperty::Get(TUid aCategory, TUint aKey, TInt& aValue) {
    uint64_t k = MakePropKey(aCategory, aKey);
    if (gProperties.find(k) == gProperties.end()) return KErrNotFound;
    aValue = atoi(gProperties[k].c_str());
    return KErrNone;
}

TInt RProperty::Set(TUid aCategory, TUint aKey, TInt aValue) {
    uint64_t k = MakePropKey(aCategory, aKey);
    char buf[32];
    snprintf(buf, sizeof(buf), "%d", aValue);
    gProperties[k] = buf;
    return KErrNone;
}

TInt RProperty::Get(TUid aCategory, TUint aKey, TDes8& aValue) {
    uint64_t k = MakePropKey(aCategory, aKey);
    if (gProperties.find(k) == gProperties.end()) return KErrNotFound;
    std::string val = gProperties[k];
    TPtrC8 src((const TUint8*)val.c_str(), val.length());
    aValue.Copy(src);
    return KErrNone;
}

TInt RProperty::Set(TUid aCategory, TUint aKey, const TDesC8& aValue) {
    uint64_t k = MakePropKey(aCategory, aKey);
    std::string val((const char*)aValue.Ptr(), aValue.Length());
    gProperties[k] = val;
    return KErrNone;
}

/* ------------ CRepository (CenRep) Implementation -------- */
CRepository* CRepository::NewL(TUid aRepositoryUid) {
    CRepository* self = new CRepository();
    User::LeaveIfNull(self);
    self->iRepositoryUid = aRepositoryUid;
    
    // Default directory in Symbian hierarchy
    char path[256];
    snprintf(path, sizeof(path), "/tmp/symbian_cenrep_0x%08X.cre", aRepositoryUid.iUid);
    self->iFilePath = path;
    self->Load();
    return self;
}

CRepository* CRepository::NewLC(TUid aRepositoryUid) {
    CRepository* self = NewL(aRepositoryUid);
    CleanupStack::PushL(self);
    return self;
}

CRepository::~CRepository() {
    Save();
}

void CRepository::Load() {
    std::ifstream file(iFilePath.c_str());
    if (!file.is_open()) return;
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        uint32_t key;
        std::string val;
        if (iss >> std::hex >> key >> val) {
            iSettings[key] = val;
        }
    }
}

void CRepository::Save() {
    std::ofstream file(iFilePath.c_str());
    if (!file.is_open()) return;
    for (std::map<TUint32, std::string>::iterator it = iSettings.begin(); it != iSettings.end(); ++it) {
        file << "0x" << std::hex << it->first << " " << it->second << "\n";
    }
}

TInt CRepository::Get(TUint32 aKey, TInt& aValue) {
    if (iSettings.find(aKey) == iSettings.end()) return KErrNotFound;
    aValue = atoi(iSettings[aKey].c_str());
    return KErrNone;
}

TInt CRepository::Set(TUint32 aKey, TInt aValue) {
    char buf[32];
    snprintf(buf, sizeof(buf), "%d", aValue);
    iSettings[aKey] = buf;
    Save();
    return KErrNone;
}

TInt CRepository::Get(TUint32 aKey, TDes8& aValue) {
    if (iSettings.find(aKey) == iSettings.end()) return KErrNotFound;
    std::string val = iSettings[aKey];
    TPtrC8 src((const TUint8*)val.c_str(), val.length());
    aValue.Copy(src);
    return KErrNone;
}

TInt CRepository::Set(TUint32 aKey, const TDesC8& aValue) {
    std::string val((const char*)aValue.Ptr(), aValue.Length());
    iSettings[aKey] = val;
    Save();
    return KErrNone;
}

TInt CRepository::Create(TUint32 aKey, TInt aValue) {
    return Set(aKey, aValue);
}

TInt CRepository::Delete(TUint32 aKey) {
    if (iSettings.find(aKey) == iSettings.end()) return KErrNotFound;
    iSettings.erase(aKey);
    Save();
    return KErrNone;
}
