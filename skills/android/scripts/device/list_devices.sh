#!/bin/bash
# List all connected Android devices and emulators
# Outputs JSON by default

set -e

FORMAT="${1:-json}"

devices=$(adb devices -l 2>&1)

if [ "$FORMAT" = "json" ]; then
    echo "$devices" | tail -n +2 | grep -v "^$" | awk '{
        split($0, parts, " ")
        udid = parts[1]
        state = parts[2]
        
        # Extract device info
        model = ""
        device = ""
        transport_id = ""
        
        for (i = 3; i <= NF; i++) {
            if (match(parts[i], /model:/)) {
                model = substr(parts[i], 7)
            }
            if (match(parts[i], /device:/)) {
                device = substr(parts[i], 8)
            }
            if (match(parts[i], /transport_id:/)) {
                transport_id = substr(parts[i], 14)
            }
        }
        
        printf "{\"udid\":\"%s\",\"state\":\"%s\",\"model\":\"%s\",\"device\":\"%s\",\"transport_id\":\"%s\"}\n", udid, state, model, device, transport_id
    }' | jq -s '{"success": true, "data": {"devices": .}, "error": null}'
else
    echo "Connected Android Devices:"
    echo "========================="
    echo "$devices" | tail -n +2 | grep -v "^$"
fi
