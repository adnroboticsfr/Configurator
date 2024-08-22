import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class RegionStep(Gtk.Box):
    def __init__(self, parent, gettext_function):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        global _  # Utiliser la fonction de traduction globale
        _ = gettext_function

        label = Gtk.Label(label=_("Select your region"))
        self.pack_start(label, True, True, 0)

        # Create buttons for region selection
        self.region_buttons = Gtk.Box(spacing=10)
        regions = [_("Asia Pacific"), _("Europe"), _("China"), _("North America"), _("Others")]
        for region in regions:
            button = Gtk.Button(label=region)
            button.connect("clicked", self.on_region_selected)
            self.region_buttons.pack_start(button, True, True, 0)
        
        self.pack_start(self.region_buttons, True, True, 0)

        # Navigation buttons
        nav_box = Gtk.Box(spacing=10)
        self.previous_button = Gtk.Button(label=_("<"))
        self.previous_button.connect("clicked", self.on_previous_clicked)
        nav_box.pack_start(self.previous_button, True, True, 0)

        self.next_button = Gtk.Button(label=_("Next"))
        self.next_button.connect("clicked", self.on_next_clicked)
        nav_box.pack_start(self.next_button, True, True, 0)

        self.pack_start(nav_box, True, True, 0)

    def on_region_selected(self, button):
        print(f"Selected region: {button.get_label()}")

    def on_next_clicked(self, button):
        self.parent.next_step()

    def on_previous_clicked(self, button):
        self.parent.previous_step()
