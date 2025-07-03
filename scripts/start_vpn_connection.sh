#!/bin/bash

VPN_CONFIG="$1"
STATUS_PATH="$2"
PASSWORD="$3"

OPENVPN_BIN="/opt/LinuxOVPN/docs/openvpn-local/sbin/openvpn"

if [ -z "$VPN_CONFIG" ] || [ -z "$STATUS_PATH" ]; then
    echo "Usage: $0 <vpn_config> <status_path> [password]"
    exit 1
fi

if [ -n "$PASSWORD" ]; then
    TEMP_PASS_FILE=$(mktemp)
    trap 'rm -f "$TEMP_PASS_FILE"' EXIT
    
    echo "$PASSWORD" > "$TEMP_PASS_FILE"
    chmod 600 "$TEMP_PASS_FILE"

    "$OPENVPN_BIN" \
        --config "$VPN_CONFIG" \
        --askpass "$TEMP_PASS_FILE" \
        --status "$STATUS_PATH" 1 &
else
    "$OPENVPN_BIN" \
        --config "$VPN_CONFIG" \
        --status "$STATUS_PATH" 1 &
fi

OPENVPN_PID=$!
echo "$OPENVPN_PID" > /tmp/openvpn.pid

wait $OPENVPN_PID

if [ -f "$STATUS_PATH" ]; then
    chmod 777 "$STATUS_PATH"
fi

