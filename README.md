# Configurator

Test on a Yumios 1.1.0 version

## Install :

git clone https://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@github.com/adnroboticsfr/Configurator.git

chmod +x Configurator/scripts/install.sh

./Configurator/scripts/install.sh

The installation script automatically launches the program in the Configurator/main.py folder

To launch the program in console mode, after the ssh connection

python3 Configurator/main.py

If the application does not start and there is the following message:

it is because the installation variable is set to "setup_mode_enabled = False" because all the installation steps have been completed and disables the launch of the program. you have to change the value to "setup_mode_enabled = true" in the [main] section of the configuration file in the Configurator/config/config.conf folder.

# Calibration test

Launches standard and generic commands to all printers. Thanks to the button, you can select the test you want:

- Fan test
- Axis test
- Speed ​​test (Warning!!! for this test the size of the plate must be approximately 230x230)

Warning!!! Stand close to press the button to turn off the printer in case of a problem during the test. Test on d12-230 first!

