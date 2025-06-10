import gi
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GdkPixbuf
from read_write_json import ReadWriteJSON

class ImportedProfileWindowUIComponents:
    def __init__(self):
        self.header_box = None
        self.header_label = None
        self.body_box = None
        self.footer_box = None
        self.config=ReadWriteJSON().read_config()
        self.theme = self.config.get("theme", "light")

    def create_imported_profile_header_box(self, callback):
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.header_box.set_size_request(500, 55)
        self.header_box.set_name("custom-header")
      
        # Back button
        path = "../images/" + self.theme + "/ovpn_arrow.png"
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                path, 32, 32,
                preserve_aspect_ratio=True
                )
        view_icon = Gtk.Image.new_from_pixbuf(pixbuf)
        back_button = Gtk.Button()
        back_button.set_image(view_icon)
        back_button.set_relief(Gtk.ReliefStyle.NONE)
        back_button.get_style_context().add_class("back-btn")
        back_button.connect("clicked", callback)
        self.header_box.pack_start(back_button, False, False, 0)

        # Header label
        self.header_label = Gtk.Label("Imported Profile")
        self.header_label.set_halign(Gtk.Align.CENTER)
        self.header_label.get_style_context().add_class("ImportedProfile")
        self.header_box.pack_start(self.header_label, True, True, 0)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_size_request(80, -1)
        self.header_box.pack_start(spacer, False, False, 0)

        return self.header_box

    def create_imported_profile_body_box(self):
        self.body_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.body_box.set_name("custom-body")


        
        return self.body_box

    def create_imported_profile_footer_box(self):
        self.footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.footer_box.set_size_request(500, 40)
        self.footer_box.set_name("custom-footer")
        self.footer_box.set_valign(Gtk.Align.END)
        self.footer_box.set_halign(Gtk.Align.CENTER)

        # Footer button
        profiles_button = Gtk.Button(label="PROFILES")
        profiles_button.get_style_context().add_class("add-footer-btn-1")
        profiles_button.set_margin_bottom(20)
        profiles_button.set_margin_left(20)
        profiles_button.set_margin_right(3)
        self.footer_box.pack_start(profiles_button, False, False, 0)

        connect_button = Gtk.Button(label="CONNECT")
        connect_button.get_style_context().add_class("add-footer-btn")
        connect_button.set_margin_bottom(20)
        connect_button.set_margin_right(20)
        self.footer_box.pack_start(connect_button, False, False, 0)

        return self.footer_box






