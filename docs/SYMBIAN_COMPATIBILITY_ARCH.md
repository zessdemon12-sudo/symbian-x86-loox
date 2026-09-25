# Symbian Compatibility Subsystem Architecture

This document describes the design, implementation, and interfaces of the Symbian-X86 compatibility subsystem running atop the Linux userland.

---

## 1. Architectural Principles

The Symbian compatibility layer does **not** emulate the hardware or attempt to interpret foreign ARM instructions natively in the kernel. Instead, it provides a clean, native x86 implementation of the core Symbian OS concepts, APIs, and execution paradigms:

1. **Active Object Architecture**: Non-preemptive event-driven multitasking within single threads, minimizing context switches and memory overhead.
2. **Two-Phase Construction & Cleanup Stack**: Bulletproof memory leak prevention using `CleanupStack::PushL()` and `User::Leave()`.
3. **Client-Server Architecture**: Asynchronous inter-process communication (IPC) with capability-checked message passing.
4. **Publish & Subscribe (`RProperty`)**: Ultra-lightweight property broadcast for state synchronization (battery level, network status, flight mode).
5. **Central Repository (`CRepository`)**: Hierarchical, transactional key-value store for application configuration and system parameters.
6. **Capability & Security Model**: Strict application sandboxing based on Symbian capabilities (`Cap_NetworkServices`, `Cap_UserEnvironment`, `Cap_ReadUserData`, `Cap_WriteUserData`, `Cap_AllFiles`).
7. **Resource System (`RResourceFile`)**: Binary `.rsc` resource compiler and localized string management.

---

## 2. Component Breakdown

### 2.1 Core Runtime (`symbian/api/`)
- `e32def.h`: Primitive Symbian data types (`TInt`, `TUint`, `TBool`, `TAny*`, `TInt32`, `TInt64`, `TReal64`).
- `e32cmn.h` & `e32des.h`: Symbian descriptor hierarchy:
  - 8-bit descriptors: `TDes8`, `TDesC8`, `TPtr8`, `TPtrC8`, `TBuf8<S>`, `TBufC8<S>`.
  - 16-bit descriptors: `TDes16`, `TDesC16`, `TPtr16`, `TPtrC16`, `TBuf16<S>`, `TBufC16<S>`.
- `e32base.h`:
  - `CBase`: Base class for heap-allocated objects; zeroes memory upon instantiation.
  - `CActive`: Base class for active objects. Implements `RunL()`, `DoCancel()`, `RunError()`.
  - `CActiveScheduler`: Event dispatcher running atop Linux `epoll` / eventfd.
  - `CleanupStack`: LIFO cleanup stack for leave-safe exception handling.
  - `TRAP` / `TRAPD` macros: Exception boundary catching `User::Leave()`.

### 2.2 Client-Server IPC (`symbian/ipc/`)
- `CServer2`: Base class for Symbian system servers. Creates a Unix domain socket under `/tmp/.symbian_ipc/<ServerName>`.
- `CSession2`: Represents an active client connection on the server.
- `RSessionBase`: Client-side handle for connecting to servers and sending synchronous (`SendReceive()`) or asynchronous (`Send()`) messages.
- `RMessage2`: Message container carrying function ID, 4 arguments, client thread identification, and capability credentials.

### 2.3 Publish & Subscribe (`RProperty`)
- Backed by POSIX shared memory (`/dev/shm/.symbian_pubsub`) with eventfd notifications.
- Keys are identified by `(TUid Category, TUint Key)`.
- Standard categories include:
  - `KUidSystemCategoryValue`: Battery status, charging state, thermal state.
  - `KUidNetworkCategoryValue`: Wi-Fi signal, connection state, IP address.

### 2.4 Central Repository (CenRep)
- Persistent key-value store mapping `(TUid RepositoryUid, TUint32 SettingId) -> TValue`.
- Storage directory: `/opt/symbian/system/data/cenrep/<RepositoryUid>.cre`.
- Supports transactional commits, read/write access control based on application `SecureID` and capabilities.

### 2.5 Security & Sandbox Isolation (`symbian/security/`)
- Every application package is assigned a unique `SecureID` (UID3).
- Directory layout:
  - `/opt/symbian/sys/bin/`: Application binaries (read-only for unprivileged apps).
  - `/opt/symbian/resource/apps/`: Resource files and icons.
  - `/opt/symbian/private/<SecureID>/`: Application private storage (accessible only by the owner application UID).
  - `/opt/symbian/system/data/`: Shared application data (requires `ReadUserData` / `WriteUserData`).
- Capability verification table:
  | Capability | Linux Equivalent / Mapping |
  | :--- | :--- |
  | `NetworkServices` | Access to network sockets (AF_INET, AF_INET6) |
  | `UserEnvironment` | Access to microphone, camera (`/dev/video*`, `/dev/snd/*`) |
  | `ReadUserData` | Read access to `/home/symbian/Documents` and shared media |
  | `WriteUserData` | Write access to `/home/symbian/Documents` and shared media |
  | `AllFiles` | Global filesystem read/write access |
  | `DiskAdmin` | Access to raw block devices and mount operations |

---

## 3. Application Lifecycle Framework (`symbian/framework/`)

```
   ┌───────────────┐
   │ Application   │
   │ Executable    │
   └───────┬───────┘
           │ 1. E32Main()
           ▼
   ┌───────────────┐
   │ CAknAppUi     │◄──── Event Loop (X11 / Openbox events)
   └───────┬───────┘
           │ 2. ConstructL()
           ▼
   ┌───────────────┐
   │ CAknDocument  │──── Persistent data model
   └───────┬───────┘
           │ 3. CreateViewL()
           ▼
   ┌───────────────┐
   │ CAknView      │──── Renders UI on LXDE / X11 Window
   └───────────────┘
```
