#!/usr/bin/env bash

HOST="${1:-google.com}"

if getent hosts "$HOST" >/dev/null 2>&1; then
    echo "DNS resolution successful for $HOST"
else
    echo "DNS resolution failed for $HOST"
    exit 1
fi

if command -v ping >/dev/null 2>&1 && ping -c 1 -W 2 "$HOST" >/dev/null 2>&1; then
    echo "Network connectivity successful for $HOST"
else
    echo "Ping failed for $HOST (ICMP may be blocked)"
fi
