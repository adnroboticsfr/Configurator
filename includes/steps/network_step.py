import gi
import subprocess
import os
import configparser
from gi.repository import Gtk, Gdk, GdkPixbuf

gi.require_version('Gtk', '3.0')

class WiFiSetup(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        self._ = _
        self.is_uppercase = False

        # Charger la configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/config.conf')
        self.image_path = self.config.get('Network_Select_WiFi', 'image_path', fallback='/path/to/default/image.png')

        # Lire la largeur et la hauteur de l'image depuis le fichier de configuration
        self.image_width = self.config.getint('Network_Select_WiFi', 'image_width', fallback=100)
        self.image_height = self.config.getint('Network_Select_WiFi', 'image_height', fallback=100)

        # Créer un Gtk.Stack pour gérer les pages
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.stack.set_transition_duration(500)

        # Créer et ajouter les pages au Gtk.Stack
        self.page1 = self.create_page1()
        self.page2 = self.create_page2()
        self.stack.add_named(self.page1, "page1")
        self.stack.add_named(self.page2, "page2")

        self.pack_start(self.stack, True, True, 0)
        self.show_page1()

        # Charger le fichier CSS
        self.load_css()

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('config/themes/theme.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def create_page1(self):
        page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Ajouter des marges autour des bords
        #page1.set_margin_top(20)
        #page1.set_margin_bottom(20)
        #page1.set_margin_end(20)

        # Label pour le titre
        title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        title_label.get_style_context().add_class('title')
        page1.pack_start(title_label, False, False, 10)

        # Conteneur principal pour le texte et l'image
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)


        # Création du conteneur pour le texte
        text_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        description_label = Gtk.Label(label=self._("Connect to Wi-Fi. This step enables you to send prints from phones, computers!"))
        description_label.get_style_context().add_class('text-under-image')
        #description_label.set_halign(Gtk.Align.CENTER)
        #description_label.set_justify(Gtk.Justification.CENTER)
        description_label.set_line_wrap(True)
        #description_label.set_hexpand(True)

        text_container.pack_start(description_label, True, True, 0)

        # Charger l'image depuis la configuration
        if os.path.exists(self.image_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.image_path)
            pixbuf = pixbuf.scale_simple(self.image_width, self.image_height, GdkPixbuf.InterpType.BILINEAR)
            wifi_image = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            wifi_image = Gtk.Image.new_from_icon_name("network-wireless-symbolic", Gtk.IconSize.DIALOG)

        # Ajouter le texte et l'image au conteneur principal, mais en inversant leur place
        main_box.pack_start(text_container, False, False, 0)
        main_box.pack_start(wifi_image, False, False, 0)

        page1.pack_start(main_box, True, True, 0)

        # Conteneur pour les boutons
        button_box = Gtk.Box(spacing=10, margin_top=20)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_hexpand(True)
        button_box.set_vexpand(False)

        back_button = Gtk.Button(label=self._("< Back"))
        back_button.get_style_context().add_class('button')
        back_button.connect("clicked", self.on_back_clicked)
        button_box.pack_start(back_button, False, False, 0)

        connect_button = Gtk.Button(label=self._("Connect to Wi-Fi"))
        connect_button.get_style_context().add_class('button')
        connect_button.connect("clicked", self.on_connect_to_wifi_clicked)
        button_box.pack_start(connect_button, False, False, 0)

        # Ajouter le bouton box avec un espace de marges
        page1.pack_start(button_box, False, False, 0)

        return page1

    def create_page2(self):
        page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin=20)
     

        return page2

    def show_page1(self):
        self.stack.set_visible_child_name("page1")

    def show_page2(self):
        self.stack.set_visible_child_name("page2")

    def on_back_clicked(self, button):
        if self.stack.get_visible_child_name() == "page2":
            self.show_page1()
        else:
            self.parent.previous_step()

    def on_connect_to_wifi_clicked(self, button):
        self.show_page2()

    def on_refresh_clicked(self, button):
        self.wifi_networks = self.get_wifi_networks()
        self.update_listbox()

    def on_wifi_switch_toggled(self, switch, state):
        if state:
            self.listbox.show_all()
            self.wifi_networks = self.get_wifi_networks()
            self.update_listbox()
        else:
            self.listbox.hide()

    def on_disconnect_clicked(self, button):
        try:
            subprocess.run(['nmcli', 'radio', 'wifi', 'off'])
            print("Wi-Fi disconnected")
        except Exception as e:
            print(f"Failed to disconnect Wi-Fi: {e}")

    def get_wifi_networks(self):
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE, text=True)
            networks = result.stdout.split('\n')
            return [net.split(":") for net in networks if net]
        except Exception as e:
            print(f"Error scanning Wi-Fi networks: {e}")
            return []

    def update_listbox(self):
        self.listbox.foreach(lambda child: self.listbox.remove(child))
        for ssid, security, signal in self.wifi_networks:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            icon_name = "network-wireless-signal-excellent-symbolic" if signal == "100" else "network-wireless-symbolic"
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.SMALL_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)

            ssid_label = Gtk.Label(label=ssid)
            ssid_label.set_xalign(0)
            hbox.pack_start(ssid_label, True, True, 0)

            row.add(hbox)
            self.listbox.add(row)

        self.listbox.show_all()

    def on_skip_clicked(self, button):
        self.parent.next_step()
