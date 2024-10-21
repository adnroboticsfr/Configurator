import gi
from gi.repository import Gtk, Gdk, GLib
import time
import requests
import threading

gi.require_version('Gtk', '3.0')

class CalibrationStep(Gtk.Box):
    def __init__(self, parent, _):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        if not isinstance(parent, Gtk.Window):
            raise TypeError("parent must be an instance of Gtk.Window")

        self.parent = parent

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('config/themes/theme.css')
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.13, 0.13, 0.13, 1))

        title_label = Gtk.Label(label="Calibration")
        title_label.get_style_context().add_class("title")
        title_label.set_xalign(0.5)
        title_box.pack_start(title_label, True, True, 0)

        skip_button = Gtk.Button(label="Skip")
        skip_button.get_style_context().add_class('button2')
        skip_button.connect("clicked", self.on_skip_clicked)
        
        title_box.pack_start(skip_button, False, False, 0)
        self.pack_start(title_box, False, False, 0)

        self.fan_test_switch = self.create_test_item("Fan Test", active=True)
        self.axis_test_switch = self.create_test_item("Axis Check", active=True)
        self.speed_test_switch = self.create_test_item("Speed Test", active=True)
        self.speed_test_switch['box'].hide()

        test_items_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        test_items_box.set_halign(Gtk.Align.CENTER)
        test_items_box.pack_start(self.fan_test_switch['box'], False, False, 5)
        test_items_box.pack_start(self.axis_test_switch['box'], False, False, 5)

        self.pack_start(test_items_box, False, False, 20)

        # Create a horizontal box for the Start button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)

        self.calibrate_button = Gtk.Button(label="Start Calibration")
        self.calibrate_button.get_style_context().add_class('button1')
        self.calibrate_button.set_size_request(200, -1)  # Ajuster la largeur du bouton
        self.calibrate_button.connect("clicked", self.on_calibrate_clicked)
        
        button_box.pack_start(self.calibrate_button, True, True, 0)  # Utiliser True pour permettre l'expansion
        self.pack_start(button_box, False, False, 20)  # Ajouter le button_box à CalibrationStep

    def create_test_item(self, label_text, active=False):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_halign(Gtk.Align.FILL)

        label = Gtk.Label(label=label_text)
        label.get_style_context().add_class("test-label")
        label.set_xalign(0)

        switch = Gtk.Switch()
        switch.set_active(active)
        switch.set_size_request(60, 30)

        box.pack_start(label, True, True, 0)
        box.pack_start(switch, False, False, 0)
        
        return {"box": box, "switch": switch, "label": label}

    def on_calibrate_clicked(self, button):
        if not self.check_printer_connection():
            print("Error: Printer not connected")
            return

        self.set_all_buttons_sensitive(False)
        threading.Thread(target=self.run_tests_sequentially).start()

    def run_tests_sequentially(self):
        if self.fan_test_switch["switch"].get_active():
            self.run_test(self.fan_test_switch, self.run_fan_test)
            GLib.idle_add(self.pause_between_tests)
        
        if self.axis_test_switch["switch"].get_active():
            self.run_test(self.axis_test_switch, self.run_axis_test)
            GLib.idle_add(self.pause_between_tests)

        GLib.idle_add(lambda: self.set_all_buttons_sensitive(True))

    def run_test(self, test_item, test_function):
        GLib.idle_add(self.update_test_status, test_item, "in_progress")
        success = test_function()
        GLib.idle_add(self.update_test_status, test_item, "success" if success else "failed")

    def update_test_status(self, test_item, status):
        status_text = ""
        icon_name = ""
        if status == "in_progress":
            status_text = "In Progress..."
            icon_name = "process-working-symbolic"
        elif status == "success":
            status_text = "Success!"
            icon_name = "emblem-ok-symbolic"
        else:
            status_text = "Failed!"
            icon_name = "dialog-error-symbolic"
        
        test_item["label"].set_text(status_text)

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
        time.sleep(5)

    def set_all_buttons_sensitive(self, sensitive):
        for test_item in [self.fan_test_switch, self.axis_test_switch]:
            test_item["switch"].set_sensitive(sensitive)
        
        self.calibrate_button.set_sensitive(sensitive)

    def check_printer_connection(self):
        return True

    def run_fan_test(self):
        try:
            home_command = "G28"
            response = requests.post(
                'http://localhost:7125/printer/gcode/script',
                json={"script": home_command},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 200:
                print(f"Error sending {home_command}: Status Code {response.status_code}")
                return False

            time.sleep(5)
                                  
            speeds = [0, 51, 102, 153, 204, 255, 255, 255, 0]
            fan_commands = [
                {"name": "Extruder Fan", "command": "M106 S", "fan_id": "extruder"},
            ]

            for fan in fan_commands:
                for speed in speeds:
                    command = f"{fan['command']}{speed}"
                    response = requests.post(
                        'http://localhost:7125/printer/gcode/script',
                        json={"script": command},
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code != 200:
                        print(f"Error sending {command} for {fan['name']}: Status Code", response.status_code)
                        return False
                    time.sleep(5)

            return True

        except requests.RequestException as e:
            print("Error during fan test:", e)
            return False

    def run_axis_test(self):
        try:
            home_command = "G28"
            response = requests.post(
                'http://localhost:7125/printer/gcode/script',
                json={"script": home_command},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 200:
                print(f"Error sending {home_command}: Status Code {response.status_code}")
                return False

            time.sleep(5)

            commands = [
                {"name": "X", "command": "G1 X100 F3000"},
                {"name": "Y", "command": "G1 Y100 F3000"},
                {"name": "Z", "command": "G1 Z100 F3000"},
            ]

            for axis in commands:
                response = requests.post(
                    'http://localhost:7125/printer/gcode/script',
                    json={"script": axis["command"]},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code != 200:
                    print(f"Error sending {axis['command']} for {axis['name']} axis: Status Code", response.status_code)
                    return False
                time.sleep(5)

            return True

        except requests.RequestException as e:
            print("Error during axis test:", e)
            return False

    def on_skip_clicked(self, button):
        #print("Calibration skipped.")
        self.parent.next_step()

class MainApplication(Gtk.Window):
    def __init__(self):
        super().__init__(title="3D Printer Configuration")
        self.set_default_size(400, 600)
        self.set_border_width(10)

        self.calibration_step = CalibrationStep(self, None)
        self.add(self.calibration_step)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

if __name__ == "__main__":
    app = MainApplication()
    Gtk.main()
