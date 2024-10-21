#!/bin/bash

# Arguments: $1 = printer model, $2 = head type, $3 = smartbox enabled
PRINTER_MODEL=$1
PRINTER_CONFIG_PATH="/home/pi/Configurator/printer_configs/${PRINTER_MODEL}/printer.cfg"
TARGET_CONFIG_PATH="/home/pi/printer_data/config/printer.cfg"

# Copy printer.cfg to the target location, replacing the existing one
if [ -f "$PRINTER_CONFIG_PATH" ]; then
    cp "$PRINTER_CONFIG_PATH" "$TARGET_CONFIG_PATH"
    echo "Printer configuration copied successfully."

    # Restart Klipper and Mainsail
    sudo systemctl restart klipper.service
    sudo systemctl restart klipper-mcu.service
    sudo systemctl restart moonraker.service
    sudo systemctl restart moonraker-obico.service
    echo "Klipper and Moonraker restarted."
else
    echo "Error: printer.cfg not found for model ${PRINTER_MODEL}."
    exit 1
fi
