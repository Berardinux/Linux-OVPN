#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "# (ERROR) please run the script with sudo or as root"
    exit 1
else
    current_user=$SUDO_USER
fi

if [ -d "/opt/LinuxOVPN" ]; then
    echo "# (ERROR) LinuxOVPN is already installed on your system."
    echo "          If you want to reinstall run the uninstall.sh script"
    echo "          in the scripts directory, and then run install.sh"
    echo "          again."
    exit 1
fi

prompt_user=1
if command -v apt &> /dev/null; then
    pkg_manager="apt"
elif command -v dnf &> /dev/null; then
    pkg_manager="dnf"
elif command -v "yum" &> /dev/null; then
    pkg_manager="yum"
elif command -v "pacman" &> /dev/null; then
    pkg_manager="pacman"
elif command -v "apk" &> /dev/null; then
    pkg_manager="apk"
elif command -v "zypper" &> /dev/null; then
    pkg_manager="zypper"
else 
    echo "# (ERROR) We cannot find your package manager on your system!"
    echo "#         Would you still like to install LinuxOVPN?"
    read -r app
    install=n
    prompt_user=0
fi

if [ "$prompt_user" = 1 ]; then
    keep_prompting_user=1
    while [ "$keep_prompting_user" = 1 ]; do
        clear
        echo "# Are you ready to install OpenVPN client (Y/n)"
        read -r install
        if [ -z "$install" ] || [ "$install" = Y ] || [ "$install" = y ] || [ "$install" = N ] || [ "$install" = n ]; then
            keep_prompting_user=0
            clear
        else
            echo "# (ERROR) That was not a valid option, try again"
        fi
    done
    
    keep_prompting_user=1
    while [ "$keep_prompting_user" = 1 ]; do
        echo "# Would you like to install the LinuxOVPN GUI application? (Y/n)"
        read -r app
        if [ -z "$app" ] || [ "$app" = Y ] || [ "$app" = y ] || [ "$app" = N ] || [ "$app" = n ]; then
            keep_prompting_user=0
            clear
        else
            echo "# (ERROR) That was not a valid option, try again"
        fi
    done
fi

if [ -z "$app" ] || [ "$app" = Y ] || [ "$app" = y ]; then
    sudo mkdir -p /opt/LinuxOVPN
    sudo cp -r config css docs images scripts src /opt/LinuxOVPN
    touch "/home/$current_user/.local/share/applications/LinuxOVPN.desktop"
    sudo chown -R $current_user:$current_user /opt/LinuxOVPN
    sudo chmod -R 755 /opt/LinuxOVPN/
    sudo chmod -R 777 /opt/LinuxOVPN/docs
    sudo chmod -R 777 /opt/LinuxOVPN/config
    chmod 644 "/home/$current_user/.local/share/applications/LinuxOVPN.desktop"
    
    cat << EOM | sudo tee "/home/$current_user/.local/share/applications/LinuxOVPN.desktop" >/dev/null
[Desktop Entry]
Type=Application
Name=LinuxOVPN
Comment=Linux OpenVPN Connect
Icon=/opt/LinuxOVPN/images/linuxovpn.png
Exec=pkexec python3 LinuxOVPN
Path=/opt/LinuxOVPN/src
Terminal=false
EOM
    
    echo "###### LinuxOVPN Installation complete! ######"
fi

if [ -z "$install" ] || [ "$install" = Y ] || [ "$install" = y ]; then
    if [ "$pkg_manager" = apt ]; then
        sudo apt update && sudo apt upgrade -y
        sudo apt install -y \
            build-essential \
            pkg-config \
            libssl-dev \
            liblzo2-dev \
            liblz4-dev \
            libpam0g-dev \
            libpkcs11-helper1-dev \
            libtool \
            automake \
            autoconf \
            libsystemd-dev \
            libnl-3-dev \
            libnl-genl-3-dev \
            libcap-ng-dev \
            python3-docutils

    elif [ "$pkg_manager" = dnf ]; then
        sudo dnf update -y
        sudo dnf install -y \
            gcc \
            make \
            automake \
            autoconf \
            libtool \
            pkgconf-pkg-config \
            openssl-devel \
            lzo-devel \
            lz4-devel \
            pam-devel \
            pkcs11-helper-devel \
            systemd-devel \
            libcap-ng-devel \
            python3-docutils

    elif [ "$pkg_manager" = yum ]; then
        sudo yum update -y
        sudo yum install -y \
            gcc \
            make \
            automake \
            autoconf \
            libtool \
            pkgconfig \
            openssl-devel \
            lzo-devel \
            lz4-devel \
            pam-devel \
            pkcs11-helper-devel \
            systemd-devel \
            libcap-ng-devel \
            python3-docutils

    elif [ "$pkg_manager" = pacman ]; then
        sudo pacman -Syu --noconfirm
        sudo pacman -S --noconfirm \
            base-devel \
            openssl \
            lzo \
            lz4 \
            pam \
            pkcs11-helper \
            systemd \
            libcap-ng \
            python-docutils

    elif [ "$pkg_manager" = apk ]; then
        sudo apk update
        sudo apk add --no-cache \
            build-base \
            openssl-dev \
            lzo-dev \
            lz4-dev \
            linux-pam-dev \
            pkcs11-helper-dev \
            autoconf \
            automake \
            libtool \
            libcap-ng-dev \
            py3-docutils

    elif [ "$pkg_manager" = zypper ]; then
        sudo zypper refresh
        sudo zypper update -y
        sudo zypper install -y \
            gcc \
            make \
            automake \
            autoconf \
            libtool \
            pkg-config \
            libopenssl-devel \
            lzo-devel \
            lz4-devel \
            pam-devel \
            pkcs11-helper-devel \
            libsystemd-dev \
            libcap-ng-devel \
            python3-docutils
    fi

    echo "### Building OpenVPN ###"

    cd /opt/LinuxOVPN/docs/openvpn-master || {
        echo "ERROR: OpenVPN source directory missing at /opt/LinuxOVPN/docs/openvpn-master"
        exit 1
    }

    if [ -f autogen.sh ]; then
        echo "Running autogen.sh"
        ./autogen.sh
    fi

    if [ -f configure.ac ]; then
        echo "Running autoreconf..."
        autoreconf -vi
    fi

    ./configure --prefix=/opt/LinuxOVPN/docs/openvpn-local \
        --disable-dependency-tracking \
        --enable-pkcs11 \
        --enable-systemd \
        --enable-async-push

    make -j$(nproc)
    make install

    echo "### OpenVPN build complete! Installed to /opt/LinuxOVPN/docs/openvpn-local ###"
fi



