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

        # Ajouter un label pour le titre
        self.title_label = Gtk.Label(label="Select your language")
        self.title_label.get_style_context().add_class("title")  # Appliquer la classe CSS pour le label
        self.title_label.set_margin_top(20)
        self.title_label.set_margin_bottom(10)
        self.pack_start(self.title_label, False, False, 10)

        # Créer un conteneur pour les boutons de langue avec une barre de défilement
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_vexpand(True)
        scroll_window.set_hexpand(True)
        
        # Forcer l'affichage des barres de défilement
        scroll_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.pack_start(scroll_window, True, True, 0)

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
        scroll_window.add(self.flowbox)

        # Ajouter les boutons de langue
        self.add_language_buttons()

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
        """Ajouter des boutons pour chaque langue"""
        for code, name in self.languages.items():
            button = Gtk.Button(label=name)
            button.set_size_request(150, 60) 

            # Utiliser une classe CSS spécifique pour le bouton
            button.get_style_context().add_class("button")

            # Stocker l'identifiant de langue dans un attribut normal
            button.language_code = code

            button.connect("clicked", self.on_language_selected)
            self.flowbox.add(button)

    def on_language_selected(self, button):
        """Gérer la sélection d'une langue"""
        selected_language = getattr(button, 'language_code', None)
        if selected_language:
            self.config.set('select_language', 'language', selected_language)
            with open('config/config.conf', 'w') as configfile:
                self.config.write(configfile)
            print(f"Selected language: {selected_language}")

            self.update_application_configs(selected_language)
            self.create_and_translate_files(selected_language)
            self.parent.next_step()

    def update_application_configs(self, language_code):
        """Mettre à jour les fichiers de configuration pour Mainsail et KlipperScreen"""
        mainsail_config_path = '/home/pi/printer_data/config/config.txt'
        klipperscreen_config_path = '/home/pi/printer_data/config/KlipperScreen.conf'

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

    def create_and_translate_files(self, language_code):
        """Créer et traduire les fichiers de langue si nécessaire"""
        locale_dir = 'config/locales'
        lang_dir = os.path.join(locale_dir, f'{language_code}/LC_MESSAGES')
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
            po_file = os.path.join(lang_dir, 'messages.po')
            if not os.path.exists(po_file):
                with open(po_file, 'w') as file:
                    file.write(f'''
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Language: {language_code}\\n"

msgid "Welcome to ConfigFlowX!"
msgstr ""
''')
                print(f"Created new translation file for {language_code}")

    def on_next_clicked(self, button):
        """Passer à l'étape suivante"""
        self.parent.next_step()

    def on_previous_clicked(self, button):
        """Revenir à l'étape précédente"""
        self.parent.previous_step()

    def on_skip_clicked(self, button):
        """Sauter cette étape"""
        self.parent.next_step()
