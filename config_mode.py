import gi
import os
import configparser
import gettext
from includes.steps import language_step, app_step, network1_step, network2_step, welcome_step, calibration_step

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def setup_translation(language_code):
    locale_dir = os.path.join(os.path.dirname(__file__), 'config/locales')
    lang = gettext.translation('messages', localedir=locale_dir, languages=[language_code], fallback=True)
    lang.install()
    return lang.gettext

def run_config_mode():
    class ConfigModeApp(Gtk.Window):
        def __init__(self):
            super().__init__()
            self.set_border_width(10)
            self.set_default_size(800, 500)

            # Charger le thème CSS
            css_provider = Gtk.CssProvider()
            css_file = os.path.join(os.path.dirname(__file__), 'config/themes/theme.css')
            css_provider.load_from_path(css_file)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

            # Charger la langue définie dans le fichier de configuration
            config = configparser.ConfigParser()
            config.read('config/config.conf')
            default_language = config.get('main', 'language', fallback='en_US')

            self._ = setup_translation(default_language)

            self.steps = [
                welcome_step.WelcomeStep(self),
                language_step.LanguageStep(self),
                network1_step.NetworkStep1(self, self._),
                network2_step.NetworkStep2(self, self._),
                #app_step.AppConnectStep(self, self._),
                calibration_step.CalibrationStep(self, self._)
            ]

            self.step_names = {
                'welcome': 0,
                'language': 1,
                'network1': 2,
                'network2': 3,
                'app': 4,
                'calibration': 5,
            }

            self.current_step_index = 0

            self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.add(self.main_container)

            self.step_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.main_container.pack_start(self.step_container, True, True, 0)

            self.show_step(self.current_step_index)

        def setup_translation(self, language_code):
            self._ = setup_translation(language_code)
            for step in self.steps:
                if hasattr(step, 'update_translation'):
                    step.update_translation(self._)

        def skip_to_step(self, step_name):
            if step_name in self.step_names:
                step_index = self.step_names[step_name]
                self.show_step(step_index)
            else:
                print(f"Invalid step name: {step_name}")

        def show_step(self, step_index):
            if 0 <= step_index < len(self.steps):
                for widget in self.step_container.get_children():
                    self.step_container.remove(widget)
                self.step_container.pack_start(self.steps[step_index], True, True, 0)
                self.steps[step_index].show_all()
            else:
                print(f"Invalid step index: {step_index}")
            
        def next_step(self):
            if self.current_step_index < len(self.steps) - 1:
                self.current_step_index += 1
                self.show_step(self.current_step_index)
            else:
                self.complete_setup_mode()

        def previous_step(self):
            if self.current_step_index > 0:
                self.current_step_index -= 1
                self.show_step(self.current_step_index)


        def complete_setup_mode(self):
            config = configparser.ConfigParser()
            config.read('config/config.conf')
            config.set('main', 'setup_mode_enabled', 'false')
            with open('config/config.conf', 'w') as configfile:
                config.write(configfile)
            print(_("Setup mode complete. Restart the application to apply changes."))
            for widget in self.step_container.get_children():
                    widget.destroy()


    if not Gtk.init_check(None):
        raise RuntimeError("GTK could not be initialized.")

    app = ConfigModeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
