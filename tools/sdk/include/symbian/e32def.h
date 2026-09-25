/*
 * Symbian-X86 LOOX OS - Core Definitions
 * File: e32def.h
 */

#ifndef __E32DEF_H__
#define __E32DEF_H__

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Basic Primitive Types */
typedef int32_t         TInt;
typedef uint32_t        TUint;
typedef int8_t          TInt8;
typedef uint8_t         TUint8;
typedef int16_t         TInt16;
typedef uint16_t        TUint16;
typedef int32_t         TInt32;
typedef uint32_t        TUint32;
typedef int64_t         TInt64;
typedef uint64_t        TUint64;
typedef double          TReal64;
typedef float           TReal32;
typedef TReal64         TReal;
typedef int32_t         TBool;
typedef void            TAny;
typedef uint16_t        TChar;

#ifndef TRUE
#define TRUE  1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define ETrue  1
#define EFalse 0

/* Symbian Error Codes */
#define KErrNone                0
#define KErrNotFound          (-1)
#define KErrGeneral           (-2)
#define KErrCancel            (-3)
#define KErrNoMemory          (-4)
#define KErrNotSupported      (-5)
#define KErrArgument          (-6)
#define KErrTotalLossOfPrecision (-7)
#define KErrBadHandle         (-8)
#define KErrOverflow          (-9)
#define KErrUnderflow         (-10)
#define KErrAlreadyExists     (-11)
#define KErrPathNotFound      (-12)
#define KErrDied              (-13)
#define KErrInUse             (-14)
#define KErrServerTerminated  (-15)
#define KErrServerBusy        (-16)
#define KErrCompletion        (-17)
#define KErrNotReady          (-18)
#define KErrUnknown           (-19)
#define KErrCorrupt           (-20)
#define KErrAccessDenied      (-21)
#define KErrLocked            (-22)
#define KErrWrite             (-23)
#define KErrDisMounted        (-24)
#define KErrEof               (-25)
#define KErrDiskFull          (-26)
#define KErrBadDriver         (-27)
#define KErrBadName           (-28)
#define KErrCommsLineFail     (-29)
#define KErrCommsFrame        (-30)
#define KErrCommsOverrun      (-31)
#define KErrCommsParity       (-32)
#define KErrTimedOut          (-33)
#define KErrPermissionDenied  (-46)

/* UID Type */
typedef struct TUid {
    TUint32 iUid;
#ifdef __cplusplus
    inline bool operator==(const TUid& aOther) const { return iUid == aOther.iUid; }
    inline bool operator!=(const TUid& aOther) const { return iUid != aOther.iUid; }
#endif
} TUid;

#define KNullUid (TUid{0})

#define IMPORT_C
#define EXPORT_C
#define GLDEF_C
#define GLREF_C

#ifdef __cplusplus
}
#endif

#endif /* __E32DEF_H__ */
