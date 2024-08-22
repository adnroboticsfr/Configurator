import gi
from gi.repository import Gtk
import gettext
import os

def setup_translation(language_code):
    locale_dir = os.path.join(os.path.dirname(__file__), '../../config/locales')
    lang = gettext.translation('messages', localedir=locale_dir, languages=[language_code], fallback=True)
    return lang.gettext

class DiagnosticsStep(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        self.label = Gtk.Label(label=_("Diagnostics"))
        self.pack_start(self.label, True, True, 0)

        # Add diagnostic tools here

        self.show_all()
