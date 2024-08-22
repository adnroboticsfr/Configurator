import gi
import os
import configparser
import subprocess
from gi.repository import Gtk, Gdk

gi.require_version('Gtk', '3.0')

class NetworkStep2(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        self._ = _
        self.shift_active = False
        self.symbols_active = False

        # Charger la configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/config.conf')

        # Créer la page 2
        self.page2 = self.create_page2()
        self.pack_start(self.page2, True, True, 0)
        self.update_wifi_networks()

    def create_page2(self):
        page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        page2.set_margin_top(10)
        page2.set_margin_bottom(10)
        page2.set_margin_start(20)
        page2.set_margin_end(20)

        # Titre
        title_label = Gtk.Label(label=self._("Network Select Wi-Fi"))
        title_label.get_style_context().add_class('title')
        title_label.set_halign(Gtk.Align.CENTER)
        title_label.set_margin_bottom(10)
        page2.pack_start(title_label, False, False, 10)

        # ScrolledWindow pour la liste des réseaux Wi-Fi
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_min_content_height(200)  # Fixer une hauteur minimale
        self.scrolled_window.set_min_content_width(300)   # Fixer une largeur minimale
        
        # Conteneur pour les réseaux
        self.network_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.network_box.set_hexpand(True)
        self.network_box.set_vexpand(True)
        self.scrolled_window.add(self.network_box)

        page2.pack_start(self.scrolled_window, True, True, 10)

        # Ajouter les boutons de rafraîchissement et d'activation Wi-Fi en bas
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)

        refresh_button = Gtk.Button(label=self._("Refresh"))
        refresh_button.get_style_context().add_class('button')
        refresh_button.connect("clicked", self.on_refresh_clicked)
        button_box.pack_start(refresh_button, False, False, 0)

        wifi_switch_button = Gtk.Button(label=self._("Enable/Disable Wi-Fi"))
        wifi_switch_button.get_style_context().add_class('button')
        wifi_switch_button.connect("clicked", self.on_wifi_switch_clicked)
        button_box.pack_start(wifi_switch_button, False, False, 0)

        skip_button = Gtk.Button(label=self._("Skip"))
        skip_button.get_style_context().add_class('button')
        skip_button.connect("clicked", self.on_skip_clicked)
        button_box.pack_start(skip_button, False, False, 0)

        page2.pack_start(button_box, False, False, 20)

        return page2

    def update_wifi_networks(self):
        # Obtenir la liste des réseaux Wi-Fi
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE, text=True)
            networks = result.stdout.split('\n')
            self.wifi_networks = [net.split(":") for net in networks if net]
        except Exception as e:
            print(f"Error scanning Wi-Fi networks: {e}")
            self.wifi_networks = []

        # Mettre à jour la Box de réseaux
        self.network_box.foreach(lambda child: self.network_box.remove(child))
        for ssid, security, signal in self.wifi_networks:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.set_hexpand(True)
            row.set_vexpand(False)
            
            # Label du SSID avec texte deux fois plus grand et en gras
            ssid_label = Gtk.Label(label=ssid)
            ssid_label.set_xalign(0)
            ssid_label.set_markup(f'<span size="xx-large" weight="bold">{ssid}</span>')  # Texte deux fois plus grand et en gras

            # Icône de signal Wi-Fi
            icon_name = "network-wireless-signal-excellent-symbolic" if signal == "100" else "network-wireless-symbolic"
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)

            row.pack_start(icon, False, False, 5)  # L'icône est plus proche du texte
            row.pack_start(ssid_label, True, True, 0)
            row.connect("button-press-event", self.on_network_selected)
            self.network_box.pack_start(row, False, False, 0)

        self.network_box.show_all()

    def show_password_dialog(self, ssid):
        # Créer une boîte de dialogue pour la saisie du mot de passe en plein écran
        dialog = Gtk.Dialog(
            title=self._("Enter Wi-Fi Password"),
            parent=self.parent,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
        )
        dialog.set_decorated(False)  # Retirer les bordures de la fenêtre pour un affichage plein écran
        dialog.fullscreen()

        # Ajouter le champ de mot de passe à la boîte de dialogue
        content_area = dialog.get_content_area()
        content_area.set_margin_top(50)
        content_area.set_margin_bottom(50)
        content_area.set_margin_start(50)
        content_area.set_margin_end(50)

        # Titre de la boîte de dialogue
        title_label = Gtk.Label(label=self._("Enter password for {ssid}").format(ssid=ssid))
        title_label.get_style_context().add_class('dialog-title')
        title_label.set_halign(Gtk.Align.CENTER)
        content_area.pack_start(title_label, False, False, 20)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text(self._("Password"))
        self.password_entry.set_visibility(False)  # Masquer le mot de passe
        self.password_entry.set_margin_top(20)
        self.password_entry.set_margin_bottom(20)
        content_area.pack_start(self.password_entry, False, False, 20)

        # Ajouter le clavier virtuel
        self.virtual_keyboard = self.create_virtual_keyboard()
        content_area.pack_start(self.virtual_keyboard, True, True, 10)

        # Ajouter les boutons OK et Annuler, plus larges
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        button_box.set_margin_top(20)

        cancel_button = Gtk.Button(label=self._("Cancel"))
        cancel_button.get_style_context().add_class('button-large')
        cancel_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.CANCEL))
        button_box.pack_start(cancel_button, True, True, 0)

        ok_button = Gtk.Button(label=self._("OK"))
        ok_button.get_style_context().add_class('button-large')
        ok_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.OK))
        button_box.pack_start(ok_button, True, True, 0)

        content_area.pack_start(button_box, False, False, 20)

        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            password = self.password_entry.get_text()
            if self.connect_to_wifi(ssid, password):
                self.show_info_message("Connected successfully!")
                self.parent.next_step()
            else:
                self.show_error_message("Failed to connect. Please check your password and try again.")
        dialog.destroy()

    def create_virtual_keyboard(self):
        # Créer un clavier virtuel adapté avec des lettres plus grandes
        keyboard_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # Mapper les touches pour chaque mode
        self.key_map = {
            'default': [
                '1234567890',
                'qwertyuiop',
                'asdfghjkl',
                'zxcvbnm'
            ],
            'shift': [
                '!"#$%&\'()*+,-./',
                'QWERTYUIOP',
                'ASDFGHJKL',
                'ZXCVBNM'
            ],
            'symbols': [
                '`~@#$%^&*()_+',
                '[]{}\\|;:\'",<.>/?',
                '   ',
                '   '
            ]
        }

        self.current_mode = 'default'
        self.update_keyboard_layout(keyboard_box)
        
        return keyboard_box

    def update_keyboard_layout(self, keyboard_box):
        # Créer le clavier en fonction du mode courant avec des touches plus grandes
        keyboard_box.foreach(lambda child: keyboard_box.remove(child))
        for row in self.key_map[self.current_mode]:
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            for key in row:
                button = Gtk.Button(label=key)
                button.set_size_request(80, 80)
                button.get_style_context().add_class('keyboard-button')
                button.connect("clicked", self.on_key_clicked)
                row_box.pack_start(button, True, True, 0)
            keyboard_box.pack_start(row_box, False, False, 0)

        self.add_control_buttons(keyboard_box)

    def add_control_buttons(self, keyboard_box):
        control_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        shift_button = Gtk.Button(label="Shift")
        shift_button.set_size_request(80, 80)
        shift_button.connect("clicked", self.toggle_shift)
        control_row.pack_start(shift_button, True, True, 0)

        symbols_button = Gtk.Button(label="Symbols")
        symbols_button.set_size_request(80, 80)
        symbols_button.connect("clicked", self.toggle_symbols)
        control_row.pack_start(symbols_button, True, True, 0)

        backspace_button = Gtk.Button(label="Backspace")
        backspace_button.set_size_request(80, 80)
        backspace_button.connect("clicked", self.on_backspace_clicked)
        control_row.pack_start(backspace_button, True, True, 0)

        keyboard_box.pack_start(control_row, False, False, 0)

    def toggle_shift(self, button):
        self.current_mode = 'shift' if self.current_mode == 'default' else 'default'
        self.update_keyboard_layout(self.virtual_keyboard)

    def toggle_symbols(self, button):
        self.current_mode = 'symbols' if self.current_mode != 'symbols' else 'default'
        self.update_keyboard_layout(self.virtual_keyboard)

    def on_key_clicked(self, button):
        key = button.get_label()
        if key != "":
            current_text = self.password_entry.get_text()
            self.password_entry.set_text(current_text + key)

    def on_backspace_clicked(self, button):
        current_text = self.password_entry.get_text()
        self.password_entry.set_text(current_text[:-1])

    def connect_to_wifi(self, ssid, password):
        # Implémenter la connexion au réseau Wi-Fi avec le SSID et le mot de passe fournis
        try:
            result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], check=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Failed to connect to Wi-Fi: {e}")
            return False

    def show_error_message(self, message):
        dialog = Gtk.MessageDialog(
            parent=self.parent,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            message_format=message
        )
        dialog.run()
        dialog.destroy()

    def show_info_message(self, message):
        dialog = Gtk.MessageDialog(
            parent=self.parent,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=message
        )
        dialog.run()
        dialog.destroy()

    def on_network_selected(self, widget, event):
        # Sélection d'un réseau, demander le mot de passe
        ssid = widget.get_children()[1].get_label()
        self.show_password_dialog(ssid)

    def on_refresh_clicked(self, button):
        self.update_wifi_networks()

    def on_wifi_switch_clicked(self, button):
        # Activer/Désactiver le Wi-Fi (fonctionnalité à implémenter selon les besoins)
        pass

    def on_skip_clicked(self, button):
        self.parent.next_step()
