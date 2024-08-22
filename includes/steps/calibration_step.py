import gi
from gi.repository import Gtk, Gdk, GLib
import time
import requests
import threading

gi.require_version('Gtk', '3.0')

class CalibrationStep(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        if not isinstance(parent, Gtk.Window):
            raise TypeError("parent must be an instance of Gtk.Window")
        
        self.parent = parent

        # Load CSS stylesheet
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('config/themes/theme.css')  # Path to your CSS file
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Title and Skip button
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_box.set_margin_top(20)
        title_box.set_margin_bottom(10)
        title_box.set_margin_start(10)
        title_box.set_margin_end(10)
        self.pack_start(title_box, False, False, 0)

                # Bouton de retour
        back_button = Gtk.Button(label="<")
        back_button.connect("clicked", self.on_back_clicked)
        back_button.get_style_context().add_class('button')
        title_box.pack_start(back_button, False, False, 0)

        # Title
        title_label = Gtk.Label(label="Calibration")
        title_label.get_style_context().add_class("title")
        title_label.set_xalign(0)  # Align left
        title_box.pack_start(title_label, True, True, 0)

        # Skip Button
        skip_button = Gtk.Button(label="Finish")
        skip_button.get_style_context().add_class('button')
        skip_button.connect("clicked", self.on_skip_clicked)
        title_box.pack_start(skip_button, False, False, 0)

        # Test items with switches next to labels
        self.fan_test_switch = self.create_test_item("Test des ventilos", active=True)
        self.axis_test_switch = self.create_test_item("Vérification des axes", active=True)
        self.speed_test_switch = self.create_test_item("Test de vitesse", active=True)

        # Container for test items, centered horizontally
        test_items_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        test_items_box.set_halign(Gtk.Align.CENTER)  # Center items
        test_items_box.pack_start(self.fan_test_switch['box'], False, False, 5)
        test_items_box.pack_start(self.axis_test_switch['box'], False, False, 5)
        test_items_box.pack_start(self.speed_test_switch['box'], False, False, 5)

        self.pack_start(test_items_box, False, False, 10)

        # Button to start calibration
        self.calibrate_button = Gtk.Button(label="Commencer la calibration")
        self.calibrate_button.get_style_context().add_class('button')
        self.calibrate_button.connect("clicked", self.on_calibrate_clicked)
        self.calibrate_button.set_margin_bottom(20)  # Margin at the bottom for the button
        self.pack_start(self.calibrate_button, False, False, 20)

    def create_test_item(self, label_text, active=False):
        """Creates a test item with a label and a switch aligned to the right."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_halign(Gtk.Align.FILL)  # Align items horizontally

        # Label with text
        label = Gtk.Label(label_text)
        label.get_style_context().add_class("test-label")  # Add CSS class
        label.set_xalign(0)  # Align the label to the left

        # Switch
        switch = Gtk.Switch()
        switch.set_active(active)  # Default to "on"
        switch.set_size_request(60, 30)  # Adjust size of the switch

        # Add items to the box
        box.pack_start(label, True, True, 0)  # Label takes all available space
        box.pack_start(switch, False, False, 0)  # Switch aligned to the right
        
        return {"box": box, "switch": switch, "label": label}

    def on_calibrate_clicked(self, button):
        """Starts the calibration process."""
        # Check if the printer is connected
        if not self.check_printer_connection():
            print("Erreur : Imprimante non connectée")
            return

        # Disable all buttons during calibration
        self.set_all_buttons_sensitive(False)

        # Start tests sequentially without blocking the UI
        threading.Thread(target=self.run_tests_sequentially).start()

    def run_tests_sequentially(self):
        """Runs the selected tests sequentially with a 5-second pause between each."""
        if self.fan_test_switch["switch"].get_active():
            self.run_test(self.fan_test_switch, self.run_fan_test)
            GLib.idle_add(self.pause_between_tests)  # Add a pause between tests
        
        if self.axis_test_switch["switch"].get_active():
            self.run_test(self.axis_test_switch, self.run_axis_test)
            GLib.idle_add(self.pause_between_tests)  # Add a pause between tests

        if self.speed_test_switch["switch"].get_active():
            self.run_test(self.speed_test_switch, self.run_speed_test)
        
        # Re-enable all buttons when all tests are done
        GLib.idle_add(lambda: self.set_all_buttons_sensitive(True))

    def run_test(self, test_item, test_function):
        """Executes a test and updates the GUI based on the result."""
        # Ensure GUI is updated before starting the test
        GLib.idle_add(self.update_test_status, test_item, "in_progress")

        # Run the test in a separate thread
        success = test_function()

        # Update the GUI based on the result
        GLib.idle_add(self.update_test_status, test_item, "success" if success else "failed")

        # Show confirmation dialog
        #GLib.idle_add(self.show_test_result_dialog, success)

    def update_test_status(self, test_item, status):
        """Updates the icon and text based on the test status."""
        status_text = ""
        icon_name = ""
        if status == "in_progress":
            status_text = "En cours..."
            icon_name = "process-working-symbolic"
        elif status == "success":
            status_text = "Succès!"
            icon_name = "emblem-ok-symbolic"
        else:
            status_text = "Échec!"
            icon_name = "dialog-error-symbolic"
        
        # Update text
        test_item["label"].set_text(status_text)

        # Update CSS classes based on the test status
        test_item["label"].get_style_context().remove_class("error")
        test_item["label"].get_style_context().remove_class("info")
        test_item["label"].get_style_context().remove_class("success")
        
        if status == "in_progress":
            test_item["label"].get_style_context().add_class("info")
        elif status == "success":
            test_item["label"].get_style_context().add_class("success")
        else:
            test_item["label"].get_style_context().add_class("error")

    def pause_between_tests(self):
        """Pauses for 5 seconds between tests."""
        time.sleep(5)

    def set_all_buttons_sensitive(self, sensitive):
        """Sets the sensitivity of all buttons (including switches and calibration button)."""
        # Set the sensitivity of switches
        for test_item in [self.fan_test_switch, self.axis_test_switch, self.speed_test_switch]:
            test_item["switch"].set_sensitive(sensitive)
        
        # Set the sensitivity of the calibration button
        self.calibrate_button.set_sensitive(sensitive)

    def check_printer_connection(self):
        """Checks connection to the printer via API."""
        return True  # Implement your logic to check if the printer is connected

    def run_fan_test(self):
        """Tests the fans' speeds and operation in various conditions."""
        try:
            # Home all axes
            home_command = "G28"
            response = requests.post(
                'http://localhost:7125/printer/gcode/script',
                json={"script": home_command},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 200:
                print(f"Error sending {home_command}: Status Code {response.status_code}")
                return False

            # Wait for homing to complete
            time.sleep(5)
                                    
            # Define the fan speeds from 0% to 100% in increments
            speeds = [0, 51, 102, 153, 204, 255, 255, 255]
            # Define the fan commands for extruder and head
            fan_commands = [
                {"name": "Extruder Fan", "command": "M106 S", "fan_id": "extruder"},
            ]

            for fan in fan_commands:
                for speed in speeds:
                    # Set fan speed
                    command = f"{fan['command']}{speed}"
                    response = requests.post(
                        'http://localhost:7125/printer/gcode/script',
                        json={"script": command},
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code != 200:
                        print(f"Error sending {command} for {fan['name']}: Status Code", response.status_code)
                        return False
                    time.sleep(2)  # Wait 2 seconds to observe the changes

            return True

        except requests.RequestException as e:
            print("Error during fan test:", e)
            return False

    def run_axis_test(self):
        """Tests the movement of X, Y, Z axes and their position detection."""
        try:
            # Home all axes
            command = "G28"
            response = requests.post(
                'http://localhost:7125/printer/gcode/script',
                json={"script": command},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 200:
                print(f"Error sending {command}: Status Code {response.status_code}")
                return False
            
            # Wait for home to complete
            time.sleep(3)

            # Test X-axis movement
            commands = [
                "G1 X0 F5000",  # Move to 0 position with speed F1000
                "G1 X100 F5000",  # Move to 100 position with speed F1000
                "G1 X0 F5000"  # Return to 0 position with speed F1000
            ]
            for command in commands:
                response = requests.post(
                    'http://localhost:7125/printer/gcode/script',
                    json={"script": command},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 200:
                    print(f"Error sending {command}: Status Code {response.status_code}")
                    return False
                time.sleep(3)  # Wait for each move to complete

            # Test Y-axis movement
            commands = [
                "G1 Y0 F5000",  # Move to 0 position with speed F1000
                "G1 Y100 F5000",  # Move to 100 position with speed F1000
                "G1 Y0 F5000"  # Return to 0 position with speed F1000
            ]
            for command in commands:
                response = requests.post(
                    'http://localhost:7125/printer/gcode/script',
                    json={"script": command},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 200:
                    print(f"Error sending {command}: Status Code {response.status_code}")
                    return False
                time.sleep(3)

            # Test Z-axis movement
            commands = [
                "G1 Z0 F5000",  # Move to 0 position with speed F1000
                "G1 Z100 F5000",  # Move to 100 position with speed F1000
                "G1 Z0 F5000"  # Return to 0 position with speed F1000
            ]
            for command in commands:
                response = requests.post(
                    'http://localhost:7125/printer/gcode/script',
                    json={"script": command},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 200:
                    print(f"Error sending {command}: Status Code {response.status_code}")
                    return False
                time.sleep(3)

            return True

        except requests.RequestException as e:
            print("Error during axis test:", e)
            return False

    def run_speed_test(self):
        """Tests the speed by tracing increasingly larger squares at the center of the bed without pauses."""
        try:
            # Home all axes
            home_command = "G28"
            response = requests.post(
                'http://localhost:7125/printer/gcode/script',
                json={"script": home_command},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 200:
                print(f"Error sending {home_command}: Status Code {response.status_code}")
                return False

            # Wait for homing to complete
            time.sleep(5)

            # Define the parameters for the square test
            initial_side_length = 10  # Initial side length of the square in mm
            num_squares = 10  # Number of squares to draw
            side_length_increment = 10  # Side length increment per square in mm
            speed_increment = 1000  # Speed increment in mm/min

            # Initial speed
            speed = 1000  # Starting speed in mm/min

            # Get printer bed size (replace these values with actual bed dimensions)
            bed_width = 200  # Example value in mm
            bed_depth = 200  # Example value in mm

            # Ensure the starting point is at the center
            start_x = bed_width / 2
            start_y = bed_depth / 2

            for i in range(num_squares):
                side_length = initial_side_length + i * side_length_increment
                if side_length <= 0:
                    side_length = 1  # Minimum side length to avoid zero

                # Generate the G-code for the square
                gcode_commands = [f"G1 F{speed}"]  # Set speed
                half_side = side_length / 2
                gcode_commands.append(f"G1 X{start_x - half_side:.2f} Y{start_y - half_side:.2f}")  # Move to starting point
                
                # Draw the square
                gcode_commands.append(f"G1 X{start_x + half_side:.2f} Y{start_y - half_side:.2f}")  # Bottom side
                gcode_commands.append(f"G1 X{start_x + half_side:.2f} Y{start_y + half_side:.2f}")  # Right side
                gcode_commands.append(f"G1 X{start_x - half_side:.2f} Y{start_y + half_side:.2f}")  # Top side
                gcode_commands.append(f"G1 X{start_x - half_side:.2f} Y{start_y - half_side:.2f}")  # Left side
                gcode_commands.append(f"G1 X{start_x - half_side:.2f} Y{start_y - half_side:.2f}")  # Return to starting point

                # Send the G-code commands
                for command in gcode_commands:
                    response = requests.post(
                        'http://localhost:7125/printer/gcode/script',
                        json={"script": command},
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code != 200:
                        print(f"Error sending {command}: Status Code {response.status_code}")
                        return False

                # Increment speed for the next square
                speed += speed_increment

            return True

        except requests.RequestException as e:
            print("Error during speed test:", e)
            return False

    def show_test_result_dialog(self, success):
        """Shows a dialog with the result of the test."""
        dialog = Gtk.MessageDialog(
            self.parent,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.INFO if success else Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "Le test s'est terminé avec succès." if success else "Le test a échoué."
        )
        dialog.run()
        dialog.destroy()

    def on_skip_clicked(self, button):
        """Handles the skip button click event."""
        self.parent.next_step() # Assume you have a method to switch steps

    def on_back_clicked(self, button):
        self.parent.previous_step()