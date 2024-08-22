import gi
import time
import subprocess
from gi.repository import Gtk, Gdk, GLib
from includes.widget.keyboard import Keyboard

gi.require_version('Gtk', '3.0')


class NetworkStep2(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, margin=0)
        self.parent = parent
        self._ = _

        self.title_label_dialog = Gtk.Label()
        self.cancel_button = Gtk.Label()
        self.connect_button = Gtk.Label()
        self.ok_button_dialog = Gtk.Label()
        self.cancel_button_dialog = Gtk.Label()
        # Créer la page 2
        self.page2 = self.create_page2()
        self.pack_start(self.page2, True, True, 0)

        # Ajouter un style CSS
        self.add_custom_css()

    def create_page2(self):
        page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, margin=0)
        page2.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))  # Fond noir

        # Conteneur pour le titre et les boutons
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
        self.title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        self.title_label.get_style_context().add_class('title')
        self.title_label.set_xalign(0.5)  # Centrer le texte horizontalement
        header_box.pack_start(self.title_label, True, True, 0)

        # Conteneur pour les boutons Skip et Wi-Fi
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Bouton Skip
        self.skip_button = Gtk.Button(label=self._("Skip"))
        self.skip_button.get_style_context().add_class('button')
        self.skip_button.connect("clicked", self.on_skip_clicked)
        header_box.pack_start(self.skip_button, False, False, 0)

        # Bouton pour activer/désactiver le Wi-Fi
        self.wifi_switch = Gtk.Switch()
        self.wifi_switch.set_active(True)
        self.wifi_switch.connect("state-set", self.on_wifi_switch_toggled)
        self.wifi_switch.get_style_context().add_class('wifi-switch')
        self.wifi_switch.set_size_request(100, -1)  # Ajuster la largeur du bouton
        action_box.pack_start(self.wifi_switch, False, False, 0)

        # Ajouter action_box à header_box
        header_box.pack_start(action_box, False, False, 0)

        page2.pack_start(header_box, False, False, 0)

        # Conteneur principal pour la liste des réseaux et le bouton de rafraîchissement
        network_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        network_container.set_hexpand(True)
        network_container.set_vexpand(True)

        # Conteneur pour les réseaux Wi-Fi
        self.networks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.networks_box.set_hexpand(True)
        self.networks_box.set_vexpand(True)

        # Ajouter la Box à une ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.networks_box)

        network_container.pack_start(self.scrolled_window, True, True, 0)
        # Image cliquable avec changement d'apparence
        self.refresh_image = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.DIALOG)
        self.refresh_image.set_pixel_size(48)  # Ajuster la taille de l'icône

        self.refresh_button = Gtk.Button()
        self.refresh_button.set_image(self.refresh_image)
        self.refresh_button.set_tooltip_text(self._("Refresh"))
        self.refresh_button.set_size_request(60, 60)  # Ajuster la taille du bouton
        self.refresh_button.get_style_context().add_class('refresh-button')  # Utiliser une classe CSS spécifique
        
        self.refresh_button.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))
        self.refresh_button.set_margin_start(10)
        self.refresh_button.set_valign(Gtk.Align.START)  # Aligner l'icône vers le haut
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        network_container.pack_start(self.refresh_button, False, False, 0)

        page2.pack_start(network_container, True, True, 0)

        # Icône de chargement
        self.loading_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.DIALOG)
        self.loading_icon.set_pixel_size(64)
        self.loading_icon.set_visible(False)  # Cacher l'icône de chargement par défaut

        self.loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.loading_box.set_halign(Gtk.Align.CENTER)
        self.loading_box.set_valign(Gtk.Align.CENTER)
        self.loading_box.pack_start(self.loading_icon, True, True, 0)

        # Conteneur pour les boutons de navigation
        #nav_box = Gtk.Box(spacing=10, margin_top=0)
        #nav_box.set_halign(Gtk.Align.END)

        #skip_button = Gtk.Button(label=self._("Skip"))
        #skip_button.get_style_context().add_class('button')
        #skip_button.connect("clicked", self.on_skip_clicked)
        #nav_box.pack_start(skip_button, False, False, 0)
        #disconnect_button = Gtk.Button(label=self._("Disconnect Wi-Fi"))
        #disconnect_button.get_style_context().add_class('button')
        #disconnect_button.connect("clicked", self.on_disconnect_wifi_clicked)
        #nav_box.pack_start(disconnect_button, False, False, 0)

        #page2.pack_start(nav_box, False, False, 10)

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
        /* CSS pour le bouton de rafraîchissement */
        .refresh-button {
            border: none; /* Supprimer le contour blanc par défaut */
            background-color: transparent; /* Fond transparent pour éviter les contours */
            padding: 0; /* Supprimer le padding */
            border-radius: 8px; /* Bord arrondi si nécessaire */
            margin: 20px;
            margin-right: 50px;
        }

        .refresh-button:hover {
            border: 2px solid #dcdcdc; /* Contour gris au survol */
        }

        .refresh-button:active {
            border: 2px solid #a0a0a0; /* Contour gris plus foncé lors du clic */
        }

        /* Style pour le bouton Wi-Fi */
        .wifi-switch {
            background-color: #008F00; /* Vert foncé pour l'état activé */
        }
        .wifi-switch.active {
            background-color: #008F00; /* Vert foncé pour l'état activé */
        }
        .wifi-switch.inactive {
            background-color: #a0a0a0; /* Gris pour l'état désactivé */
        }
        /* Boutons */
        .custom-button {
            background-image: none; /* Supprime l'image de fond */
            background-color: #444444; /* Gris foncé */
            color: #ffffff; /* Blanc pour le texte des boutons */
            border-radius: 0px; /* Coins arrondis */
            padding: 15px 30px; /* Espacement interne des boutons */
            border: 1px solid #555555; /* Bordure gris moyen */
            font-size: 24px;
            margin: 16px; /* Espacement externe entre les boutons */
            margin-top: 20px; /* Espacement externe entre les boutons */
            transition: background-color 0.3s ease, transform 0.3s ease; /* Transition douce pour hover et active */
        }

        .custom-button:hover {
            background-color: #555555; /* Gris plus clair au survol */
        }

        .custom-button:active {
            background-color: #333333; /* Gris plus foncé lorsque le bouton est actif */
        }
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
        # Changer l'image pour l'état cliqué
        self.refresh_image = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.DIALOG)
        self.refresh_image.set_pixel_size(48)  # Ajuster la taille de l'icône
        self.refresh_button.set_image(self.refresh_image)
        self.update_wifi_networks
        self.refresh_button.set_sensitive(False)  # Désactiver le bouton pendant le rafraîchissement

        # Simuler le rafraîchissement avec une temporisation
        GLib.timeout_add(1000, self.finish_refresh)  # Appel à finish_refresh après 1 seconde

    def finish_refresh(self):
        # Remettre l'image d'origine et réactiver le bouton
        self.refresh_image = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.DIALOG)
        self.refresh_image.set_pixel_size(48)  # Ajuster la taille de l'icône
        self.refresh_button.set_image(self.refresh_image)
        self.refresh_button.set_sensitive(True)  # Réactiver le bouton
        return False  # Ne pas répéter

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
        self.title_label_dialog = Gtk.Label(label=self._("Enter the password -") + f" {ssid}")
        self.title_label_dialog.set_markup(f'<span size="xx-large" weight="bold" color="white">{self.title_label_dialog.get_text()}</span>')
        self.title_label_dialog.set_margin_top(20)  # Espacement sous le titre
        self.title_label_dialog.set_margin_bottom(0)  # Espacement sous le titre
        content_area.pack_start(self.title_label_dialog, False, False, 0)

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
        translated_message = self._(message)
        dialog = Gtk.Dialog(
            parent=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            title=self._("Confirmation"),
        )
        dialog.set_default_size(400, 200)  # Augmente la taille de la boîte de dialogue

        # Contenu principal de la boîte de dialogue (icône et message)
        content_area = dialog.get_content_area()
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_halign(Gtk.Align.CENTER)

        # Icône
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        icon.set_pixel_size(60)  # Augmente la taille de l'icône
        icon.set_margin_top(30)
        icon.set_margin_bottom(10)
        content_box.pack_start(icon, False, False, 0)

        # Message avec un formatage personnalisé
        message_label = Gtk.Label()
        message_style = "bold" if not success else "normal"
        message_color = "red" if not success else "blue"
        formatted_message = f'<span size="xx-large" weight="{message_style}" foreground="{message_color}">{translated_message}</span>'
        message_label.set_markup(formatted_message)
        message_label.set_margin_bottom(30)
        message_label.set_justify(Gtk.Justification.CENTER)
        content_box.pack_start(message_label, False, False, 0)

        content_area.pack_start(content_box, True, True, 0)

        # Conteneur pour les boutons en bas
        button_box = Gtk.Box(spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        if success:
            self.ok_button_dialog = Gtk.Button(label=self._("Ok"))
            self.ok_button_dialog.get_style_context().add_class("custom-button")
            self.ok_button_dialog.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.OK))
            button_box.pack_start(self.ok_button_dialog, False, False, 0)
        else:
            self.cancel_button_dialog = Gtk.Button(label=self._("Cancel"))
            self.cancel_button_dialog.get_style_context().add_class("custom-button")
            self.cancel_button_dialog.connect("clicked", lambda x: dialog.response(Gtk.ResponseType.CANCEL))
            button_box.pack_start(self.cancel_button_dialog, False, False, 0)

        # Ajouter le bouton à la zone de boutons de la boîte de dialogue
        dialog.get_action_area().pack_start(button_box, False, False, 0)
        dialog.get_action_area().show_all()  # Affiche les boutons

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

    def update_translation(self, _):
        self._ = _
        self.title_label.set_text(self._("Network Select Wi-Fi"))
        self.skip_button.set_label(self._("Skip"))
        self.title_label_dialog.set_label(self._("Enter the password -"))
        self.cancel_button.set_label(self._("Cancel"))
        self.connect_button.set_label(self._("Connect"))
        self.ok_button_dialog.set_label(self._("ok"))
        self.cancel_button_dialog.set_label(self._("Cancel"))



    

if __name__ == "__main__":
    win = Gtk.Window()
    win.set_title("Network Configuration")
    win.set_default_size(800, 500)
    win.connect("destroy", Gtk.main_quit)

    network_step = NetworkStep2(None, lambda x: x)
    win.add(network_step)
    win.show_all()

    Gtk.main()
