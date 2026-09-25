/*
 * Symbian-X86 LOOX OS - Capability & Security Model
 * File: security_manager.h
 */

#ifndef __SECURITY_MANAGER_H__
#define __SECURITY_MANAGER_H__

#include "../api/include/e32def.h"
#include <string>
#include <vector>

/* Standard Symbian OS v9.x Capabilities */
enum TCapability {
    ECapabilityTCB               = 0,
    ECapabilityCommDD            = 1,
    ECapabilityPowerMgmt         = 2,
    ECapabilityMultimediaDD      = 3,
    ECapabilityReadDeviceData    = 4,
    ECapabilityWriteDeviceData   = 5,
    ECapabilityDRM               = 6,
    ECapabilityTrustedUI         = 7,
    ECapabilityProtServ          = 8,
    ECapabilityDiskAdmin         = 9,
    ECapabilityNetworkControl    = 10,
    ECapabilityAllFiles          = 11,
    ECapabilitySwEvent           = 12,
    ECapabilityNetworkServices   = 13,
    ECapabilityLocalServices     = 14,
    ECapabilityReadUserData      = 15,
    ECapabilityWriteUserData     = 16,
    ECapabilityLocation          = 17,
    ECapabilitySurroundingsDD    = 18,
    ECapabilityUserEnvironment   = 19
};

class TCapabilitySet {
private:
    TUint64 iCapabilities;
public:
    inline TCapabilitySet() : iCapabilities(0) {}
    inline TCapabilitySet(TUint64 aCaps) : iCapabilities(aCaps) {}

    inline void AddCapability(TCapability aCap) {
        iCapabilities |= (1ULL << aCap);
    }

    inline void RemoveCapability(TCapability aCap) {
        iCapabilities &= ~(1ULL << aCap);
    }

    inline TBool HasCapability(TCapability aCap) const {
        return (iCapabilities & (1ULL << aCap)) != 0;
    }

    inline TUint64 Value() const { return iCapabilities; }

    static TCapabilitySet FromStringList(const std::vector<std::string>& aCapNames);
    std::vector<std::string> ToStringList() const;
};

class SecurityManager {
public:
    static TBool CheckCapability(pid_t aPid, TCapability aRequiredCap);
    static TBool VerifyPrivatePathAccess(pid_t aPid, TUid aAppUid, const std::string& aPath);
    static void EnforceSandbox(TUid aAppUid);
};

#endif /* __SECURITY_MANAGER_H__ */
