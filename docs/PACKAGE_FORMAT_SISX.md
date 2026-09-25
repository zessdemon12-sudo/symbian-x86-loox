# SIS and SISX Package Management Specification

This document details the binary structure, metadata format, capability enforcement, and installation workflow for `.sis` and `.sisx` application packages on Symbian-X86 LOOX OS.

---

## 1. Overview of Package Formats

Symbian-X86 LOOX OS supports two formats:
1. **SISX (Symbian OS v9.x+)**: Modern SIS format with digital signatures, capability declarations, SHA-1/SHA-256 digests, and compressed file blocks (UID: `0x10201A7A`).
2. **Legacy SIS (Symbian OS v6/7/8)**: Legacy packaging format with uncompressed or zlib data blocks (UID: `0x1000006D`).

### Architecture Notice
Native Symbian-X86 packages contain x86 (`i686`) ELF shared libraries or executables. For legacy ARM binaries packaged in `.sis` or `.sisx`, the package installer tags the application to run via the ARM compatibility runner (`symbian-run --arm`), which leverages user-mode translation (e.g. QEMU-ARM or EKA2L1).

---

## 2. SISX Binary Structure

```
+-------------------------------------------------------------+
| Header (32 bytes)                                           |
| - UID1: 0x10201A7A (SISX identifier)                        |
| - UID2: Package Type                                        |
| - UID3: Application SecureID (UID3)                         |
| - Checksum & Header CRC                                     |
+-------------------------------------------------------------+
| Language Block (Supported language codes, e.g. EN, JA)      |
+-------------------------------------------------------------+
| Package Names (Localized string table)                      |
+-------------------------------------------------------------+
| Vendor Names (Localized vendor strings)                     |
+-------------------------------------------------------------+
| Version (Major, Minor, Build)                               |
+-------------------------------------------------------------+
| Capability Bitmask (64-bit required capability set)         |
+-------------------------------------------------------------+
| File Manifest Block:                                        |
| - Target Path (e.g., "!:\sys\bin\app.exe")                  |
| - File Size & Offset                                        |
| - SHA-256 Digest                                            |
| - Compression Flag (0 = Uncompressed, 1 = Deflate/Zlib)      |
+-------------------------------------------------------------+
| Signature & Certificate Chain Block (X.509 DER)             |
+-------------------------------------------------------------+
| Data Payloads (Compressed file archives)                    |
+-------------------------------------------------------------+
```

### Drive Letter Mapping in Package Targets:
- `!:\sys\bin\`: Resolves to `/opt/symbian/sys/bin/` on drive selected during installation (`C:` = System root, `E:` = Removable/Mass storage).
- `!:\resource\apps\`: Resolves to `/opt/symbian/resource/apps/` (contains `.rsc` and icon files).
- `!:\private\<UID3>\`: Application private data storage sandbox.

---

## 3. Package Management Engine (`symbian-pkg`)

The package manager provides command-line and graphical interfaces:

### CLI Commands:
```bash
# Install a SISX package
symbian-pkg install /path/to/app.sisx --target=C:

# Query package details without installing
symbian-pkg info /path/to/app.sisx

# List installed packages
symbian-pkg list

# Uninstall a package by UID3
symbian-pkg remove 0x2000E001

# Verify package integrity and signatures
symbian-pkg verify /path/to/app.sisx
```

### Automatic Desktop Registration
When a package is installed:
1. Binary is extracted to `/opt/symbian/sys/bin/<app_name>`.
2. App icon is extracted or converted to standard PNG and placed in `/usr/share/icons/hicolor/48x48/apps/`.
3. An XDG `.desktop` file is generated in `/usr/share/applications/symbian-<uid3>.desktop`.
4. App appears automatically in the Symbian Belle LXPanel "Applications" menu under its designated category.
