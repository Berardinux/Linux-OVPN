#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run the script with sudo or as root"
    exit 1
fi

current_user=${SUDO_USER:-root}

echo "Uninstalling LinuxOVPN..."

# Remove application files
rm -rf /opt/LinuxOVPN

rm -f "/home/$current_user/.local/share/applications/LinuxOVPN.desktop"

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
        sudo apt remove --purge -y \
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
        sudo apt autoremove -y
        ;;
    dnf)
        sudo dnf remove -y \
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
        sudo yum remove -y \
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
        sudo pacman -Rs --noconfirm \
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
        sudo apk del \
            openssl-dev \
            lzo-dev \
            lz4-dev \
            linux-pam-dev \
            pkcs11-helper-dev \
            libcap-ng-dev \
            py3-docutils
        ;;
    zypper)
        sudo zypper rm -y \
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

