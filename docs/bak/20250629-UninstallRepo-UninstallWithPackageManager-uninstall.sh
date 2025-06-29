#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run the script with sudo or as root"
    exit 1
else
    current_user=$SUDO_USER
fi

if [ -d "/opt/LinuxOVPN" ]; then
    rm -r /opt/LinuxOVPN
    rm -r /home/$current_user/.local/share/applications/LinuxOVPN.desktop
    rm /etc/apt/sources.list.d/openvpn-aptrepo.list
    rm /etc/apt/keyrings/openvpn-repo-public.asc
    apt update
    echo "LinuxOVPN has successfully been uninstalled."
fi
