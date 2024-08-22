import gi
import configparser
import os
from gi.repository import Gtk, Gdk, GdkPixbuf

gi.require_version('Gtk', '3.0')

class NetworkStep1(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        self._ = _

        # Charger la configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/config.conf')
        self.image_path = self.config.get('Network_Select_WiFi', 'image_path', fallback='/path/to/default/image.png')
        self.image_width = self.config.getint('Network_Select_WiFi', 'image_width', fallback=100)
        self.image_height = self.config.getint('Network_Select_WiFi', 'image_height', fallback=100)

        # Conteneur du titre avec fond de couleur
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.33, 0.05, 0.05, 1))  # Couleur #550d0d
        title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        title_label.get_style_context().add_class('title')
        title_box.pack_start(title_label, True, True, 0)
        
        # Ajouter l'icône retour << à gauche du titre
        back_button = Gtk.Button(label="<<")
        back_button.connect("clicked", self.on_back_clicked)
        title_box.pack_start(back_button, False, False, 0)

        self.pack_start(title_box, False, False, 0)

        # Conteneur principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.pack_start(main_box, True, True, 0)

        # Colonne de gauche grise
        left_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_column.set_size_request(100, -1)
        left_column.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.33, 0.33, 0.33, 1))  # Gris
        main_box.pack_start(left_column, False, False, 0)

        # Conteneur du texte et de l'image
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_box.set_margin_start(10)  # Ajouter une marge à gauche pour espacer le texte de la colonne grise

        # Texte descriptif
        self.description_label = Gtk.Label(label=self._("Connect to Wi-Fi. This step enables you to send prints from phones, computers!"))
        self.description_label.get_style_context().add_class('text-under-image')
        self.description_label.set_justify(Gtk.Justification.LEFT)
        self.description_label.set_line_wrap(True)
        self.description_label.set_xalign(0)  # Aligner le texte à gauche
        content_box.pack_start(self.description_label, True, True, 0)

        # Charger l'image et l'aligner en haut à droite du texte
        if os.path.exists(self.image_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.image_path, self.image_width, self.image_height, GdkPixbuf.InterpType.BILINEAR)
            self.wifi_image = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            self.wifi_image = Gtk.Image.new_from_icon_name("network-wireless-symbolic", Gtk.IconSize.DIALOG)
        
        # Aligner l'image en haut
        self.wifi_image.set_valign(Gtk.Align.START)
        content_box.pack_start(self.wifi_image, False, False, 0)

        main_box.pack_start(content_box, True, True, 0)

        # Boutons de navigation en bas
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)  # Aligner les boutons à droite
        button_box.set_margin_bottom(20)  # Ajouter une marge en bas

        skip_button = Gtk.Button(label=self._("Skip"))
        skip_button.connect("clicked", self.on_skip_clicked)
        button_box.pack_start(skip_button, False, False, 0)

        self.pack_end(button_box, False, False, 0)

    def on_back_clicked(self, button):
        self.parent.previous_step()

    def on_skip_clicked(self, button):
        self.parent.next_step()

    def update_translation(self, _):
        self._ = _
        self.description_label.set_text(self._("Connect to Wi-Fi. This step enables you to send prints from phones, computers!"))

