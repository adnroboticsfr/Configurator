import gi
import qrcode
import requests
import logging
from io import BytesIO
from gi.repository import Gtk, GdkPixbuf, Pango

gi.require_version('Gtk', '3.0')

OBICO_LINK_STATUS_MACRO = 'OBICO_LINK_STATUS'

# Simuler une classe Printer pour tester
class Printer:
    def get_gcode_macros(self):
        return ["OBICO_LINK_STATUS", "SOME_OTHER_MACRO"]

class AppConnectStep(Gtk.Box):
    def __init__(self, screen, printer):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.screen = screen
        self.printer = printer
        self._ = lambda x: x  # Simuler une fonction de traduction

        self.init_ui()
        self.activate()

    def init_ui(self):
        # Conteneur principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.pack_start(main_box, True, True, 0)

        # Conteneur de gauche : description
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_box.set_margin_top(10)
        left_box.set_margin_start(10)
        left_box.set_margin_end(5)
        left_box.set_margin_bottom(5)

        self.title_label = Gtk.Label(label=self._("Connectez votre imprimante à Obico"))
        self.title_label.get_style_context().add_class('title')
        left_box.pack_start(self.title_label, False, False, 0)

        self.description = Gtk.Label(label=self._("1. Scannez le code QR pour connecter votre imprimante à Obico."))
        self.description.get_style_context().add_class('text-under-image')
        self.description.set_justify(Gtk.Justification.LEFT)
        self.description.set_line_wrap(True)
        left_box.pack_start(self.description, False, False, 0)

        main_box.pack_start(left_box, True, True, 0)

        # Conteneur de droite : QR Code
        self.qr_image = Gtk.Image()
        main_box.pack_start(self.qr_image, False, False, 0)

        # Boutons de navigation
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_bottom(20)

        self.skip_button = Gtk.Button(label=self._("Passer"))
        self.skip_button.connect("clicked", self.on_skip_clicked)
        button_box.pack_start(self.skip_button, False, False, 0)

        self.back_button = Gtk.Button(label=self._("Retour"))
        self.back_button.connect("clicked", self.on_back_clicked)
        button_box.pack_start(self.back_button, False, False, 0)

        self.pack_end(button_box, False, False, 0)

    def activate(self):
        logging.info('Activation de la connexion')
        
        #if not hasattr(self.printer, 'get_gcode_macros'):
            #raise AttributeError("L'objet 'printer' n'a pas la méthode 'get_gcode_macros'")
        
        #gcode_macros = self.printer.get_gcode_macros()

        if True:
            moonraker_config = self.get_connected_moonraker_config(self.screen)
            moonraker_host = moonraker_config.get('moonraker_host', '127.0.0.1')
            moonraker_port = moonraker_config.get('moonraker_port', 7125)

            url = f'http://{moonraker_host}:{moonraker_port}/printer/objects/query?gcode_macro%20{OBICO_LINK_STATUS_MACRO}'

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logging.info(data)
            print(data)

            is_linked = data.get('result', {}).get('status', {}).get(f'gcode_macro {OBICO_LINK_STATUS_MACRO}', {}).get('is_linked')
            one_time_passcode = data.get('result', {}).get('status', {}).get(f'gcode_macro {OBICO_LINK_STATUS_MACRO}', {}).get('one_time_passcode')
            one_time_passlink = data.get('result', {}).get('status', {}).get(f'gcode_macro {OBICO_LINK_STATUS_MACRO}', {}).get('one_time_passlink')
            if is_linked is None:
                self.display_setup_guide_qr_code()
            elif is_linked:
                self.display_linked_status()
            elif one_time_passcode and one_time_passlink:
                self.display_link_qr_code(one_time_passcode, one_time_passlink)
            else:
                self.display_setup_guide_qr_code()

    def display_linked_status(self):
        self.update_qr_code('https://app.yumi-lab.com/')
        self.description.set_label(self._("Imprimante connectée à Obico. Scannez le code QR pour en savoir plus."))

    def display_link_qr_code(self, one_time_passcode, one_time_passlink):
        self.update_qr_code(one_time_passlink)
        self.description.set_label(self._(f"Scannez pour lier Obico ou entrez le code ci-dessous dans l'application Obico :\n\n{one_time_passcode}"))

    def display_setup_guide_qr_code(self):
        self.update_qr_code('https://obico.io/docs/user-guides/klipper-setup/')
        self.description.set_label(self._("Scannez pour configurer Obico."))

    def update_qr_code(self, link_url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(link_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')

        loader = GdkPixbuf.PixbufLoader.new_with_type('png')
        loader.write(img_byte_arr.getvalue())
        loader.close()
        pixbuf = loader.get_pixbuf()

        self.qr_image.set_from_pixbuf(pixbuf)

    def on_skip_clicked(self, button):
        # Code pour passer l'étape, par exemple : self.parent.next_step()
        print("Passer l'étape")

    def on_back_clicked(self, button):
        # Code pour revenir à l'étape précédente, par exemple : self.parent.previous_step()
        print("Retour à l'étape précédente")

    def get_connected_moonraker_config(self, screen):
        # Simulation de la récupération de la configuration Moonraker
        return {
            'moonraker_host': '127.0.0.1',
            'moonraker_port': 7125
        }

# Exemple d'utilisation
if __name__ == "__main__":
    screen = None  # Remplacez par l'objet réel représentant votre écran
    printer_instance = Printer()  # Instance de la classe Printer
    app_step = AppConnectStep(screen, printer_instance)
    Gtk.main()
