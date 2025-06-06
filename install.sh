#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "please run the script with sudo or as root"
    exit 1
else
    current_user=$SUDO_USER
fi

if [ -d "/opt/LinuxOVPN" ]; then
    echo "# (ERROR) LinuxOVPN is already installed on your system."
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
        sudo apt update && sudo apt upgrade -y && sudo apt install openvpn -y
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
    sudo cp -r config css docs images src /opt/LinuxOVPN
    touch "/home/$current_user/.local/share/applications/LinuxOVPN.desktop"
    sudo chmod -R 755 /opt/LinuxOVPN/
    chmod 644 "/home/$current_user/.local/share/applications/LinuxOVPN.desktop"
    
    cat << EOM | sudo tee -a "/home/$current_user/.local/share/applications/LinuxOVPN.desktop" >/dev/null
[Desktop Entry]
Type=Application
Name=LinuxOVPN
Comment=Linux OpenVPN Connect
Icon=/opt/LinuxOVPN/images/openvpn.png
Exec=python3 main.py
Path=/opt/LinuxOVPN/src
Terminal=false
EOM
    
    echo "###### Installation complete! ######"
fi
