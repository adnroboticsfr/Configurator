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
        self.image_path = self.config.get('Network_Select_WiFi', 'image_path', fallback='assets/img/wificonfig.png')
        self.image_width = self.config.getint('Network_Select_WiFi', 'image_width', fallback=100)
        self.image_height = self.config.getint('Network_Select_WiFi', 'image_height', fallback=100)

        # Conteneur principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.pack_start(main_box, True, True, 0)

        # Conteneur pour le titre et le bouton "Skip"
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))  # Couleur de fond #550d0d
        title_box.set_margin_top(16)
        title_box.set_margin_bottom(12)
        title_box.set_margin_start(10)
        title_box.set_margin_end(10)

        # Bouton de retour
        back_button = Gtk.Button(label="<")
        back_button.connect("clicked", self.on_back_clicked)
        back_button.get_style_context().add_class('button')
        title_box.pack_start(back_button, False, False, 0)

        # Label pour le titre
        self.title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        self.title_label.get_style_context().add_class('title')
        self.title_label.set_xalign(0.5)  # Centrer le texte horizontalement
        title_box.pack_start(self.title_label, True, True, 0)

        # Bouton "Skip"
        self.skip_button = Gtk.Button(label=self._("Skip"))
        self.skip_button.connect("clicked", self.on_skip_clicked)
        self.skip_button.get_style_context().add_class('button')
        title_box.pack_start(self.skip_button, False, False, 0)

        # Ajouter le conteneur de titre en haut de la boîte principale
        main_box.pack_start(title_box, False, False, 0)

        # Conteneur principal pour le contenu
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        content_box.set_hexpand(True)
        content_box.set_vexpand(True)
        main_box.pack_start(content_box, True, True, 0)

        # Colonne de gauche
        left_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_column.set_size_request(50, -1)  # Taille fixe pour la colonne de gauche
        left_column.set_margin_start(10)
        left_column.set_margin_end(10)
        content_box.pack_start(left_column, False, False, 0)

        # Conteneur pour la description
        text_button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        text_button_box.set_valign(Gtk.Align.START)  # Aligner vers le haut
        text_button_box.set_vexpand(True)

        # Description
        self.description = Gtk.Label(label=self._("Connect to Wi-Fi to be able to send prints from your phone or computer!"))
        self.description.get_style_context().add_class('text-under-image')
        self.description.set_justify(Gtk.Justification.LEFT)
        self.description.set_line_wrap(True)
        self.description.set_xalign(0)  # Aligner le texte à gauche
        self.description.set_valign(Gtk.Align.START)  # Aligner le texte vers le haut
        text_button_box.pack_start(self.description, False, False, 10)

        # Ajouter le conteneur pour le texte à gauche
        content_box.pack_start(text_button_box, True, True, 0)

        # Charger l'image et l'aligner à droite
        if os.path.exists(self.image_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.image_path, self.image_width, self.image_height, GdkPixbuf.InterpType.BILINEAR)
            wifi_image = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            icon_size = 148  # Taille de l'icône par défaut
            wifi_image = Gtk.Image.new_from_icon_name("network-wireless-symbolic", Gtk.IconSize.DIALOG)
            wifi_image.set_size_request(icon_size, icon_size)
        
        # Créer un conteneur pour l'image et l'aligner vers le haut
        image_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        image_box.set_valign(Gtk.Align.START)  # Aligner l'image vers le haut
        image_box.set_margin_end(20)  # Ajuster l'espacement depuis le bord droit
        image_box.pack_start(wifi_image, False, False, 0)

        # Ajouter l'image à droite
        content_box.pack_start(image_box, False, False, 0)

        # Conteneur pour le bouton "Connect to Wi-Fi"
        button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_container.set_halign(Gtk.Align.CENTER)  # Centrer horizontalement le bouton
        button_container.set_margin_top(20)  # Ajouter un espace au-dessus du bouton
        button_container.set_margin_bottom(60)  # Ajouter un espace au-dessus du bouton
        main_box.pack_start(button_container, False, False, 0)

        # Ajouter le bouton "Connect to Wi-Fi" en bas du conteneur
        self.connect_button = Gtk.Button(label=self._("Connect to Wi-Fi"))
        self.connect_button.connect("clicked", self.on_connect_clicked)
        self.connect_button.get_style_context().add_class('button')
        button_container.pack_start(self.connect_button, False, False, 0)

    def update_translation(self, _):
        self._ = _
        self.title_label.set_text(self._("Network Select Wi-Fi"))
        self.description.set_text(self._("Connect to Wi-Fi to be able to send prints from your phone or computer!"))
        self.connect_button.set_label(self._("Connect to Wi-Fi"))
        self.skip_button.set_label(self._("Skip"))

    def on_back_clicked(self, button):
        self.parent.previous_step()

    def on_connect_clicked(self, button):
        # Ajouter la logique pour se connecter au Wi-Fi
        # Exemple de ce qui pourrait être fait:
        self.parent.next_step()  # Passer à l'étape suivante après la connexion

    def on_skip_clicked(self, button):
        # Changer directement à l'étape de calibration
        self.parent.skip_to_step('calibration')
