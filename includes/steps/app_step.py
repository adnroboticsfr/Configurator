import gi
import configparser
import os
import qrcode  # Vous devez installer qrcode avec pip install qrcode[pil]
from gi.repository import Gtk, Gdk, GdkPixbuf

gi.require_version('Gtk', '3.0')

class AppConnectStep(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        self._ = _

        # Conteneur principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.pack_start(main_box, True, True, 0)

        # Conteneur de gauche : description
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_box.set_margin_top(10)
        left_box.set_margin_start(10)
        left_box.set_margin_end(5)
        left_box.set_margin_bottom(5)

        # Conteneur pour le titre et le bouton retour
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Label pour le titre
        self.title_label = Gtk.Label(label=self._("APP Connect"))
        self.title_label.get_style_context().add_class('title')
        main_box.pack_start(self.title_label, True, True, 0)

        description = Gtk.Label(label=self._("1. Scan the QR code to connect to App Connect, or visit app.connect.com\n\n2. Log in, Code: RXXXXXXXXX5"))
        description.get_style_context().add_class('text-under-image')
        description.set_justify(Gtk.Justification.LEFT)
        description.set_line_wrap(True)
        left_box.pack_start(description, False, False, 0)
        main_box.pack_start(left_box, True, True, 0)

        # Génération du QR Code
        qr_code = qrcode.make("https://app.yumi-lab.com/accounts/login/?code=RXXXXXXXXX5")
        qr_code_path = "/tmp/app_connect_qr.png"
        qr_code.save(qr_code_path)

        # Conteneur de droite : QR Code
        if os.path.exists(qr_code_path):
            qr_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(qr_code_path, 150, 150, True)
            qr_image = Gtk.Image.new_from_pixbuf(qr_pixbuf)
            main_box.pack_start(qr_image, False, False, 0)

        # Boutons de navigation en bas à droite
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)  # Aligner les boutons à droite
        button_box.set_margin_bottom(20)  # Ajouter une marge en bas

        skip_button = Gtk.Button(label=self._("Skip"))
        skip_button.connect("clicked", self.on_skip_clicked)
        skip_button.get_style_context().add_class('button')
        skip_button.set_halign(Gtk.Align.END)

        back_button = Gtk.Button(label=self._("Back"))
        back_button.get_style_context().add_class('button')
        back_button.connect("clicked", self.on_back_clicked)
        back_button.set_halign(Gtk.Align.END)

        button_box.pack_start(back_button, False, False, 0)
        button_box.pack_start(skip_button, False, False, 0)

        # Ajouter les boutons en bas de la boîte principale
        self.pack_end(button_box, False, False, 0)

    def on_skip_clicked(self, button):
        self.parent.next_step()

    def on_back_clicked(self, button):
        self.parent.previous_step()
