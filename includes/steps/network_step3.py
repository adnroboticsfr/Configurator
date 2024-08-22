import gi
import subprocess
from gi.repository import Gtk

gi.require_version('Gtk', '3.0')

class NetworkStep2(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin=20)
        self.parent = parent
        self._ = _
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Créer la page 2
        self.page2 = self.create_page2()
        self.pack_start(self.page2, True, True, 0)

    def create_page2(self):
        page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin=20)
        page2.set_halign(Gtk.Align.CENTER)
        page2.set_valign(Gtk.Align.CENTER)
        page2.set_hexpand(True)
        page2.set_vexpand(True)

        # Conteneur pour le titre et le bouton rafraîchir
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_hexpand(True)
        header_box.set_vexpand(False)

        # Label du titre
        title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        title_label.get_style_context().add_class('title')
        title_label.set_margin_bottom(20)
        header_box.pack_start(title_label, True, True, 0)

        # Bouton rafraîchir avec icône
        refresh_button = Gtk.Button()
        refresh_button.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.LARGE_TOOLBAR))
        refresh_button.set_image_position(Gtk.PositionType.RIGHT)
        refresh_button.set_tooltip_text(self._("Refresh"))
        refresh_button.set_size_request(50, 50)  # Ajuster la taille du bouton
        refresh_button.connect("clicked", self.on_refresh_clicked)
        header_box.pack_start(refresh_button, False, False, 0)

        # Bouton pour activer/désactiver le Wi-Fi
        wifi_switch = Gtk.Switch()
        wifi_switch.set_active(True)
        wifi_switch.set_size_request(80, 30)  # Ajuster la taille du commutateur
        wifi_switch.connect("state-set", self.on_wifi_switch_toggled)
        header_box.pack_start(wifi_switch, False, False, 0)

        page2.pack_start(header_box, False, False, 10)

        # Conteneur principal pour les réseaux Wi-Fi
        self.networks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.networks_box.set_hexpand(True)
        self.networks_box.set_vexpand(True)
        self.networks_box.set_margin_bottom(20)

        # Ajouter la Box à une ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.networks_box)

        page2.pack_start(self.scrolled_window, True, True, 0)

        # Conteneur pour les boutons de navigation
        nav_box = Gtk.Box(spacing=10, margin_top=20)
        nav_box.set_halign(Gtk.Align.CENTER)

        back_button = Gtk.Button(label=self._("< Back"))
        back_button.get_style_context().add_class('button')
        back_button.connect("clicked", self.on_back_clicked)
        nav_box.pack_start(back_button, False, False, 0)

        skip_button = Gtk.Button(label=self._("Skip"))
        skip_button.get_style_context().add_class('button')
        skip_button.connect("clicked", self.on_skip_clicked)
        nav_box.pack_start(skip_button, False, False, 0)

        page2.pack_start(nav_box, False, False, 10)

        # Initialiser les réseaux Wi-Fi
        self.update_wifi_networks()

        return page2

    def on_back_clicked(self, button):
        self.parent.previous_step()

    def on_skip_clicked(self, button):
        self.parent.next_step()

    def on_refresh_clicked(self, button):
        self.update_wifi_networks()

    def on_wifi_switch_toggled(self, switch, state):
        if state:
            self.update_wifi_networks()
            self.scrolled_window.show_all()
        else:
            self.scrolled_window.hide()

    def on_network_clicked(self, widget):
        ssid = widget.get_label()
        self.show_password_dialog(ssid)

    def show_password_dialog(self, ssid):
        dialog = Gtk.Dialog(
            title=self._("Enter Password"),
            parent=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        )
        dialog.set_default_size(400, 200)

        content_area = dialog.get_content_area()
        content_area.set_padding(20)
        content_area.set_spacing(10)

        title_label = Gtk.Label(label=self._("Enter the password for network:") + f" {ssid}")
        title_label.set_markup(f"<b>{title_label.get_text()}</b>")
        content_area.pack_start(title_label, False, False, 0)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text(self._("Password"))
        content_area.pack_start(self.password_entry, False, False, 0)

        # Configuration du clavier virtuel
        self.keyboard = self.create_virtual_keyboard()
        content_area.pack_start(self.keyboard, False, False, 0)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            password = self.password_entry.get_text()
            print(f"Password for {ssid}: {password}")
            # Appeler la fonction pour se connecter au réseau avec le mot de passe
            self.connect_to_wifi(ssid, password)
        
        dialog.destroy()

    def create_virtual_keyboard(self):
        keyboard = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        keys = [
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        for row in keys:
            key_row = Gtk.Box(spacing=2)
            for key in row:
                button = Gtk.Button(label=key.upper())
                button.set_size_request(40, 40)
                button.get_style_context().add_class('keyboard-key')
                button.connect("clicked", self.on_keyboard_key_clicked)
                key_row.pack_start(button, False, False, 0)
            keyboard.pack_start(key_row, False, False, 0)

        special_keys = Gtk.Box(spacing=2)
        for label, action in [("Shift", self.on_shift_clicked), ("Space", self.on_space_clicked), ("Backspace", self.on_backspace_clicked)]:
            button = Gtk.Button(label=label)
            button.set_size_request(80, 40)
            button.get_style_context().add_class('keyboard-key')
            button.connect("clicked", action)
            special_keys.pack_start(button, False, False, 0)
        keyboard.pack_start(special_keys, False, False, 0)

        return keyboard

    def on_keyboard_key_clicked(self, button):
        current_text = self.password_entry.get_text()
        key = button.get_label().lower()
        self.password_entry.set_text(current_text + key)

    def on_shift_clicked(self, button):
        # Fonction pour gérer la touche Shift pour majuscules/minuscules
        pass

    def on_space_clicked(self, button):
        current_text = self.password_entry.get_text()
        self.password_entry.set_text(current_text + ' ')

    def on_backspace_clicked(self, button):
        current_text = self.password_entry.get_text()
        self.password_entry.set_text(current_text[:-1])

    def connect_to_wifi(self, ssid, password):
        try:
            # Connexion au réseau Wi-Fi
            subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password])
            print(f"Connecting to {ssid} with password.")
        except Exception as e:
            print(f"Failed to connect to Wi-Fi: {e}")

    def update_wifi_networks(self):
        # Vider les éléments existants
        for child in self.networks_box.get_children():
            self.networks_box.remove(child)

        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE, text=True)
            networks = result.stdout.split('\n')
            for net in networks:
                if net:
                    ssid, security, signal = net.split(":")
                    self.create_network_item(ssid, signal)
        except Exception as e:
            print(f"Error scanning Wi-Fi networks: {e}")

    def create_network_item(self, ssid, signal):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_hexpand(True)
        hbox.set_vexpand(False)
        
        # Label du SSID avec taille de texte très grande
        ssid_label = Gtk.Label(label=ssid)
        ssid_label.set_markup(f'<span size="xx-large" weight="bold">{ssid}</span>')  # Taille xx-large
        ssid_label.set_xalign(0)
        ssid_label.set_yalign(0)
        ssid_label.set_margin_start(10)
        ssid_label.set_margin_end(10)
        
        # Icône d'antenne avec taille ajustée
        icon_name = "network-wireless-symbolic"
        icon_name = "network-wireless-signal-excellent-symbolic" if int(signal) > 75 else \
                    "network-wireless-signal-good-symbolic" if int(signal) > 50 else \
                    "network-wireless-signal-ok-symbolic" if int(signal) > 25 else \
                    "network-wireless-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)  # Ajuster la taille de l'icône
        icon.set_margin_start(10)
        
        hbox.pack_start(ssid_label, True, True, 0)
        hbox.pack_start(icon, False, False, 0)
        hbox.connect("button-press-event", self.on_network_clicked)
        
        self.networks_box.pack_start(hbox, False, False, 5)

if __name__ == "__main__":
    win = Gtk.Window()
    win.set_title("Network Configuration")
    win.set_default_size(800, 600)
    win.connect("destroy", Gtk.main_quit)

    network_step = NetworkStep2(None, lambda x: x)
    win.add(network_step)
    win.show_all()

    Gtk.main()
