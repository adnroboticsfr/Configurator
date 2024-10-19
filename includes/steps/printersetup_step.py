import gi
import configparser
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class PrinterSetup(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin=20)
        self.parent = parent

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('config/themes/theme.css')
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Stack for multiple pages
        self.stack = Gtk.Stack()
        self.pack_start(self.stack, True, True, 0)

        # Page 1: Printer selection
        self.page1 = self.create_printer_selection_page()
        self.stack.add_titled(self.page1, "printer_page", "Printer Selection")

        # Page 2: Head type selection
        self.page2 = self.create_head_type_page()
        self.stack.add_titled(self.page2, "head_type_page", "Head Type Selection")

        # Page 3: Smartbox and Hyperdrive selection
        self.page3 = self.create_smartbox_hyperdrive_page()
        self.stack.add_titled(self.page3, "smartbox_hyperdrive_page", "Smartbox and Hyperdrive Selection")

        # Initially show the first page
        self.stack.set_visible_child_name("printer_page")

        # Create a button box for navigation
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.pack_start(self.button_box, False, False, 0)

        # Create navigation buttons
        self.prev_button = Gtk.Button(label="Previous")
        self.prev_button.connect("clicked", self.on_previous_clicked)
        self.prev_button.set_sensitive(False)

        # Add the Apply button
        self.apply_button = Gtk.Button(label="Apply")  # Create the Apply button
        self.apply_button.connect("clicked", self.on_apply_clicked)
        self.apply_button.set_sensitive(False)  # Initially disabled

        self.button_box.pack_start(self.prev_button, False, False, 0)
        #self.button_box.pack_start(self.apply_button, False, False, 0)  # Add it to the button box

        # Set default selected printer
        self.selected_printer = "C235"  # Default printer
        self.apply_printer_selection_css(self.selected_printer)

        # Head type selection
        self.selected_head_type = None  # Variable to store selected head type

        # Smartbox and Hyperdrive selections
        self.smartbox_enabled = False
        self.hyperdrive_enabled = False

    def create_printer_selection_page(self):
        """Create the printer selection page with images."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        label = Gtk.Label(label="Select Printer Model")
        label.get_style_context().add_class("title")
        box.pack_start(label, False, False, 0)

        flowbox = Gtk.FlowBox()
        flowbox.set_max_children_per_line(3)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        # List of printer models and corresponding image file paths
        self.printers = [
            ("C235", "images/C235.png"),
            ("C335", "images/C335.png"),
            ("C435", "images/C435.png")
        ]

        for printer_name, image_path in self.printers:
            # Create a button with an image and label for each printer
            button1 = Gtk.Button()
            button1.get_style_context().add_class("language-button1")
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            image = Gtk.Image.new_from_file(image_path)
            image.set_size_request(80, 100)
            vbox.pack_start(image, True, True, 0)

            label = Gtk.Label(label=printer_name)
            label.get_style_context().add_class("printer-label")
            vbox.pack_start(label, False, False, 0)

            button1.add(vbox)
            button1.set_size_request(80, 100)
            button1.connect("clicked", self.on_printer_button_clicked, printer_name)

            flowbox.add(button1)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        scrolled_window.add(flowbox)

        box.pack_start(scrolled_window, True, True, 0)
        return box

    def create_head_type_page(self):
        """Create the head type selection page with image buttons."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        label = Gtk.Label(label="Select Head Type")
        label.get_style_context().add_class("title")
        box.pack_start(label, False, False, 0)

        # Create a horizontal box for head type buttons
        head_type_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Define head types and their corresponding images
        head_types = [
            ("Direct Drive", "images/direct_drive.png"),
            ("12 Colors", "images/12_colors.png")
        ]

        for head_name, image_path in head_types:
            button = Gtk.Button()
            button.get_style_context().add_class("language-button1")
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            image = Gtk.Image.new_from_file(image_path)
            image.set_size_request(80, 100)
            vbox.pack_start(image, True, True, 0)

            label = Gtk.Label(label=head_name)
            label.get_style_context().add_class("printer-label")
            vbox.pack_start(label, False, False, 0)

            button.add(vbox)
            button.set_size_request(80, 100)
            button.connect("clicked", self.on_head_type_button_clicked, head_name)

            head_type_box.pack_start(button, True, True, 0)

        box.pack_start(head_type_box, True, True, 0)
        return box

    def create_smartbox_hyperdrive_page(self):
        """Create the Smartbox and Hyperdrive selection page."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        label = Gtk.Label(label="Smartbox and Hyperdrive Options")
        label.get_style_context().add_class("title")
        box.pack_start(label, False, False, 0)

        # Smartbox selection
        smartbox_label = Gtk.Label(label="Enable Smartbox?")
        smartbox_label.get_style_context().add_class("subtitle")
        box.pack_start(smartbox_label, False, False, 0)

        smartbox_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.smartbox_yes = Gtk.Button(label="Yes")
        self.smartbox_yes.connect("clicked", self.on_smartbox_selected, True)
        smartbox_box.pack_start(self.smartbox_yes, True, True, 0)

        self.smartbox_no = Gtk.Button(label="No")
        self.smartbox_no.connect("clicked", self.on_smartbox_selected, False)
        smartbox_box.pack_start(self.smartbox_no, True, True, 0)

        box.pack_start(smartbox_box, False, False, 0)

        # Hyperdrive selection
        hyperdrive_label = Gtk.Label(label="Enable Hyperdrive?")
        hyperdrive_label.get_style_context().add_class("subtitle")
        box.pack_start(hyperdrive_label, False, False, 0)

        hyperdrive_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.hyperdrive_yes = Gtk.Button(label="Yes")
        self.hyperdrive_yes.connect("clicked", self.on_hyperdrive_selected, True)
        hyperdrive_box.pack_start(self.hyperdrive_yes, True, True, 0)

        self.hyperdrive_no = Gtk.Button(label="No")
        self.hyperdrive_no.connect("clicked", self.on_hyperdrive_selected, False)
        hyperdrive_box.pack_start(self.hyperdrive_no, True, True, 0)

        box.pack_start(hyperdrive_box, False, False, 0)

        # Add validation button to save the selections and proceed
        validate_button = Gtk.Button(label="Confirm")
        validate_button.connect("clicked", self.on_validate_clicked)
        box.pack_start(validate_button, False, False, 0)

        return box

    def on_printer_button_clicked(self, button, printer_name):
        """Handle printer selection."""
        print(f"Selected Printer: {printer_name}")
        self.selected_printer = printer_name
        
        # Save selection to config
        self.save_selected_printer(printer_name)

        # Apply CSS to highlight the selected printer
        self.apply_printer_selection_css(printer_name)

        # Automatically move to the head type selection page
        self.stack.set_visible_child_name("head_type_page")
        self.prev_button.set_sensitive(True)
        self.apply_button.set_sensitive(True)  # Enable the apply button

    def on_head_type_button_clicked(self, button, head_name):
        """Handle head type selection."""
        print(f"Selected Head Type: {head_name}")
        self.selected_head_type = head_name
        
        # Save selection to config
        self.save_selected_head_type(head_name)

        # Automatically move to the Smartbox and Hyperdrive selection page
        self.stack.set_visible_child_name("smartbox_hyperdrive_page")
        self.prev_button.set_sensitive(True)
        self.apply_button.set_sensitive(True)  # Enable the apply button


    def on_smartbox_selected(self, button, is_enabled):
        """Handle Smartbox selection."""
        self.smartbox_enabled = is_enabled
        print(f"Smartbox Enabled: {self.smartbox_enabled}")

        # Update button styles
        self.update_smartbox_buttons()

    def on_hyperdrive_selected(self, button, is_enabled):
        """Handle Hyperdrive selection."""
        self.hyperdrive_enabled = is_enabled
        print(f"Hyperdrive Enabled: {self.hyperdrive_enabled}")

        # Update button styles
        self.update_hyperdrive_buttons()

    def update_smartbox_buttons(self):
        """Update the styles of Smartbox buttons."""
        if self.smartbox_enabled:
            self.smartbox_yes.get_style_context().add_class("selected")
            self.smartbox_no.get_style_context().remove_class("selected")
        else:
            self.smartbox_yes.get_style_context().remove_class("selected")
            self.smartbox_no.get_style_context().add_class("selected")

    def update_hyperdrive_buttons(self):
        """Update the styles of Hyperdrive buttons."""
        if self.hyperdrive_enabled:
            self.hyperdrive_yes.get_style_context().add_class("selected")
            self.hyperdrive_no.get_style_context().remove_class("selected")
        else:
            self.hyperdrive_yes.get_style_context().remove_class("selected-button")
            self.hyperdrive_no.get_style_context().add_class("selected-button")

    def on_validate_clicked(self, button):
        """Save selections and proceed to next step."""
        self.save_smartbox_hyperdrive_settings()
        self.stack.set_visible_child_name("printer_page")  # Navigate to the printer page or next step
        print(f"Smartbox: {self.smartbox_enabled}, Hyperdrive: {self.hyperdrive_enabled}")

    def apply_printer_selection_css(self, printer_name):
        """Apply CSS styles for selected printer."""
        # Reset all buttons' styles
        for p in self.printers:
            button = self.get_child_button(p[0])
            if button:
                button.get_style_context().remove_class("selected-printer")

        # Highlight the selected printer
        button = self.get_child_button(printer_name)
        if button:
            button.get_style_context().add_class("selected-printer")

    def get_child_button(self, printer_name):
        """Get the button for a specific printer name."""
        for child in self.get_children()[0].get_children()[0].get_children():  # Navigate to FlowBox
            if isinstance(child, Gtk.Button):  # Check if the child is a button
                vbox = child.get_children()[0]  # Get the VBox
                label = vbox.get_children()[1]  # Get the label
                if label.get_label() == printer_name:
                    return child
        return None

    def save_selected_printer(self, printer_name):
        """Save the selected printer name to the configuration file."""
        config = configparser.ConfigParser()
        config.read('config/config.conf')
        config['printer'] = {'selected_printer': printer_name}

        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)

    def save_selected_head_type(self, head_name):
        """Save the selected head type to the configuration file."""
        config = configparser.ConfigParser()
        config.read('config/config.conf')
        config['head'] = {'selected_head_type': head_name}

        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)

    def save_smartbox_hyperdrive_settings(self):
        """Save Smartbox and Hyperdrive settings to the configuration file."""
        config = configparser.ConfigParser()
        config.read('config/config.conf')
        config['smartbox'] = {'enabled': str(self.smartbox_enabled)}
        config['hyperdrive'] = {'enabled': str(self.hyperdrive_enabled)}

        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)

    def on_previous_clicked(self, button):
        """Switch to the previous page."""
        current_page = self.stack.get_visible_child_name()
        if current_page == "head_type_page":
            self.stack.set_visible_child_name("printer_page")
            self.prev_button.set_sensitive(False)
            self.apply_button.set_sensitive(False)
        elif current_page == "smartbox_hyperdrive_page":
            self.stack.set_visible_child_name("head_type_page")
            self.prev_button.set_sensitive(True)
            self.apply_button.set_sensitive(True)

    def on_apply_clicked(self, button):
        """Apply the selected settings."""
        print(f"Printer: {self.selected_printer}, Head Type: {self.selected_head_type}, Smartbox: {self.smartbox_enabled}, Hyperdrive: {self.hyperdrive_enabled}")
        # Additional logic to save or apply these settings.

if __name__ == "__main__":
    win = Gtk.Window()
    win.set_title("Printer Setup")
    win.set_default_size(800, 500)
    win.connect("destroy", Gtk.main_quit)

    setup_page = PrinterSetup(None)
    win.add(setup_page)
    win.show_all()

    Gtk.main()
