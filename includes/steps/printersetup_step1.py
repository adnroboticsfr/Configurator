import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio

class PrinterSetup(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin=20)
        self.parent = parent
        self._ = _

        # Load CSS stylesheet
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('config/themes/theme.css')  # Path to your CSS file
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Header
        self.header = self.create_header()
        self.pack_start(self.header, False, False, 0)

        # Printer selection
        self.printer_selection = self.create_printer_selection()
        self.pack_start(self.printer_selection, False, False, 0)

        # Head type selection
        self.head_type_selection = self.create_head_type_selection()
        self.pack_start(self.head_type_selection, False, False, 0)

        # Smartbox option
        self.smartbox_toggle = self.create_smartbox_option()
        self.pack_start(self.smartbox_toggle, False, False, 0)

        # Submit button
        self.submit_button = Gtk.Button(label=self._("Apply Settings"))
        self.submit_button.get_style_context().add_class("big-button")  # Apply a larger button size using CSS
        self.submit_button.connect("clicked", self.on_submit_clicked)
        self.pack_start(self.submit_button, False, False, 0)

    def apply_css(self):
        """Method to apply the CSS from the external file."""
        css_provider = Gtk.CssProvider()

        # Load CSS from the external file
        css_file = Gio.File.new_for_path("config/themes/theme.css")
        css_provider.load_from_file(css_file)

        # Apply the CSS to the screen
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def create_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.33, 0.05, 0.05, 1))
        header_box.set_margin_top(16)
        header_box.set_margin_bottom(12)

        title_label = Gtk.Label(label=self._("Printer Setup"))
        title_label.get_style_context().add_class('title')  # Apply a 'title' class for styling
        title_label.set_xalign(0.5)  # Center the text horizontally
        header_box.pack_start(title_label, True, True, 0)

        return header_box

    def create_printer_selection(self):
        printer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=self._("Select Printer:"))
        printer_box.pack_start(label, False, False, 0)

        # Printer dropdown (ComboBox) with larger size via CSS
        self.printer_combo = Gtk.ComboBoxText()
        self.printer_combo.append_text(self._("Printer 1"))
        self.printer_combo.append_text(self._("Printer 2"))
        self.printer_combo.append_text(self._("Printer 3"))
        self.printer_combo.set_active(0)
        self.printer_combo.get_style_context().add_class("big-combo")  # Apply a class for larger ComboBox size
        printer_box.pack_start(self.printer_combo, False, False, 0)

        return printer_box

    def create_head_type_selection(self):
        head_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=self._("Select Head Type:"))
        head_box.pack_start(label, False, False, 0)

        # Head type dropdown (ComboBox) with larger size via CSS
        self.head_combo = Gtk.ComboBoxText()
        self.head_combo.append_text(self._("Type A"))
        self.head_combo.append_text(self._("Type B"))
        self.head_combo.append_text(self._("Type C"))
        self.head_combo.set_active(0)
        self.head_combo.get_style_context().add_class("big-combo")  # Apply class for bigger size
        head_box.pack_start(self.head_combo, False, False, 0)

        return head_box

    def create_smartbox_option(self):
        smartbox_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label(label=self._("Enable Smartbox:"))
        smartbox_box.pack_start(label, False, False, 0)

        # Toggle for Smartbox
        self.smartbox_switch = Gtk.Switch()
        self.smartbox_switch.set_active(False)
        smartbox_box.pack_start(self.smartbox_switch, False, False, 0)

        return smartbox_box

    def on_submit_clicked(self, button):
        """Handle the submit button click event."""
        selected_printer = self.printer_combo.get_active_text()
        selected_head = self.head_combo.get_active_text()
        is_smartbox_enabled = self.smartbox_switch.get_active()

        # Debug output
        print(f"Selected Printer: {selected_printer}")
        print(f"Selected Head Type: {selected_head}")
        print(f"Smartbox Enabled: {'Yes' if is_smartbox_enabled else 'No'}")

        # Here you can add logic to save these settings or apply them accordingly.

if __name__ == "__main__":
    win = Gtk.Window()
    win.set_title("Printer Setup")
    win.set_default_size(800, 500)
    win.connect("destroy", Gtk.main_quit)

    setup_page = PrinterSetup(None, lambda x: x)
    win.add(setup_page)
    win.show_all()

    Gtk.main()
