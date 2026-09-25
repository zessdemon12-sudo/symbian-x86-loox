/*
 * Symbian-X86 LOOX OS - Central Repository (CenRep)
 * File: centralrepository.h
 */

#ifndef __CENTRALREPOSITORY_H__
#define __CENTRALREPOSITORY_H__

#include "e32base.h"
#include <string>
#include <map>

class CRepository : public CBase {
private:
    TUid iRepositoryUid;
    std::map<TUint32, std::string> iSettings;
    std::string iFilePath;
    void Load();
    void Save();
public:
    static CRepository* NewL(TUid aRepositoryUid);
    static CRepository* NewLC(TUid aRepositoryUid);
    virtual ~CRepository();

    TInt Get(TUint32 aKey, TInt& aValue);
    TInt Set(TUint32 aKey, TInt aValue);
    TInt Get(TUint32 aKey, TDes8& aValue);
    TInt Set(TUint32 aKey, const TDesC8& aValue);

    TInt Create(TUint32 aKey, TInt aValue);
    TInt Delete(TUint32 aKey);
};

#endif /* __CENTRALREPOSITORY_H__ */
