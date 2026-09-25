/*
 * Symbian-X86 LOOX OS - Descriptor Hierarchy
 * File: e32des.h
 */

#ifndef __E32DES_H__
#define __E32DES_H__

#include "e32def.h"
#include <string.h>

class TDesC8 {
protected:
    const TUint8* iPtr;
    TInt iLength;
public:
    inline TDesC8(const TUint8* aPtr, TInt aLength) : iPtr(aPtr), iLength(aLength) {}
    inline TInt Length() const { return iLength; }
    inline const TUint8* Ptr() const { return iPtr; }
    inline TUint8 operator[](TInt aIndex) const { return iPtr[aIndex]; }
    inline TInt Compare(const TDesC8& aDes) const {
        TInt minLen = iLength < aDes.iLength ? iLength : aDes.iLength;
        int res = memcmp(iPtr, aDes.iPtr, minLen);
        if (res != 0) return res;
        return iLength - aDes.iLength;
    }
};

class TDes8 : public TDesC8 {
protected:
    TInt iMaxLength;
public:
    inline TDes8(TUint8* aPtr, TInt aLength, TInt aMaxLength) 
        : TDesC8(aPtr, aLength), iMaxLength(aMaxLength) {}
    inline TInt MaxLength() const { return iMaxLength; }
    inline void Zero() { iLength = 0; }
    inline void SetLength(TInt aLength) { if (aLength <= iMaxLength) iLength = aLength; }
    inline void Copy(const TDesC8& aDes) {
        TInt copyLen = aDes.Length() < iMaxLength ? aDes.Length() : iMaxLength;
        memcpy((void*)iPtr, aDes.Ptr(), copyLen);
        iLength = copyLen;
    }
    inline void Append(const TDesC8& aDes) {
        TInt rem = iMaxLength - iLength;
        TInt copyLen = aDes.Length() < rem ? aDes.Length() : rem;
        memcpy((void*)(iPtr + iLength), aDes.Ptr(), copyLen);
        iLength += copyLen;
    }
};

class TPtrC8 : public TDesC8 {
public:
    inline TPtrC8() : TDesC8(NULL, 0) {}
    inline TPtrC8(const TUint8* aPtr, TInt aLength) : TDesC8(aPtr, aLength) {}
    inline TPtrC8(const char* aStr) : TDesC8((const TUint8*)aStr, aStr ? (TInt)strlen(aStr) : 0) {}
};

template <TInt S>
class TBuf8 : public TDes8 {
private:
    TUint8 iBuffer[S];
public:
    inline TBuf8() : TDes8(iBuffer, 0, S) {}
    inline TBuf8(const TDesC8& aDes) : TDes8(iBuffer, 0, S) { Copy(aDes); }
};

#define _L8(a) TPtrC8(a)
#define _L(a)  TPtrC8(a)

#endif /* __E32DES_H__ */
