#!/bin/bash
# Resolves and downloads TCZ extensions for Tiny Core Linux 15.x x86
set -e

REPO="http://repo.tinycorelinux.net/15.x/x86/tcz"
DEST="kernel/tinycore/tcz"
mkdir -p "$DEST"

# Primary application list requested
APPS=(
    "dillo.tcz"
    "leafpad.tcz"
    "gpicview.tcz"
    "epdfview.tcz"
    "pcmanfm.tcz"
    "lxtask.tcz"
    "htop.tcz"
)

declare -A VISITED
QUEUE=("${APPS[@]}")
ALL_PACKAGES=()

echo "[1/2] Resolving dependencies from $REPO..."
while [ ${#QUEUE[@]} -gt 0 ]; do
    PKG="${QUEUE[0]}"
    QUEUE=("${QUEUE[@]:1}")
    
    [[ "$PKG" != *.tcz ]] && PKG="${PKG}.tcz"
    [ -n "${VISITED[$PKG]}" ] && continue
    VISITED[$PKG]=1
    ALL_PACKAGES+=("$PKG")
    
    # Fetch .dep
    DEP_CONTENT=$(curl -s --connect-timeout 2 --max-time 3 "$REPO/${PKG}.dep" || true)
    while IFS= read -r DEP; do
        DEP=$(echo "$DEP" | tr -d '\r' | xargs)
        if [ -n "$DEP" ]; then
            [[ "$DEP" != *.tcz ]] && DEP="${DEP}.tcz"
            [ -z "${VISITED[$DEP]}" ] && QUEUE+=("$DEP")
        fi
    done <<< "$DEP_CONTENT"
done

echo "Resolved ${#ALL_PACKAGES[@]} total packages."

echo "[2/2] Downloading missing TCZ packages to $DEST..."
for PKG in "${ALL_PACKAGES[@]}"; do
    if [ ! -f "$DEST/$PKG" ]; then
        echo " -> Downloading $PKG..."
        curl -s --connect-timeout 5 --max-time 30 -o "$DEST/$PKG" "$REPO/$PKG" || {
            echo " [WARN] Failed to download $PKG"
            rm -f "$DEST/$PKG"
        fi
    else
        echo " [OK] $PKG already cached"
    fi
done

echo "All TCZ packages downloaded successfully!"
