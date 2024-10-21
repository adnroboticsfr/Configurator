#!/bin/bash

# Installation script for a Python application in a virtual environment

# Configuration variables
REPO_URL="https://github.com/adnroboticsfr/Configurator.git"  # Replace with your Git repository URL
APP_NAME="Configurator"  # Replace with the name of your application
VENV_DIR="venv"  # Name of the virtual environment directory
POLKIT_RULES_FILE="/usr/share/polkit-1/rules.d/50-nmcli.rules"
SUDOERS_FILE="/etc/sudoers.d/klipper_mainsail_restart"  # Sudoers file for passwordless restart of services

# Function to display error messages and exit the script
function die {
    echo "$1" >&2
    exit 1
}

# Install necessary dependencies for Git and Python
echo "Installing Git and Python dependencies..."
sudo apt-get install -y git python3-venv python3-pip gettext || die "Failed to install Git and Python dependencies."

# Remove EXTERNALLY-MANAGED restriction if present
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip || die "Failed to upgrade pip."
python3 -m pip install requests qrcode[pil] || die "Failed to install Python dependencies."

# Create the Polkit rules file
echo "Creating the Polkit rules file..."
sudo mkdir -p /usr/share/polkit-1/rules.d/
echo 'polkit.addRule(function(action, subject) {
    if (subject.isInGroup("sudo") && action.id.indexOf("org.freedesktop.NetworkManager") == 0) {
        return polkit.Result.YES;
    }
});' | sudo tee "$POLKIT_RULES_FILE" > /dev/null || die "Failed to create the Polkit rules file."

# Reload Polkit rules
echo "Reloading Polkit rules..."
sudo systemctl restart polkit || die "Failed to restart Polkit."

# Add passwordless sudo for restarting Klipper, Mainsail, and Klipperscreen
echo "Configuring passwordless sudo for restarting services..."
# Add passwordless sudo for restarting Klipper, Klipperscreen, and Moonraker
echo "pi ALL=(ALL) NOPASSWD: /bin/systemctl restart klipper.service, /bin/systemctl restart klipper-mcu.service, /bin/systemctl restart KlipperScreen.service, /bin/systemctl restart moonraker.service, /bin/systemctl restart moonraker-obico.service" | sudo tee "$SUDOERS_FILE" > /dev/null || die "Failed to configure passwordless sudo for services."

# Compile message translations
echo "Compiling message translations..."
msgfmt -o config/locales/en_US/LC_MESSAGES/messages.mo config/locales/en_US/LC_MESSAGES/messages.po
msgfmt -o config/locales/fr_FR/LC_MESSAGES/messages.mo config/locales/fr_FR/LC_MESSAGES/messages.po
msgfmt -o config/locales/es_ES/LC_MESSAGES/messages.mo config/locales/es_ES/LC_MESSAGES/messages.po
msgfmt -o config/locales/zh_CN/LC_MESSAGES/messages.mo config/locales/zh_CN/LC_MESSAGES/messages.po

echo "Installation completed successfully!"
