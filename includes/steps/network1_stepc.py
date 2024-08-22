import gi
import time
import subprocess
from gi.repository import Gtk, Gdk
from includes.widget.keyboard import Keyboard

gi.require_version('Gtk', '3.0')

class NetworkStep2(Gtk.Box):
    def __init__(self, parent, _):
        self.set_default_size(800,500)
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, margin=0)
        self.parent = parent
        self._ = _

        # Créer la page 2
        self.page2 = self.create_page2()
        self.pack_start(self.page2, True, True, 0)

        # Ajouter un style CSS
        self.add_custom_css()

    def create_page2(self):
        page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, margin=0)

        # Conteneur pour le titre et le bouton de retour
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))  # Couleur de fond #222222
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(12)
        header_box.set_margin_start(10)
        header_box.set_margin_end(10)

        # Bouton de retour
        back_button = Gtk.Button(label=self._("<"))
        back_button.get_style_context().add_class('button')
        back_button.connect("clicked", self.on_back_clicked)
        header_box.pack_start(back_button, False, False, 0)

        # Label du titre
        title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        title_label.get_style_context().add_class('title')
        title_label.set_xalign(0.5)  # Centrer le texte horizontalement
        header_box.pack_start(title_label, True, True, 0)

        # Icône de rafraîchissement plus grande avec bordure
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.DIALOG)
        refresh_icon.set_pixel_size(48)  # Ajuster la taille de l'icône

        # EventBox avec image pour rafraîchir
        refresh_event_box = Gtk.EventBox()
        refresh_event_box.add(refresh_icon)
        refresh_event_box.set_tooltip_text(self._("Refresh"))
        refresh_event_box.get_style_context().add_class('refresh-icon-box')
        refresh_event_box.connect("button-press-event", self.on_refresh_clicked)
        header_box.pack_start(refresh_event_box, False, False, 0)

        # Bouton pour activer/désactiver le Wi-Fi
        self.wifi_switch = Gtk.Switch()
        self.wifi_switch.set_active(True)
        self.wifi_switch.connect("state-set", self.on_wifi_switch_toggled)
        self.wifi_switch.get_style_context().add_class('wifi-switch')
        header_box.pack_start(self.wifi_switch, False, False, 0)

        page2.pack_start(header_box, False, False, 0)

        # Conteneur principal pour les réseaux Wi-Fi
        self.networks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.networks_box.set_hexpand(True)
        self.networks_box.set_vexpand(True)

        # Ajouter la Box à une ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.networks_box)

        page2.pack_start(self.scrolled_window, True, True, 0)

        # Icône de chargement
        self.loading_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.DIALOG)
        self.loading_icon.set_pixel_size(64)
        self.loading_icon.set_visible(False)  # Cacher l'icône de chargement par défaut

        self.loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.loading_box.set_halign(Gtk.Align.CENTER)
        self.loading_box.set_valign(Gtk.Align.CENTER)
        self.loading_box.pack_start(self.loading_icon, True, True, 0)

        # Conteneur pour les boutons de navigation
        nav_box = Gtk.Box(spacing=10, margin_top=0)
        nav_box.set_halign(Gtk.Align.END)

        skip_button = Gtk.Button(label=self._("Skip"))
        skip_button.get_style_context().add_class('button')
        skip_button.connect("clicked", self.on_skip_clicked)
        nav_box.pack_start(skip_button, False, False, 0)
        disconnect_button = Gtk.Button(label=self._("Disconnect Wi-Fi"))
        disconnect_button.get_style_context().add_class('button')
        disconnect_button.connect("clicked", self.on_disconnect_wifi_clicked)
        nav_box.pack_start(disconnect_button, False, False, 0)

        page2.pack_start(nav_box, False, False, 10)

        # Initialiser les réseaux Wi-Fi
        self.update_wifi_networks()

        return page2

    def add_custom_css(self):
        css_provider = Gtk.CssProvider()
        css_data = """
        /* Style pour les éléments réseau */
        .network-item-box {
            background-color: transparent; /* Fond transparent */
            border-radius: 0px; /* Coins non arrondis */
            padding: 10px 20px; /* Espacement interne */
            border: 1px solid transparent; /* Suppression de la bordure */
            transition: background-color 0.3s ease; /* Transition douce pour hover */
            font-size: 30px;
            color: #FFFFFF;
            font-weight: bold;
        }
        .network-item-box:hover {
            background-color: #555555; /* Couleur de fond au survol */
        }
        .network-separator {
            background-color: #666666; /* Couleur de la barre séparatrice */
            margin: 5px 0; /* Espacement autour de la barre séparatrice */
        }
        /* Style pour l'EventBox contenant l'icône de rafraîchissement */
        .refresh-icon-box {
            background-color: #444444;
            border: 2px solid #444444; /* Bordure noire de 2 pixels */
            border-radius: 0px; /* Coins non arrondis */
            padding: 5px; /* Espacement entre la bordure et le contenu */
        }
        /* Style pour le bouton Wi-Fi */
        .wifi-switch {
            /*background-color: #008F00;*/ /* Vert foncé pour l'état activé */
        }
        .wifi-switch.active {
            background-color: #008F00; /* Vert foncé pour l'état activé */
        }
        .wifi-switch.inactive {
            background-color: #a0a0a0; /* Gris pour l'état désactivé */
        }
        """
        css_provider.load_from_data(css_data.encode('utf-8'))

        # Appliquer le CSS à l'écran par défaut
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def show_loading(self):
        self.scrolled_window.add(self.loading_box)
        self.loading_box.show_all()

    def hide_loading(self):
        self.loading_box.hide()
        self.scrolled_window.remove(self.loading_box)

    def on_back_clicked(self, button):
        self.parent.previous_step()

    def on_skip_clicked(self, button):
        self.parent.next_step()

    def on_refresh_clicked(self, widget, event):
        self.update_wifi_networks()

    def on_disconnect_wifi_clicked(self, button):
        try:
            subprocess.run(['nmcli', 'radio', 'wifi', 'off'], check=True)
            print("Wi-Fi désactivé.")
            self.update_wifi_networks()  # Mettre à jour l'interface pour refléter l'état
        except subprocess.CalledProcessError as e:
            print(f"Échec de la déconnexion du Wi-Fi : {e}")

    def on_wifi_switch_toggled(self, switch, state):
        if state:
            subprocess.run(['nmcli', 'radio', 'wifi', 'on'],  check=False)
            time.sleep(2.5) 
            self.update_wifi_networks()
            self.scrolled_window.show_all()
            self.wifi_switch.get_style_context().add_class('active')
            self.wifi_switch.get_style_context().remove_class('inactive')
        else:
            subprocess.run(['nmcli', 'radio', 'wifi', 'off'],check=True)
            self.scrolled_window.hide()
            self.wifi_switch.get_style_context().add_class('inactive')
            self.wifi_switch.get_style_context().remove_class('active')

    def on_network_clicked(self, widget):
        # Récupérer le conteneur du label
        hbox = widget.get_child()  # Récupère le conteneur principal (HBox) dans l'EventBox
        ssid_label = hbox.get_children()[0]  # Le label du SSID est le premier enfant du HBox
        ssid = ssid_label.get_text()  # Récupérer le texte du label
        print(f"SSID sélectionné : {ssid}") 
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
        content_area.set_border_width(0)  # Supprimer toute bordure
        content_area.set_spacing(0)  # Espacement entre les widgets

        # Titre
        title_label = Gtk.Label(label=self._("Enter the password for network:") + f" {ssid}")
        title_label.set_markup(f'<span size="xx-large" weight="bold" color="white">{title_label.get_text()}</span>')
        title_label.set_margin_top(20)  # Espacement sous le titre
        title_label.set_margin_bottom(0)  # Espacement sous le titre
        content_area.pack_start(title_label, False, False, 0)

        # Champ de texte pour le mot de passe
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(True)
        self.password_entry.set_placeholder_text(self._("Password"))
        self.password_entry.get_style_context().add_class("password")
        self.password_entry.set_margin_bottom(6)  # Espacement sous le champ de texte
        content_area.pack_start(self.password_entry, False, False, 0)

        # Configuration du clavier virtuel
        self.keyboard = Keyboard(self.on_keyboard_input, self.password_entry)
        keyboard_box = Gtk.Box()
        keyboard_box.set_halign(Gtk.Align.CENTER)
        keyboard_box.pack_start(self.keyboard,  False, False, 0)
        content_area.pack_start(keyboard_box,  False, False, 0)

        # Boutons OK et Annuler
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        button_box.set_margin_bottom(30)
        button_box.set_halign(Gtk.Align.END)

        # Bouton Annuler
        self.cancel_button = Gtk.Button(label=self._("Cancel"))
        #self.cancel_button.set_size_request(150, 50)
        self.cancel_button.get_style_context().add_class('button')

        self.cancel_button.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.CANCEL))
        button_box.pack_start(self.cancel_button, False, False, 0)

        # Bouton Connecter
        self.connect_button = Gtk.Button(label=self._("Connect"))
        #self.connect_button.set_size_request(150, 50)
        self.connect_button.get_style_context().add_class('button')
        self.connect_button.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.OK))
        button_box.pack_start(self.connect_button, False, False, 0)

        content_area.pack_start(button_box, False, False, 0)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            password = self.password_entry.get_text()
            print(f"Password for {ssid}: {password}")
            # Appeler la fonction pour se connecter au réseau avec le mot de passe
            self.connect_to_wifi(ssid, password)
    
        dialog.destroy()

    def on_keyboard_input(self, key):
        if key == "Space":
            current_text = self.password_entry.get_text()
            self.password_entry.set_text(current_text + ' ')
        else:
            current_text = self.password_entry.get_text()
            self.password_entry.set_text(current_text + key)

    def connect_to_wifi(self, ssid, password):
        try:
            # Connexion au réseau Wi-Fi
            command = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password]
            subprocess.run(command, stdout=subprocess.PIPE, check=True)
            print(f"Connecting to {ssid} with password.")
            # Afficher un message de confirmation de succès
            self.show_confirmation_dialog(self._("Connection Successful"), "network-wireless-connected-symbolic", True)
            self.parent.next_step()  # Passer à l'étape suivante après confirmation
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect to Wi-Fi: {e}")
            # Afficher un message d'échec
            self.show_confirmation_dialog(self._("Connection Failed"), "dialog-error-symbolic", False)

    def show_confirmation_dialog(self, message, icon_name, success):
        dialog = Gtk.Dialog(
            parent=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            title=self._("Confirmation"),
        )
        dialog.set_default_size(400, 200)  # Augmente la taille de la boîte de dialogue

        # Contenu de la boîte de dialogue
        content_area = dialog.get_content_area()

        # Icône
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        icon.set_pixel_size(60)  # Augmente la taille de l'icône
        icon.set_margin_top(30)
        icon.set_margin_bottom(10)

        # Message avec un formatage personnalisé
        message_label = Gtk.Label()
        message_style = "bold" if not success else "normal"
        message_color = "red" if not success else "blue"
        formatted_message = f'<span size="xx-large" weight="{message_style}" foreground="{message_color}">{message}</span>'
        message_label.set_markup(formatted_message)
        message_label.set_justify(Gtk.Justification.CENTER)

        # Bouton OK en gras
        ok_button = dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL) if not success else dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        ok_button.get_style_context().add_class("button")
        ok_button.get_style_context().add_class("bold-button")  # Appliquer un style gras
        ok_button.set_margin_bottom(10)

        # Conteneur pour l'icône et le message
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_halign(Gtk.Align.CENTER)
        box.pack_start(icon, False, False, 0)
        box.pack_start(message_label, False, False, 0)
        content_area.pack_start(box, True, True, 0)

        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("L'utilisateur a cliqué sur OK")
            #self.parent.next_step()
        elif response == Gtk.ResponseType.CANCEL:
            print("L'utilisateur a cliqué sur Annuler")
        # Action d'annulation
        dialog.destroy()

    def update_wifi_networks(self):
        # Afficher l'icône de chargement
        self.show_loading()

        # Vider les éléments existants
        for child in self.networks_box.get_children():
            self.networks_box.remove(child)

        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE, text=True)
            networks = result.stdout.split('\n')
            for net in networks:
                if net:
                    ssid, security, signal = net.split(":")
                    self.create_network_item(ssid, security, signal)  # Appel avec les bons arguments

        except Exception as e:
            print(f"Error scanning Wi-Fi networks: {e}")

        # Cacher l'icône de chargement
        self.hide_loading()

    def create_network_item(self, ssid, security, signal):
        # Conteneur pour l'élément réseau
        network_item_box = Gtk.EventBox()
        network_item_box.get_style_context().add_class('network-item-box')  # Ajouter la classe CSS
        network_item_box.connect("button-press-event", lambda w, e: self.on_network_clicked(w))

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_hexpand(False)
        hbox.set_vexpand(False)

        # Bouton pour le SSID
        ssid_label = Gtk.Label(label=ssid)
        hbox.pack_start(ssid_label, True, True, 0)

        # Icône de signal
        icon_name = "network-wireless-signal-excellent-symbolic" if int(signal) > 75 else \
                    "network-wireless-signal-good-symbolic" if int(signal) > 50 else \
                    "network-wireless-signal-ok-symbolic" if int(signal) > 25 else \
                    "network-wireless-symbolic"
        signal_icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        signal_icon.set_margin_start(10)

        # Icône de sécurité
        if "WPA" in security or "WEP" in security:
            lock_icon = Gtk.Image.new_from_icon_name("changes-prevent", Gtk.IconSize.BUTTON)
            hbox.pack_start(lock_icon, False, False, 0)

        # Ajouter les éléments au HBox
        #hbox.pack_start(security_icon, False, False, 0)
        hbox.pack_start(signal_icon, False, False, 0)
        
        network_item_box.add(hbox)

        # Ajouter la ligne de séparation
        separator = Gtk.HSeparator()
        separator.get_style_context().add_class('network-separator')

        # Ajouter le réseau Wi-Fi à la boîte principale
        self.networks_box.pack_start(network_item_box, False, False, 0)
        self.networks_box.pack_start(separator, False, False, 0)

    def show_loading(self):
        # Créer et afficher l'icône de chargement
        self.loading_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.DIALOG)
        self.loading_icon.set_pixel_size(48)  # Ajuster la taille de l'icône
        self.loading_icon.set_margin_bottom(10)

        self.loading_event_box = Gtk.EventBox()
        self.loading_event_box.add(self.loading_icon)
        self.loading_event_box.set_tooltip_text(self._("Loading..."))
        self.loading_event_box.get_style_context().add_class('refresh-icon-box')
        
        self.networks_box.pack_start(self.loading_event_box, False, False, 0)
        self.networks_box.show_all()

    def hide_loading(self):
        # Cacher et supprimer l'icône de chargement
        if hasattr(self, 'loading_event_box'):
            self.networks_box.remove(self.loading_event_box)
            self.networks_box.show_all()
            del self.loading_event_box

if __name__ == "__main__":
    win = Gtk.Window()
    win.set_title("Network Configuration")
    win.set_default_size(800, 500)
    win.connect("destroy", Gtk.main_quit)

    network_step = NetworkStep2(None, lambda x: x)
    win.add(network_step)
    win.show_all()

    Gtk.main()
