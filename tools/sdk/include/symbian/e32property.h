/*
 * Symbian-X86 LOOX OS - Publish and Subscribe (RProperty)
 * File: e32property.h
 */

#ifndef __E32PROPERTY_H__
#define __E32PROPERTY_H__

#include "e32def.h"
#include "e32des.h"

#define KUidSystemCategoryValue  0x101F75B6
#define KUidNetworkCategoryValue 0x101F75B7

class RProperty {
public:
    enum TType {
        EInt,
        EByteArray,
        EText
    };
public:
    static TInt Define(TUid aCategory, TUint aKey, TInt aAttr);
    static TInt Delete(TUid aCategory, TUint aKey);
    static TInt Get(TUid aCategory, TUint aKey, TInt& aValue);
    static TInt Set(TUid aCategory, TUint aKey, TInt aValue);
    static TInt Get(TUid aCategory, TUint aKey, TDes8& aValue);
    static TInt Set(TUid aCategory, TUint aKey, const TDesC8& aValue);
};

#endif /* __E32PROPERTY_H__ */
