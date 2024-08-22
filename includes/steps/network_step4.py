import gi
import subprocess
from gi.repository import Gtk, Gdk

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

        # Ajouter un style CSS
        self.add_custom_css()

    def create_page2(self):
        page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin=20)

        # Conteneur pour le titre et le bouton rafraîchir
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)


        # Label du titre
        title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        title_label.get_style_context().add_class('title')
        title_label.set_margin_bottom(20)
        header_box.pack_start(title_label, True, True, 0)

        # Bouton rafraîchir avec icône
        refresh_button = Gtk.Button()
        refresh_button.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.BUTTON))
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

    def add_custom_css(self):
        css_provider = Gtk.CssProvider()
        css_data = """
        /* Style pour les boutons réseau */

        """
        css_provider.load_from_data(css_data.encode('utf-8'))

        # Appliquer le CSS à l'écran par défaut
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

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

    def on_network_clicked(self, button):
        ssid = button.get_label()
        self.show_password_dialog(ssid)


    def show_password_dialog(self, ssid):
        # Créer une boîte de dialogue en plein écran
        dialog = Gtk.Dialog(
            title=self._("Enter Password"),
            parent=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        dialog.set_decorated(False)  # Supprimer les bordures et la barre de titre
        dialog.fullscreen()  # Mettre la boîte de dialogue en plein écran

        # Contenu de la boîte de dialogue
        content_area = dialog.get_content_area()
        content_area.set_spacing(20)  # Espacement entre les widgets

        # Titre
        title_label = Gtk.Label(label=self._("Enter the password for network:") + f" {ssid}")
        title_label.set_markup(f"<b>{title_label.get_text()}</b>")
        title_label.set_margin_bottom(10)  # Espacement sous le titre
        content_area.pack_start(title_label, False, False, 0)

        # Champ de saisie pour le mot de passe
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(True)
        self.password_entry.set_placeholder_text(self._("Password"))
        self.password_entry.set_margin_bottom(10)  # Espacement sous le champ de texte
        self.password_entry.set_size_request(400, 50)  # Ajuster la taille du champ de texte
        content_area.pack_start(self.password_entry, False, False, 0)

        # Configuration du clavier virtuel
        self.shift_active = False  # Suivi de l'état du Shift
        self.keyboard = self.create_virtual_keyboard()
        keyboard_box = Gtk.Box()
        keyboard_box.set_halign(Gtk.Align.CENTER)
        keyboard_box.pack_start(self.keyboard, False, False, 0)
        content_area.pack_start(keyboard_box, True, True, 0)

        # Boutons OK et Annuler
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)

        ok_button = Gtk.Button(label=Gtk.STOCK_OK, use_stock=True)
        ok_button.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.OK))
        button_box.pack_start(ok_button, False, False, 0)

        cancel_button = Gtk.Button(label=Gtk.STOCK_CANCEL, use_stock=True)
        cancel_button.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.CANCEL))
        button_box.pack_start(cancel_button, False, False, 0)

        content_area.pack_start(button_box, False, False, 10)

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
                button = Gtk.Button(label=key.upper() if self.shift_active else key.lower())
                button.set_size_request(60, 60)  # Ajuster la taille des touches
                button.get_style_context().add_class('keyboard-key')
                button.connect("clicked", self.on_keyboard_key_clicked)
                key_row.pack_start(button, False, False, 0)
            keyboard.pack_start(key_row, False, False, 0)

        special_keys = Gtk.Box(spacing=2)
    
        # Icône pour la touche Shift
        shift_button = Gtk.Button()
        shift_icon = Gtk.Image.new_from_icon_name("format-text-italic-symbolic", Gtk.IconSize.BUTTON)
        shift_button.set_image(shift_icon)
        shift_button.set_size_request(80, 60)
        shift_button.get_style_context().add_class('keyboard-key')
        shift_button.connect("clicked", self.on_shift_clicked)
        special_keys.pack_start(shift_button, False, False, 0)

        space_button = Gtk.Button(label="Space")
        space_button.set_size_request(200, 60)
        space_button.get_style_context().add_class('keyboard-key')
        space_button.connect("clicked", self.on_space_clicked)
        special_keys.pack_start(space_button, False, False, 0)

        backspace_button = Gtk.Button()
        backspace_icon = Gtk.Image.new_from_icon_name("edit-clear-symbolic", Gtk.IconSize.BUTTON)
        backspace_button.set_image(backspace_icon)
        backspace_button.set_size_request(80, 60)
        backspace_button.get_style_context().add_class('keyboard-key')
        backspace_button.connect("clicked", self.on_backspace_clicked)
        special_keys.pack_start(backspace_button, False, False, 0)

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
            command = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password]
            subprocess.run(command, check=True)
            print(f"Connecting to {ssid} with password.")
        except subprocess.CalledProcessError as e:
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

        # Bouton pour le SSID avec styles personnalisés
        ssid_button = Gtk.Button()
        ssid_label = Gtk.Label()
        ssid_label.set_markup(f'<span color="grey">{ssid}</span>')  # Couleur du texte en gris
        ssid_button.add(ssid_label)
        ssid_button.get_style_context().add_class('network-button')  # Appliquer le style CSS
        ssid_button.connect("clicked", self.on_network_clicked)
        
        # Icône d'antenne avec taille ajustée
        icon_name = "network-wireless-symbolic"
        icon_name = "network-wireless-signal-excellent-symbolic" if int(signal) > 75 else \
                    "network-wireless-signal-good-symbolic" if int(signal) > 50 else \
                    "network-wireless-signal-ok-symbolic" if int(signal) > 25 else \
                    "network-wireless-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)  # Utiliser une taille plus grande
        icon.set_margin_start(10)
        
        hbox.pack_start(ssid_button, True, True, 0)
        hbox.pack_start(icon, False, False, 0)
        
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
