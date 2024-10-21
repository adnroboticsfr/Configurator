import gi
import configparser
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class PrinterSetup(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin=0)
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
        # Create a vertical box for the entire page
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)  # Increased spacing for uniformity
        
        # Create a horizontal box to hold the title and back button
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))  # Background color #550d0d

        # Create the back button
        back_button = Gtk.Button(label="<")
        back_button.connect("clicked", self.on_back_clicked)
        back_button.get_style_context().add_class('button')

        # Pack the back button into the title box
        title_box.pack_start(back_button, False, False, 0)

        # Create the title label
        label = Gtk.Label(label="Select Printer Model")
        label.get_style_context().add_class("title")
        label.set_xalign(0.3)

        # Pack the label into the title box
        title_box.pack_start(label, True, True, 0)

        # Add the title box to the main box
        box.pack_start(title_box, False, False, 0)

        # Create a FlowBox for the printer models
        flowbox = Gtk.FlowBox()
        flowbox.set_max_children_per_line(3)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        # List of printer models and corresponding image file paths
        self.printers = [
            ("C235", "assets/img/C235.png"),
            ("C335", "assets/img/C335.png"),
            ("C435", "assets/img/C435.png")
        ]

        for printer_name, image_path in self.printers:
            # Create a button with an image and label for each printer
            button1 = Gtk.Button()
            button1.get_style_context().add_class("printermodel-button")
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

        # Create a ScrolledWindow for the FlowBox
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        scrolled_window.add(flowbox)

        # Pack the scrolled window into the main box
        box.pack_start(scrolled_window, True, True, 0)

        # Add spacing at the bottom using a Gtk.Alignment or a blank Gtk.Box
        bottom_spacing = Gtk.Box()
        bottom_spacing.set_size_request(-1, 30)  # Set space between bottom of screen and buttons
        box.pack_start(bottom_spacing, False, False, 0)

        return box

    def create_head_type_page(self):
        """Create the head type selection page with image buttons."""
        # Create a vertical box for the entire page
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)  # Uniform spacing

        # Create a horizontal box to hold the title and back button
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))  # Background color

        # Create the back button
        back_button = Gtk.Button(label="<")
        back_button.connect("clicked", self.on_previous_clicked)
        back_button.get_style_context().add_class('button')

        # Pack the back button into the title box
        title_box.pack_start(back_button, False, False, 0)

        # Create the title label
        label = Gtk.Label(label="Select Head Type")
        label.get_style_context().add_class("title")
        label.set_xalign(0.3)  # Center the label horizontally
        title_box.pack_start(label, True, True, 0)

        # Add the title box (with back button and title) to the main box
        box.pack_start(title_box, False, False, 0)

        # Create a horizontal box for head type buttons with reduced spacing
        head_type_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)  # Reduced spacing between buttons

        # Define head types and their corresponding images
        head_types = [
            ("Direct-Drive", "assets/img/direct_drive.png"),
            ("12-Colors", "assets/img/12_colors.png")
        ]

        for head_name, image_path in head_types:
            button = Gtk.Button()
            button.get_style_context().add_class("printermodel-button")
            
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            # Create and add the image, with padding to lower it slightly
            image = Gtk.Image.new_from_file(image_path)
            image.set_size_request(80, 100)
            vbox.pack_start(image, False, False, 30)  # Padding above the image to lower it slightly

            # Create and add the label
            label = Gtk.Label(label=head_name)
            label.get_style_context().add_class("printer-label")
            vbox.pack_start(label, False, False, 2)  # Small padding between the image and label

            # Add the vbox to the button
            button.add(vbox)
            button.set_size_request(80, 100)
            button.connect("clicked", self.on_head_type_button_clicked, head_name)

            head_type_box.pack_start(button, True, True, 0)

        # Pack the head type box into the main vertical box
        box.pack_start(head_type_box, True, True, 0)

        # Add spacing at the bottom using a Gtk.Box to create space between buttons and the bottom of the screen
        bottom_spacing = Gtk.Box()
        bottom_spacing.set_size_request(-1, 30)  # Space between bottom of screen and buttons
        box.pack_start(bottom_spacing, False, False, 0)

        return box

    # Add this method in your PrinterSetup class
    def on_smartbox_selected(self, button, enabled):
        """Handle Smartbox selection: save the choice and update configuration."""
        print(f"Smartbox enabled: {enabled}")
        self.smartbox_enabled = enabled

        """Save selections and execute bash script."""
        config = configparser.ConfigParser()

        # Read the existing config file
        config.read('config/config.conf')

        # Update or add the necessary sections
        if 'Printer' not in config:
            config['Printer'] = {}
        config['Printer']['model'] = self.selected_printer

        if 'HeadType' not in config:
            config['HeadType'] = {}
        config['HeadType']['type'] = self.selected_head_type

        if 'Smartbox' not in config:
            config['Smartbox'] = {}
        config['Smartbox']['enabled'] = str(self.smartbox_enabled)

        if 'Hyperdrive' not in config:
            config['Hyperdrive'] = {}
        config['Hyperdrive']['enabled'] = str(self.hyperdrive_enabled)

        # Write the changes back to the config file
        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)

        # Call the bash script with the selected values
        subprocess.run(['/home/pi/Configurator/scripts/copy_printer_cfg.sh', self.selected_printer,
                        self.selected_head_type, str(self.smartbox_enabled),
                        str(self.hyperdrive_enabled)])

        print("Configuration saved and bash script executed.")

        # Move to the next step
        self.parent.skip_to_step('success')

    # Update the button creation in create_smartbox_hyperdrive_page method
    def create_smartbox_hyperdrive_page(self):
        """Create the Smartbox and Hyperdrive selection page with properly positioned title, description, and buttons."""
        # Create a vertical box for the entire page
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        # Create a horizontal box to hold the title and back button
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))  # Background color for title bar

        # Create the back button
        back_button = Gtk.Button(label="<")
        back_button.connect("clicked", self.on_previous_clicked)
        back_button.get_style_context().add_class('button')

        # Pack the back button into the title box
        title_box.pack_start(back_button, False, False, 0)

        # Title
        label = Gtk.Label(label="Smartbox and Hyperdrive Options")
        label.get_style_context().add_class("title")
        label.set_xalign(0.3) 
        title_box.pack_start(label, True, True, 0)  # Center the title next to the back button

        # Add the title box (with back button and title) to the main box
        box.pack_start(title_box, False, False, 0)

        # Description
        description_label = Gtk.Label(label="Do you have a Smartbox?")
        description_label.get_style_context().add_class("description-label")
        description_label.set_markup("<span size='larger' foreground='white'>Do you have a Smartbox?</span>")
        box.pack_start(description_label, False, False, 10)  # Reduced spacing here

        # Smartbox selection
        smartbox_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        smartbox_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        smartbox_icon = Gtk.Image.new_from_file("assets/img/smartbox_icon.png")
        smartbox_column.pack_start(smartbox_icon, False, False, 0)

        smartbox_label = Gtk.Label(label="Smartbox")
        smartbox_label.get_style_context().add_class("subtitle")
        smartbox_label.set_markup("<span size='larger' foreground='white'>Smartbox</span>")
        smartbox_column.pack_start(smartbox_label, False, False, 0)

        box.pack_start(smartbox_column, False, False, 0)

        # Create a horizontal box for the button alignment
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)

        # Button for No (cross)
        self.smartbox_no_image = Gtk.Image.new_from_file("assets/img/cross.png")  # Image for "No"
        self.smartbox_no = Gtk.Button()
        self.smartbox_no.get_style_context().add_class('button3')
        self.smartbox_no.add(self.smartbox_no_image)
        self.smartbox_no.connect("clicked", self.on_smartbox_selected, False)
        self.smartbox_no.set_size_request(200, -1)  # Set a specific width

        # Button for Yes (checkmark)
        self.smartbox_yes_image = Gtk.Image.new_from_file("assets/img/checkmark.png")  # Image for "Yes"
        self.smartbox_yes = Gtk.Button()
        self.smartbox_yes.get_style_context().add_class('button3')
        self.smartbox_yes.add(self.smartbox_yes_image)
        self.smartbox_yes.connect("clicked", self.on_smartbox_selected, True)
        self.smartbox_yes.set_size_request(200, -1)  # Set a specific width

        # Set margins for the buttons to keep them away from the screen edges
        self.smartbox_no.set_margin_left(20)   # Left margin
        self.smartbox_no.set_margin_right(20)  # Right margin
        self.smartbox_yes.set_margin_left(20)   # Left margin
        self.smartbox_yes.set_margin_right(20)  # Right margin

        # Pack the buttons into the button box
        button_box.pack_start(self.smartbox_no, False, False, 0)  # Keep the size unchanged
        button_box.pack_end(self.smartbox_yes, False, False, 0)   # Keep the size unchanged

        # Pack the button box with reduced spacing to lift buttons slightly
        box.pack_start(button_box, False, False, 20)  # Adjusted spacing to lower buttons

        return box


    def on_printer_button_clicked(self, button, printer_name):
        """Handle printer selection."""
        print(f"Selected Printer: {printer_name}")
        self.selected_printer = printer_name

        # Save selection to config
        self.save_selected_printer(printer_name)

        # Automatically move to the head type selection page
        self.stack.set_visible_child_name("head_type_page")
        self.prev_button.set_sensitive(True)

        # Apply CSS styling to indicate selection
        self.apply_printer_selection_css(printer_name)

    def save_selected_printer(self, printer_name):
        """Save the selected printer model to the configuration file."""
        config = configparser.ConfigParser()
        
        # Read the existing config file
        config.read('config/config.conf')
        
        # If 'Printer' section doesn't exist, add it
        if 'Printer' not in config:
            config['Printer'] = {}

        # Update the selected printer in the config
        config['Printer']['model'] = printer_name

        # Write the updated config back to the file
        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)

        print(f"Printer {printer_name} saved to configuration file.")

    def apply_printer_selection_css(self, printer_name):
        """Update CSS for printer selection."""
        for name, image_path in self.printers:
            if name == printer_name:
                style_class = "selected-printer"
            else:
                style_class = "unselected-printer"

            # Apply your custom CSS logic here for borders, colors, etc.

    def on_head_type_button_clicked(self, button, head_type):
        """Handle head type selection."""
        print(f"Selected Head Type: {head_type}")
        self.selected_head_type = head_type

        # Automatically move to Smartbox and Hyperdrive selection
        self.stack.set_visible_child_name("smartbox_hyperdrive_page")
    
    #def on_smartbox_selected(self, button, enabled):
        #"""Handle Smartbox selection."""
        #print(f"Smartbox Enabled: {enabled}")
        #self.smartbox_enabled = enabled

    def on_validate_clicked(self, button):
        """Save selections and execute bash script."""
        config = configparser.ConfigParser()

        # Read the existing config file
        config.read('config/config.conf')

        # Update or add the necessary sections
        if 'Printer' not in config:
            config['Printer'] = {}
        config['Printer']['model'] = self.selected_printer

        if 'HeadType' not in config:
            config['HeadType'] = {}
        config['HeadType']['type'] = self.selected_head_type

        if 'Smartbox' not in config:
            config['Smartbox'] = {}
        config['Smartbox']['enabled'] = str(self.smartbox_enabled)

        # Write the changes back to the config file
        with open('config/config.conf', 'w') as configfile:
            config.write(configfile)

        # Call the bash script with the selected values, even if some arguments are not used in the script
        subprocess.run(['/home/pi/Configurator/scripts/copy_printer_cfg.sh', self.selected_printer,
                        self.selected_head_type, str(self.smartbox_enabled)])

        print("Configuration saved and bash script executed.")


    def on_previous_clicked(self, button):
        """Handle 'Previous' button click."""
        if self.stack.get_visible_child_name() == "head_type_page":
            self.stack.set_visible_child_name("printer_page")
            self.prev_button.set_sensitive(False)
        elif self.stack.get_visible_child_name() == "smartbox_hyperdrive_page":
            self.stack.set_visible_child_name("head_type_page")

    def on_back_clicked(self, button):
        self.parent.skip_to_step('network1')
