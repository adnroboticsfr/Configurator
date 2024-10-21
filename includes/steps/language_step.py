import gi
import configparser
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class LanguageStep(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent

        # Lire le fichier de configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/config.conf')

        # Vérifier si l'étape de sélection de la langue est active
        self.is_active = self.config.getboolean('language', 'active', fallback=True)
        if not self.is_active:
            self.parent.next_step()  # Passer immédiatement à l'étape suivante si cette étape n'est pas active
            return

        # Obtenir les paramètres de configuration pour le nombre de colonnes et de lignes
        self.columns = self.config.getint('select_language', 'columns', fallback=3)
        self.rows = self.config.getint('select_language', 'rows', fallback=4)

        # Obtenir la liste des langues depuis le fichier de configuration
        self.languages = self.get_languages_from_config()

        # Initialiser la langue par défaut depuis le fichier de configuration
        self.default_language = self.config.get('main', 'language', fallback='en')

        # Créer un conteneur principal
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.pack_start(self.main_box, True, True, 0)

        # Ajouter un label pour le titre
        self.title_label = Gtk.Label(label="Select Language")
        self.title_label.get_style_context().add_class("title")  # Appliquer la classe CSS pour le label
        self.title_label.set_margin_bottom(6)
        self.main_box.pack_start(self.title_label, False, False, 10)

        # Créer un conteneur pour les boutons de langue avec une barre de défilement
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.main_box.pack_start(scroll_window, True, True, 0)

        # Appliquer les styles personnalisés pour la barre de défilement
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('config/themes/theme.css')  # Charger les styles depuis le fichier CSS
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Utiliser Gtk.FlowBox pour organiser les boutons
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_max_children_per_line(self.columns)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_margin_bottom(30)
        scroll_window.add(self.flowbox)

        # Ajouter les boutons de langue
        self.add_language_buttons()

        # Mettre à jour la langue sélectionnée visuellement
        self.update_selected_language()

        self.show_all()

    def get_languages_from_config(self):
        """Obtenir la liste des langues à partir du fichier de configuration"""
        languages = {}
        try:
            language_entries = self.config.get('select_language', 'additional_languages', fallback='').split(', ')
            for entry in language_entries:
                if ':' in entry:
                    key, value = entry.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        languages[key] = value
        except Exception as e:
            print(f"Error getting languages: {e}")
        return languages

    def add_language_buttons(self):
        """Ajouter les boutons de langue avec la mise en surbrillance de la langue par défaut."""
        self.buttons = {}  # Dictionnaire pour stocker les boutons
        
        for code, label in self.languages.items():
            button = Gtk.Button(label=label)
            button.set_size_request(200, 80)  # Taille fixe des boutons
            button.get_style_context().add_class("language-button")

            # Si la langue actuelle est celle par défaut, appliquer la classe 'selected'
            if code == self.default_language:
               button.get_style_context().add_class('selected')

            # Connecter le signal de clic pour mettre à jour la langue
            button.connect("clicked", self.on_language_button_clicked, code)
            self.flowbox.add(button)
            self.buttons[code] = button  # Stocker le bouton pour référence ultérieure

    def update_selected_language(self):
        """Mettre à jour visuellement la langue sélectionnée en fonction de la configuration enregistrée."""
        # Relire la langue actuellement enregistrée dans la configuration
        self.default_language = self.config.get('main', 'language', fallback='en')

        # Mettre à jour la mise en surbrillance des boutons
        for code, button in self.buttons.items():
            if code == self.default_language:
                button.get_style_context().add_class('selected')  # Mettre en surbrillance
            else:
                button.get_style_context().remove_class('selected')  # Retirer la surbrillance

    def on_language_button_clicked(self, button, language_code):
        # Mettre à jour la langue dans le fichier de configuration si elle est différente
        if language_code != self.default_language:
            self.config.set('main', 'language', language_code)
            with open('config/config.conf', 'w') as configfile:
                self.config.write(configfile)

            # Mettre à jour la langue dans l'application
            self.parent.setup_translation(language_code)
            self.update_application_configs(language_code)

            # Mettre à jour la langue par défaut
            self.default_language = language_code

        # Mettre à jour visuellement la sélection
        self.update_selected_language()

        # Passer à l'étape suivante
        self.parent.next_step()

    def update_application_configs(self, language_code):
        """Mettre à jour les fichiers de configuration pour Mainsail et KlipperScreen"""
        mainsail_config_path = '/home/pi/printer_data/config/config.txt'
        klipperscreen_config_path = '/home/pi/printer_data/config/KlipperScreen.conf'
        language_code = self.convert_language_code_klipperScreen(language_code)

        # Mettre à jour le fichier de configuration de Mainsail
        if os.path.exists(mainsail_config_path):
            with open(mainsail_config_path, 'a') as configfile:
                configfile.write(f'\nlanguage={language_code}\n')

        # Mettre à jour le fichier de configuration de KlipperScreen
        if os.path.exists(klipperscreen_config_path):
            config = configparser.ConfigParser()
            config.read(klipperscreen_config_path)
            if 'main' not in config:
                config.add_section('main')
            config.set('main', 'language', language_code)
            with open(klipperscreen_config_path, 'w') as configfile:
                config.write(configfile)

        print(f"Updated application configs for language: {language_code}")

    def convert_language_code_klipperScreen(self, language_code):
        # Liste des exceptions où le code de langue doit rester inchangé
        exceptions = ['zh_CN']
        if language_code in exceptions:
            return language_code
        else:
            # Diviser la chaîne locale par le tiret bas ('_') et prendre la première partie
            return language_code.split('_')[0]

    def on_next_clicked(self, button):
        """Passer à l'étape suivante"""
        self.parent.next_step()

    def on_previous_clicked(self, button):
        """Revenir à l'étape précédente"""
        self.parent.previous_step()

    def on_skip_clicked(self, button):
        """Sauter cette étape"""
        self.parent.next_step()
