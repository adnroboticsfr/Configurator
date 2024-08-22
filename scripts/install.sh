#!/bin/bash

# Installation script for a Python application in a virtual environment

# Configuration variables
REPO_URL="https://github.com/adnroboticsfr/Configurator.git"  # Replace with your Git repository URL
APP_NAME="Configurator"  # Replace with the name of your application
VENV_DIR="venv"  # Name of the virtual environment directory
POLKIT_RULES_FILE="/usr/share/polkit-1/rules.d/50-nmcli.rules"

# Function to display error messages and exit the script
function die {
    echo "$1" >&2
    exit 1
}

# Update system packages
echo "Updating system packages..."
sudo apt-get update -y || die "Failed to update packages."

# Install necessary dependencies for Git and Python
echo "Installing Git and Python dependencies..."
sudo apt-get install -y git python3-venv python3-pip || die "Failed to install Git and Python dependencies."


# Navigate to the application directory
#cd "$APP_NAME" || die "Failed to navigate to the application directory."

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv "$VENV_DIR" || die "Failed to create the virtual environment."

# Activate the virtual environment
source "$VENV_DIR/bin/activate" || die "Failed to activate the virtual environment."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip || die "Failed to upgrade pip."
pip install requests gettext qrcode[pil] || die "Failed to install Python dependencies."

# Deactivate the virtual environment
deactivate

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
sudo systemctl restart polkit || die "Failed to restart Polkit rules."

echo "Installation completed successfully!"

python3 main.py
