import gi
from gi.repository import Gtk
from includes.factory_steps import diagnostics_step, calibration_step, final_factory_step
import gettext
import os

def setup_translation(language_code):
    locale_dir = os.path.join(os.path.dirname(__file__), 'config/locales')
    lang = gettext.translation('messages', localedir=locale_dir, languages=[language_code], fallback=True)
    return lang.gettext

def run_factory_mode():
    class FactoryModeApp(Gtk.Window):
        def __init__(self):
            super().__init__(title=_("ConfigFlowX - Factory Mode"))
            self.set_border_width(10)
            self.set_default_size(800, 600)

            self.current_step = 0
            self.steps = [
                diagnostics_step.DiagnosticsStep(self),
                calibration_step.CalibrationStep(self),
                final_factory_step.FinalFactoryStep(self),
            ]

            self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.add(self.container)
            self.show_step(self.current_step)

        def show_step(self, step_index):
            for widget in self.container.get_children():
                widget.destroy()
            self.container.pack_start(self.steps[step_index], True, True, 0)
            self.steps[step_index].show_all()

        def next_step(self):
            if self.current_step < len(self.steps) - 1:
                self.current_step += 1
                self.show_step(self.current_step)
            else:
                self.complete_factory_mode()

        def previous_step(self):
            if self.current_step > 0:
                self.current_step -= 1
                self.show_step(self.current_step)

        def complete_factory_mode(self):
            import configparser
            config = configparser.ConfigParser()
            config.read('config/config.conf')
            config.set('general', 'factory_mode_enabled', 'false')
            with open('config/config.conf', 'w') as configfile:
                config.write(configfile)
            print(_("Factory mode complete. Restart the application to apply changes."))

    app = FactoryModeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
