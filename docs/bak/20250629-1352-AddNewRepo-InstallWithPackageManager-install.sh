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

if [ -z "$install" ] || [ "$install" = Y ] || [ "$install" = y ]; then


    if [ "$pkg_manager" = apt ]; then
        arch=$(dpkg --print-architecture)
        version="stable"
        osrelease=$(grep UBUNTU_CODENAME /etc/os-release | cut -d= -f2)
    
        ovpn_gpg_key="deb [arch=$arch signed-by=/etc/apt/keyrings/openvpn-repo-public.asc] \
            https://build.openvpn.net/debian/openvpn/$version $osrelease main"
    
        if ! grep -Fq "$ovpn_gpg_key" /etc/apt/sources.list.d/openvpn-aptrepo.list 2>/dev/null; then
            echo "Configuring OpenVPN APT repository..."
    
            mkdir -p /etc/apt/keyrings
    
            curl -fsSL https://swupdate.openvpn.net/repos/repo-public.gpg \
                | tee /etc/apt/keyrings/openvpn-repo-public.asc > /dev/null
    
            echo "$ovpn_gpg_key" > /etc/apt/sources.list.d/openvpn-aptrepo.list
        else
            echo "OpenVPN repo already configured."
        fi
    
        apt update && apt upgrade -y && apt install openvpn -y
    elif [ "$pkg_manager" = dnf ]; then
        sudo dnf update && sudo dnf install openvpn -y
    elif [ "$pkg_manager" = yum ]; then
        sudo yum update && sudo yum install openvpn -y
    elif [ "$pkg_manager" = pacman ]; then
        sudo pacman -Syu && sudo pacman -S --noconfirm openvpn
    elif [ "$pkg_manager" = apk ]; then
        sudo apk update && sudo apk install openvpn -y
    elif [ "$pkg_manager" = zypper ]; then
        sudo zypper update && sudo zypper install openvpn -you
    fi
fi

if [ -z "$app" ] || [ "$app" = Y ] || [ "$app" = y ]; then
    sudo mkdir -p /opt/LinuxOVPN
    sudo cp -r config css docs images scripts src /opt/LinuxOVPN
    touch "/home/$current_user/.local/share/applications/LinuxOVPN.desktop"
    sudo chown -R $current_user:$current_user /opt/LinuxOVPN
    sudo chmod -R 755 /opt/LinuxOVPN/
    sudo chmod -R 777 /opt/LinuxOVPN/docs/user_ovpn_files
    sudo chmod -R 777 /opt/LinuxOVPN/config
    chmod 644 "/home/$current_user/.local/share/applications/LinuxOVPN.desktop"
    
    cat << EOM | sudo tee -a "/home/$current_user/.local/share/applications/LinuxOVPN.desktop" >/dev/null
[Desktop Entry]
Type=Application
Name=LinuxOVPN
Comment=Linux OpenVPN Connect
Icon=/opt/LinuxOVPN/images/linuxovpn.png
Exec=python3 LinuxOVPN
Path=/opt/LinuxOVPN/src
Terminal=false
EOM
    
    echo "###### Installation complete! ######"
fi
