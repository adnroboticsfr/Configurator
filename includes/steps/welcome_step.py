import gi
import configparser
from gi.repository import Gtk, GdkPixbuf, GLib, Pango

gi.require_version('Gtk', '3.0')

class WelcomeStep(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent

        # Lire le fichier de configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/config.conf')

        # Obtenir les paramètres depuis la configuration
        self.logo_enabled = self.config.getboolean('welcome', 'logo_enabled', fallback=True)
        self.logo_path = self.config.get('welcome', 'logo_path', fallback='assets/img/logo.png')
        self.logo_width = self.config.getint('welcome', 'logo_width', fallback=200)
        self.logo_height = self.config.getint('welcome', 'logo_height', fallback=100)
        self.delay = self.config.getint('welcome', 'delay', fallback=3000)

        # Créer un conteneur principal pour centrer le contenu
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_container.set_valign(Gtk.Align.CENTER)
        self.main_container.set_halign(Gtk.Align.CENTER)
        self.main_container.set_size_request(-1, 200)

        self.pack_start(self.main_container, True, True, 0)

        # Ajouter le logo si activé
        if self.logo_enabled:
            self.logo_image = self.create_resized_logo(self.logo_path, self.logo_width, self.logo_height)
            self.main_container.pack_start(self.logo_image, False, False, 0)

        # Ajouter un message de bienvenue
        self.label = Gtk.Label(label=_("Welcome"))
        self.label.set_name("welcome-label")
        self.label.set_line_wrap(True)  # Permet le retour à la ligne automatique
        self.label.set_line_wrap_mode(Pango.WrapMode.WORD) 
        self.main_container.pack_start(self.label, False, False, 0)

        if not self.logo_enabled:
            self.label.get_style_context().add_class('no-logo')

        GLib.timeout_add(self.delay, self.on_timeout)
        self.show_all()

    def create_resized_logo(self, path, width, height):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        logo_image = Gtk.Image.new_from_pixbuf(pixbuf)
        return logo_image

    def on_timeout(self):
        self.parent.next_step()
        return False
