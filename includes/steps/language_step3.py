import gi
import configparser
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class LanguageStep(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        self._ = _

        # Lire le fichier de configuration
        self.config = configparser.ConfigParser()
        self.config.read('config/config.conf')

        # Vérifier si l'étape de sélection de la langue est active
        self.is_active = self.config.getboolean('language', 'active', fallback=True)
        if not self.is_active:
            self.parent.next_step()
            return

        self.columns = self.config.getint('select_language', 'columns', fallback=3)
        self.rows = self.config.getint('select_language', 'rows', fallback=4)
        self.languages = self.get_languages_from_config()

        # Conteneur principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.pack_start(main_box, True, True, 0)

        # Conteneur de gauche : Titre
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        title_box.set_margin_top(20)
        title_box.set_margin_start(20)
        title_box.set_margin_end(20)
        title_box.set_margin_bottom(20)
        title_box.set_halign(Gtk.Align.CENTER)  # Centrer le titre horizontalement

        # Label pour le titre
        self.label = Gtk.Label(label=self._("Selectionner\nla Language"))
        self.label.get_style_context().add_class("title")
        #self.label.set_margin_top(20)
        #self.label.set_margin_bottom(10)
        self.label.set_xalign(0.5)  # Centrer horizontalement
        self.label.set_justify(Gtk.Justification.CENTER)
        title_box.pack_start(self.label, True, True, 0)

        # Ajouter la colonne du titre au conteneur principal
        main_box.pack_start(title_box, False, False, 0)

        # Conteneur pour les boutons de langue avec une barre de défilement
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_vexpand(True)
        scroll_window.set_hexpand(True)
        scroll_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scroll_window, True, True, 0)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('config/themes/theme.css')
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Créer un conteneur de type VBox pour placer les boutons de langue
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_max_children_per_line(self.columns)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll_window.add(self.flowbox)

        self.add_language_buttons()

        # Boîte pour les boutons de navigation
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_margin_top(20)
        button_box.set_margin_bottom(30)  # Marge inférieure pour les boutons
        #button_box.set_halign(Gtk.Align.END)  # Aligner les boutons à droite

        # Boutons de navigation
        #self.skip_button = Gtk.Button(label=self._("Skip"))
        #self.skip_button.connect("clicked", self.on_skip_clicked)
        #self.skip_button.get_style_context().add_class('button')
        #button_box.pack_start(self.skip_button, False, False, 0)

        #self.back_button = Gtk.Button(label=self._("Back"))
        #self.back_button.connect("clicked", self.on_back_clicked)
        #self.back_button.get_style_context().add_class('button')
        #button_box.pack_start(self.back_button, False, False, 0)

        # Ajouter les boutons en bas de la boîte principale
        self.pack_end(button_box, False, False, 0)

        self.show_all()

    def get_languages_from_config(self):
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
        for code, label in self.languages.items():
            button = Gtk.Button(label=label)
            button.set_size_request(200, 80)  # Taille fixe des boutons
            button.get_style_context().add_class("language-button")
            button.connect("clicked", self.on_language_button_clicked, code)
            self.flowbox.add(button)

    def on_language_button_clicked(self, button, language_code):
        self.config.set('main', 'language', language_code)
        with open('config/config.conf', 'w') as configfile:
            self.config.write(configfile)
        self.parent.setup_translation(language_code)  # Mettre à jour la langue en temps réel
        self.update_application_configs(language_code)
        self.parent.next_step()

    def on_skip_clicked(self, button):
        self.parent.next_step()

    def on_back_clicked(self, button):
        self.parent.previous_step()

    def convert_language_code_klipperScreen(self, language_code):
        # Liste des exceptions où le code de langue doit rester inchangé
        exceptions = ['zh_CN']
        if language_code in exceptions:
            return language_code
        else:
            # Diviser la chaîne locale par le tiret bas ('_') et prendre la première partie
            return language_code.split('_')[0]
        
    def update_application_configs(self, language_code):
        """Mettre à jour les fichiers de configuration pour Mainsail et KlipperScreen"""
        mainsail_config_path = '/home/pi/printer_data/config/config.txt'
        klipperscreen_config_path = '/home/pi/printer_data/config/KlipperScreen.conf'
        language_code = self.convert_language_code_klipperScreen(language_code)
        # Mettre à jour le fichier de configuration de KlipperScreen
        if os.path.exists(klipperscreen_config_path):
            with open(klipperscreen_config_path, 'r') as file:
                lines = file.readlines()
            section_found = False
            language_line_found = False
            temp_file_path = klipperscreen_config_path + '.tmp'            
            with open(temp_file_path, 'w') as temp_file:
                in_main_section = False
                for line in lines:
                    if line.strip() == "#~# --- Do not edit below this line. This section is auto generated --- #~#":
                        temp_file.write(line)
                        in_main_section = False
                        continue
                   
                    if line.strip().startswith("#~# [main]"):
                        in_main_section = True
                        section_found = True
                    # Modifier ou ajouter la ligne de langue
                    if in_main_section and line.strip().startswith("#~# language"):
                        language_line_found = True
                        temp_file.write(f"#~# language = {language_code}\n")
                    else:
                        temp_file.write(line)                        
                if not section_found:
                    temp_file.write("#~# --- Do not edit below this line. This section is auto generated --- #~#\n")
                    temp_file.write("#~#\n")
                    temp_file.write("#~# [main]\n")
                    temp_file.write(f"#~# language = {language_code}\n")
                elif not language_line_found and in_main_section:
                    temp_file.write(f"#~# language = {language_code}\n")  
            # Remplacer le fichier original par le fichier temporaire
            os.replace(temp_file_path, klipperscreen_config_path)
