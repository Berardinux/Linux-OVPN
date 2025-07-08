#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run the script with sudo or as root"
    exit 1
fi

echo "Uninstalling LinuxOVPN..."

cd / || exit 1

# Remove application files
if [ -d /opt/LinuxOVPN ]; then
    rm -rf /opt/LinuxOVPN
    echo "/opt/LinuxOVPN removed."
else
    echo "/opt/LinuxOVPN not found."
fi

# Remove system-wide .desktop file
desktop_file="/usr/share/applications/LinuxOVPN.desktop"

if [ -f "$desktop_file" ]; then
    rm -f "$desktop_file"
    echo "$desktop_file removed."
else
    echo "$desktop_file not found."
fi

echo "LinuxOVPN application files removed."

# Detect package manager
if command -v apt &> /dev/null; then
    pkg_manager="apt"
elif command -v dnf &> /dev/null; then
    pkg_manager="dnf"
elif command -v yum &> /dev/null; then
    pkg_manager="yum"
elif command -v pacman &> /dev/null; then
    pkg_manager="pacman"
elif command -v apk &> /dev/null; then
    pkg_manager="apk"
elif command -v zypper &> /dev/null; then
    pkg_manager="zypper"
else 
    echo "# (ERROR) We cannot find your package manager!"
    exit 1
fi

echo "Removing LinuxOVPN build dependencies..."

case "$pkg_manager" in
    apt)
        apt remove --purge -y \
            libssl-dev \
            liblzo2-dev \
            liblz4-dev \
            libpam0g-dev \
            libpkcs11-helper1-dev \
            libsystemd-dev \
            libnl-3-dev \
            libnl-genl-3-dev \
            libcap-ng-dev \
            python3-docutils
        apt autoremove -y
        ;;
    dnf)
        dnf remove -y \
            openssl-devel \
            lzo-devel \
            lz4-devel \
            pam-devel \
            pkcs11-helper-devel \
            systemd-devel \
            libcap-ng-devel \
            python3-docutils
        ;;
    yum)
        yum remove -y \
            openssl-devel \
            lzo-devel \
            lz4-devel \
            pam-devel \
            pkcs11-helper-devel \
            systemd-devel \
            libcap-ng-devel \
            python3-docutils
        ;;
    pacman)
        pacman -Rs --noconfirm \
            openssl \
            lzo \
            lz4 \
            pam \
            pkcs11-helper \
            systemd \
            libcap-ng \
            python-docutils
        ;;
    apk)
        apk del \
            openssl-dev \
            lzo-dev \
            lz4-dev \
            linux-pam-dev \
            pkcs11-helper-dev \
            libcap-ng-dev \
            py3-docutils
        ;;
    zypper)
        zypper rm -y \
            libopenssl-devel \
            lzo-devel \
            lz4-devel \
            pam-devel \
            pkcs11-helper-devel \
            libsystemd-dev \
            libcap-ng-devel \
            python3-docutils
        ;;
esac

echo "LinuxOVPN uninstallation complete!"

pkill -9 -f LinuxOVPN
