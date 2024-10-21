import gi
import configparser
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango

class SuccessStep(Gtk.Box):
    def __init__(self, app, step_container=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.app = app
        self.step_container = step_container
        self.create_success_page()

    def create_success_page(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.pack_start(main_box, True, True, 0)

        # Title and back button container
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))  # Gray background
        title_box.set_margin_top(16)
        title_box.set_margin_bottom(12)
        title_box.set_margin_start(10)
        title_box.set_margin_end(10)

        # Back button
        #back_button = Gtk.Button(label="<")
        #back_button.connect("clicked", self.on_back_clicked)
        #back_button.get_style_context().add_class('button')
        #title_box.pack_start(back_button, False, False, 0)

        # Title label
        self.title_label = Gtk.Label(label="Configuration")
        self.title_label.get_style_context().add_class('title')
        self.title_label.set_xalign(0.5)  # Center text horizontally
        title_box.pack_start(self.title_label, True, True, 0)

        # Add the title container to the main box
        main_box.pack_start(title_box, False, False, 0)

        # Content box for success message
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_box.set_halign(Gtk.Align.CENTER)
        content_box.set_valign(Gtk.Align.CENTER)

        description_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        description_box.set_halign(Gtk.Align.CENTER)

        check_icon = Gtk.Image.new_from_file("assets/img/check_icon.png")
        description_box.pack_start(check_icon, False, False, 0)

        self.description = Gtk.Label(label="Configuration successful!")
        self.description.get_style_context().add_class('description-label')
        self.description.set_justify(Gtk.Justification.LEFT)
        self.description.set_line_wrap(True)
        self.description.modify_font(Pango.FontDescription("Bold 24"))

        description_box.pack_start(self.description, True, True, 0)
        content_box.pack_start(description_box, False, False, 10)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
        button_box.set_halign(Gtk.Align.CENTER)

        close_button = Gtk.Button(label="Confirm")
        close_button.get_style_context().add_class('button1')
        close_button.set_size_request(150, -1)
        close_button.connect("clicked", self.on_close_button_clicked)

        close_button.set_margin_top(14)
        close_button.set_margin_bottom(14)

        button_box.pack_start(close_button, True, True, 0)
        content_box.pack_start(button_box, False, False, 10)

        main_box.pack_start(content_box, True, True, 0)

    def on_back_clicked(self, button):
        """Handle back button click to return to the previous step."""
        self.app.previous_step()

    def on_close_button_clicked(self, button):
        """Handle the close button click to restart KlipperScreen."""
        self.complete_setup_mode()
        self.restart_klipperscreen()

    def complete_setup_mode(self):
        print("Setup mode completed. Restart the application to apply changes.")

        # Destroy the success page if it's displayed
        if self.step_container:
            for widget in self.step_container.get_children():
                widget.destroy()  # This should remove all widgets from the container

    def restart_klipperscreen(self):
        """Restart KlipperScreen."""
        subprocess.run(["sudo","systemctl", "restart", "KlipperScreen.service"])  # Adjust as necessary for your environment

