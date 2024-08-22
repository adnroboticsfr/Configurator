import logging
import os
import configparser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class Keyboard(Gtk.Box):
    langs = ["de", "en", "fr", "es"]

    def __init__(self, close_cb, entry=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.shift_active = False
        self.close_cb = close_cb
        self.keyboard = Gtk.Grid()
        self.keyboard.set_direction(Gtk.TextDirection.LTR)
        self.keyboard.get_style_context().add_class('keyboard-custom')  # Ajouter la classe CSS
        self.entry = entry

        # Lire la langue depuis un fichier de configuration
        language = self.get_language_from_config()
        logging.info(f"Keyboard language: {language}")

        # Initialisation du clavier selon la langue
        self.initialize_keys(language)

        # Création des boutons du clavier
        self.create_buttons()

        self.pallet_nr = 0
        self.set_pallet(self.pallet_nr)
        self.add(self.keyboard)

    def get_language_from_config(self):
        config_path = 'include/config/config.conf'
        if not os.path.exists(config_path):
            return "en"  # Valeur par défaut

        config = configparser.ConfigParser()
        config.read(config_path)
        return config.get('main', 'language', fallback='en_US').split('_')[0]

    def initialize_keys(self, language):
        icon = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON)
        if language == "de":
            self.keys = [
                [
                    ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä"],
                    ["↑", "y", "x", "c", "v", "b", "n", "m", "ẞ", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ü"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä"],
                    ["↑", "Y", "X", "C", "V", "B", "N", "M", "ß", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "#+=", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["[", "]", "{", "}", "#", "%", "^", "*", "+", "="],
                    ["_", "\\", "|", "~", "<", ">", "€", "£", "¥", "•"],
                    ["↑", ".", ",", "?", "!", "'", "º", "¨", "123", "⌫"],
                    ["ABC", " ", "↓"],
                ]
            ]
        elif language == "fr":
            self.keys = [
                [
                    ["a", "z", "e", "r", "t", "y", "u", "i", "o", "p"],
                    ["q", "s", "d", "f", "g", "h", "j", "k", "l", "m"],
                    ["↑", "w", "x", "c", "v", "b", "n", "ç", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
                    ["↑", "W", "X", "C", "V", "B", "N", "Ç", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "ABC", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["[", "]", "{", "}", "#", "%", "^", "*", "+", "="],
                    ["_", "\\", "|", "~", "<", ">", "€", "£", "¥", "•"],
                    ["↑", ".", ",", "?", "!", "'", "º", "Æ", "æ", "⌫"],
                    ["ABC", " ", "↓"],
                ]
            ]
        else:
            self.keys = [
                [
                    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
                    ["↑", "z", "x", "c", "v", "b", "n", "m", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                    ["↑", "Z", "X", "C", "V", "B", "N", "M", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "Ç", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["[", "]", "{", "}", "#", "%", "^", "*", "+", "="],
                    ["_", "\\", "|", "~", "<", ">", "€", "£", "¥", "•"],
                    ["↑", ".", ",", "?", "!", "'", "º", "ç", "ABC", "⌫"],
                    ["abc", " ", "↓"],
                ]
            ]

            if language == "es":
                self.keys[0][1].append("ñ")
                self.keys[1][1].append("Ñ")

    def create_buttons(self):
        self.buttons = [[[] for _ in row] for row in self.keys]
        for p, pallet in enumerate(self.keys):
            for r, row in enumerate(pallet):
                for k, key in enumerate(row):
                    if key == "⌫":
                        button = Gtk.Button(label="⌫")
                        button.set_size_request(40, 40)
                        button.connect('button-press-event', self.handle_backspace)
                    elif key == "↑":
                        button = Gtk.Button(label="↑")
                        button.connect('button-press-event', self.change_pallet, key)
                        #button.set_size_request(40, 40)
                    elif key == "↓":
                        button = Gtk.Button(label="↓")
                        #button.set_size_request(40, 40)
                    elif key in ["123", "abc", "ABC","#+=","↑"]:
                        button = Gtk.Button(label=key)
                        button.connect('button-press-event', self.change_pallet, key)
                        #button.set_size_request(40, 40)
                    else:
                        button = Gtk.Button(label=key)
                    
                    # Connecter les signaux de clic
                    button.connect('button-press-event', self.repeat, key)
                    button.connect('button-release-event', self.release)
                    #button.get_style_context().add_class("keyboard_pad")
                    self.buttons[p][r].append(button)
                    self.keyboard.attach(button, k * 2, r, 2, 1)

    def handle_backspace(self, widget, event):
        if self.entry and isinstance(self.entry, Gtk.Entry):
            cursor_pos = self.entry.get_position()
            if cursor_pos > 0:
                self.entry.delete_text(cursor_pos - 1, cursor_pos)
        return True

    def change_pallet(self, widget, event, key):
        if key == "123":
            self.set_pallet(2)  # Passe au pallet des chiffres et symboles
        elif key == "abc":
            self.set_pallet(0)  # Passe au pallet des lettres minuscules
        elif key == "ABC":
            self.set_pallet(1)  # Passe au pallet des lettres majuscules
        elif key == "#+=":
            self.set_pallet(3)  # Passe au pallet des lettres majuscules 
        elif key == "↑": 
            if self.shift_active == False:   
                self.set_pallet(1)  # Passe au pallet des lettres majuscules
                self.shift_active = True
            else: 
                self.set_pallet(0)  # Passe au pallet des lettres minuscules  
                self.shift_active = False    
        return True

    def set_pallet(self, p):
        # Retirer les widgets existants
        for child in self.keyboard.get_children():
            self.keyboard.remove(child)

        self.pallet_nr = p
        columns = 0
        for r, row in enumerate(self.keys[p][:-1]):
            for k, key in enumerate(row):
                x = k * 2 + 1  if r == 1 else k * 2
                self.keyboard.attach(self.buttons[p][r][k], x, r, 2, 1)
                columns = max(columns, x + 1)
        for k, key in enumerate(self.keys[p][-1]):
            self.keyboard.attach(self.buttons[p][-1][k], k * 2, len(self.keys[p]) - 1, 2, 1)
        self.keyboard.set_column_homogeneous(True)
        self.keyboard.set_row_homogeneous(True)
        self.keyboard.set_row_spacing(5)
        self.keyboard.set_column_spacing(5)
        #self.keyboard.set_size_request(-1, 300)
        self.keyboard.get_style_context().add_class('keyboard-custom')  # Ajouter la classe CSS
        # Assurer que chaque bouton a la même taille
        button_size = 60  # Exemple de taille, à ajuster selon les besoins
        for child in self.keyboard.get_children():
            child.set_size_request(button_size, button_size)
        self.keyboard.show_all()

    def repeat(self, widget, event, key):
        widget.set_relief(Gtk.ReliefStyle.NONE)
        try:
            if self.entry and isinstance(self.entry, Gtk.Entry):
                cursor_pos = self.entry.get_position()
                if key == "⌫":
                    # Vérifier si la position du curseur est valide pour la suppression
                    if cursor_pos > 0:
                        # Supprimer le texte à la position du curseur -1
                        text = self.entry.get_text()
                        # Créer le texte mis à jour en supprimant le caractère précédent
                        self.entry.set_text(text[:cursor_pos - 1] + text[cursor_pos:])
                        # Mettre à jour le texte dans le Gtk.Entry
                        self.entry.set_text(new_text)
                        # Déplacer le curseur d'une position vers la gauche
                        self.entry.set_position(cursor_pos - 1)
                
                else:
                    # Insérer le texte à la position du curseur
                    text = self.entry.get_text()
                    new_text = text[:cursor_pos] + key + text[cursor_pos:]
                    self.entry.set_text(new_text)
                    # Déplacer le curseur d'une position vers la droite
                    self.entry.set_position(cursor_pos + 1)

            elif self.close_cb:
                self.close_cb(key)
        except Exception as e:
            logging.error(f"Erreur lors de l'insertion du texte : {e}")
        return True

    def release(self, widget, event):
        widget.set_relief(Gtk.ReliefStyle.NORMAL)
        return True

    def close(self):
        self.destroy()
