import argparse
import configparser
import hashlib
import gettext
import os

# Désactiver l'accessibilité si non nécessaire
os.environ['NO_AT_BRIDGE'] = '1'

# Définir l'affichage pour les environnements graphiques
os.environ['DISPLAY'] = ':0'

def setup_translation(language_code):
    locale_dir = os.path.join(os.path.dirname(__file__), 'config/locales')
    lang = gettext.translation('messages', localedir=locale_dir, languages=[language_code], fallback=True)
    return lang.gettext

def main():
    parser = argparse.ArgumentParser(description="ConfigFlowX - 3D Printer Configuration Tool")
    parser.add_argument('--factory-mode', type=str, help='Enter the password to access factory mode')
    parser.add_argument('--set-mode', type=str, choices=['factory', 'setup'], help='Set the default mode (factory or setup)')
    parser.add_argument('--reset-factory', action='store_true', help='Reset factory mode to be executable again')
    parser.add_argument('--reset-setup', action='store_true', help='Reset setup mode to be executable again')
    parser.add_argument('--lang', type=str, default='en_US', help='Set the language (e.g., en_US, fr_FR)')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config/config.conf')

    default_mode = config.get('main', 'default_mode')
    factory_mode_enabled = config.getboolean('main', 'factory_mode_enabled')
    setup_mode_enabled = config.getboolean('main', 'setup_mode_enabled')

    _ = setup_translation(args.lang)

    if args.set_mode:
        if args.set_mode in ['factory', 'setup']:
            config.set('main', 'default_mode', args.set_mode)
            with open('config/config.conf', 'w') as configfile:
                config.write(configfile)
            print(_("Default mode set to {}.").format(args.set_mode))
        return

    if args.reset_factory:
        config.set('main', 'factory_mode_enabled', 'true')
        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)
        print(_("Factory mode has been reset and can be executed again."))
        return

    if args.reset_setup:
        config.set('main', 'setup_mode_enabled', 'true')
        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)
        print(_("Setup mode has been reset and can be executed again."))
        return

    if args.factory_mode:
        from factory_mode import run_factory_mode
        hashed_password = hashlib.sha256(args.factory_mode.encode()).hexdigest()
        FACTORY_PASSWORD_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd8e9f11f8cbe78ddcd"  # Exemple de hash pour "password"
        if hashed_password == FACTORY_PASSWORD_HASH:
            if factory_mode_enabled:
                run_factory_mode()
            else:
                print(_("Factory mode has already been completed. Reset 'factory_mode_enabled' in config to run again."))
        else:
            print(_("Invalid password. Access denied."))
    else:
        from config_mode import run_config_mode
        if default_mode == "factory" and factory_mode_enabled:
            run_factory_mode()
        elif default_mode == "setup" and setup_mode_enabled:
            run_config_mode()
        else:
            print(_("{} mode has already been completed or is disabled. Reset the mode to run again.").format(default_mode.capitalize()))

if __name__ == "__main__":
    main()
