# Symbian-X86 Native Application SDK Guide

This guide demonstrates how to build, test, and package native x86 applications for Symbian-X86 LOOX OS using standard Symbian project definitions (`.mmp` and `bld.inf`).

---

## 1. SDK Tools Overview

The SDK provides:
- **`mmp_builder`**: Generates native x86 Makefiles from standard Symbian `.mmp` project definitions.
- **`rcomp`**: Symbian Resource Compiler that transforms `.rss` definition files into binary `.rsc` files.
- **`makesis`**: Packages native x86 binaries, resource files, and icons into standard `.sisx` archives.
- **`signsis`**: Signs generated packages with X.509 certificates.
- **`symbian-run`**: Test runner that launches native Symbian apps or provides emulation fallback for ARM binaries.

---

## 2. Project Layout for a Native Application

```
my_app/
├── bld.inf                  # Component build definition
├── group/
│   └── my_app.mmp          # Project specification (sources, includes, libraries, UID3)
├── inc/
│   ├── my_app.h
│   └── my_appui.h
├── src/
│   ├── my_app.cpp
│   └── my_appui.cpp
├── data/
│   └── my_app.rss          # Resource file (menus, localized strings)
└── sis/
    └── my_app.pkg          # Package description for makesis
```

---

## 3. Example Project Definition Files

### `group/my_app.mmp`:
```text
TARGET        my_app.exe
TARGETTYPE    exe
UID           0x100039CE 0x2000E101
SECUREID      0x2000E101
CAPABILITY    NetworkServices UserEnvironment

USERINCLUDE   ../inc
SYSTEMINCLUDE /opt/symbian/include

SOURCEPATH    ../src
SOURCE        my_app.cpp my_appui.cpp

LIBRARY       euser.lib aknnotify.lib apparc.lib
```

### `sis/my_app.pkg`:
```text
; Package specification for MyApp
#{"MyApp"}, (0x2000E101), 1, 0, 0

%{"Fujitsu-Symbian"}
:"Fujitsu"

(0x101F7961), 0, 0, 0, {"Series60ProductID"}

"/opt/symbian/sys/bin/my_app.exe" - "!:\sys\bin\my_app.exe"
"../data/my_app.rsc"              - "!:\resource\apps\my_app.rsc"
"../data/my_app.png"              - "!:\resource\apps\my_app.png"
```

---

## 4. Build & Package Workflow

```bash
# 1. Compile resources
rcomp -u -s../data/my_app.rss -o../data/my_app.rsc

# 2. Build executable using mmp_builder
mmp_builder group/my_app.mmp
make -f Makefile

# 3. Create SISX package
makesis sis/my_app.pkg my_app.sisx

# 4. Sign package with test key
signsis my_app.sisx my_app.sisx test.cert test.key

# 5. Run & Test on host
symbian-run ./my_app.exe
```
