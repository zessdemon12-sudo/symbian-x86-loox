/*
 * Symbian-X86 LOOX OS - Capability & Security Manager Implementation
 * File: security_manager.cpp
 */

#include "security_manager.h"
#include <map>
#include <sys/stat.h>
#include <unistd.h>

static struct {
    TCapability cap;
    const char* name;
} gCapNames[] = {
    { ECapabilityTCB, "TCB" },
    { ECapabilityCommDD, "CommDD" },
    { ECapabilityPowerMgmt, "PowerMgmt" },
    { ECapabilityMultimediaDD, "MultimediaDD" },
    { ECapabilityReadDeviceData, "ReadDeviceData" },
    { ECapabilityWriteDeviceData, "WriteDeviceData" },
    { ECapabilityDRM, "DRM" },
    { ECapabilityTrustedUI, "TrustedUI" },
    { ECapabilityProtServ, "ProtServ" },
    { ECapabilityDiskAdmin, "DiskAdmin" },
    { ECapabilityNetworkControl, "NetworkControl" },
    { ECapabilityAllFiles, "AllFiles" },
    { ECapabilitySwEvent, "SwEvent" },
    { ECapabilityNetworkServices, "NetworkServices" },
    { ECapabilityLocalServices, "LocalServices" },
    { ECapabilityReadUserData, "ReadUserData" },
    { ECapabilityWriteUserData, "WriteUserData" },
    { ECapabilityLocation, "Location" },
    { ECapabilitySurroundingsDD, "SurroundingsDD" },
    { ECapabilityUserEnvironment, "UserEnvironment" }
};

TCapabilitySet TCapabilitySet::FromStringList(const std::vector<std::string>& aCapNames) {
    TCapabilitySet set;
    for (size_t i = 0; i < aCapNames.size(); ++i) {
        for (size_t j = 0; j < sizeof(gCapNames) / sizeof(gCapNames[0]); ++j) {
            if (aCapNames[i] == gCapNames[j].name) {
                set.AddCapability(gCapNames[j].cap);
                break;
            }
        }
    }
    return set;
}

std::vector<std::string> TCapabilitySet::ToStringList() const {
    std::vector<std::string> list;
    for (size_t j = 0; j < sizeof(gCapNames) / sizeof(gCapNames[0]); ++j) {
        if (HasCapability(gCapNames[j].cap)) {
            list.push_back(gCapNames[j].name);
        }
    }
    return list;
}

static std::map<pid_t, TUint64> gProcessCapabilities;

TBool SecurityManager::CheckCapability(pid_t aPid, TCapability aRequiredCap) {
    if (aPid == 0 || aPid == getpid()) return ETrue; // Root/system service
    if (gProcessCapabilities.find(aPid) == gProcessCapabilities.end()) {
        // Default unprivileged process has basic UserEnvironment and NetworkServices
        return (aRequiredCap == ECapabilityNetworkServices || aRequiredCap == ECapabilityUserEnvironment);
    }
    return (gProcessCapabilities[aPid] & (1ULL << aRequiredCap)) != 0;
}

TBool SecurityManager::VerifyPrivatePathAccess(pid_t /*aPid*/, TUid aAppUid, const std::string& aPath) {
    // Isolated sandbox: /opt/symbian/private/<uid3>/
    char privatePrefix[128];
    snprintf(privatePrefix, sizeof(privatePrefix), "/opt/symbian/private/0x%08X", aAppUid.iUid);
    return (aPath.find(privatePrefix) == 0);
}

void SecurityManager::EnforceSandbox(TUid aAppUid) {
    char privateDir[128];
    snprintf(privateDir, sizeof(privateDir), "/opt/symbian/private/0x%08X", aAppUid.iUid);
    mkdir("/opt/symbian", 0755);
    mkdir("/opt/symbian/private", 0755);
    mkdir(privateDir, 0700);
}
