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
        self.password_row_cache = 0
        self.profile_name
        self.remote_host

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

    def create_imported_profile_body_box(self, name_without_ext, remote_host):
        self.body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.body_box.set_halign(Gtk.Align.START)
        self.body_box.set_valign(Gtk.Align.START)
        self.body_box.set_margin_top(20)
        self.body_box.set_margin_left(40)
        self.body_box.set_margin_right(40)
        self.body_box.set_name("custom-body")

        profile_name = Gtk.Label(label="Profile Name")
        profile_name.get_style_context().add_class("h6")
        profile_name.get_style_context().add_class("color1")
        profile_name.set_halign(Gtk.Align.START)
        self.body_box.pack_start(profile_name, False, False, 0)

        self.entry_profile_name = Gtk.Entry()
        self.entry_profile_name.get_style_context().add_class("entry")
        self.entry_profile_name.set_size_request(420, -1)
        self.entry_profile_name.connect("changed", self.on_server_name_changed)
        self.body_box.pack_start(self.entry_profile_name, False, False, 0)

        server_name = Gtk.Label(label="Server Hostname (locked)")
        server_name.get_style_context().add_class("h6")
        server_name.get_style_context().add_class("color1")
        server_name.set_halign(Gtk.Align.START)
        server_name.set_margin_top(20)
        self.body_box.pack_start(server_name, False, False, 0)

        self.entry_server_name = Gtk.Entry()
        self.entry_server_name.set_editable(False)
        self.entry_server_name.get_style_context().add_class("entry")
        self.body_box.pack_start(self.entry_server_name, False, False, 0)

        check_button_save_private_passwd = Gtk.CheckButton(label="Save Private Key Password")
        check_button_save_private_passwd.set_active(False)
        check_button_save_private_passwd.get_style_context().add_class("h6")
        check_button_save_private_passwd.get_style_context().add_class("color1")
        check_button_save_private_passwd.set_margin_top(20)
        check_button_save_private_passwd.connect("toggled", self.on_checkbox_toggled)
        self.body_box.pack_start(check_button_save_private_passwd, False, False, 0)

        self.password_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        self.entry_private_key_password = Gtk.Entry()
        self.entry_private_key_password.set_placeholder_text("Private Key Password")
        self.entry_private_key_password.set_visibility(False)
        self.entry_private_key_password.set_invisible_char("•")
        self.entry_private_key_password.get_style_context().add_class("entry")
        self.entry_private_key_password.set_size_request(380, -1)

        self.toggle_visibility_btn = Gtk.Button()
        eye_icon = Gtk.Image.new_from_icon_name("view-conceal-symbolic", Gtk.IconSize.BUTTON)
        self.toggle_visibility_btn.set_image(eye_icon)
        self.toggle_visibility_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.toggle_visibility_btn.connect("clicked", self.on_toggle_password_visibility)

        self.body_box.pack_start(self.password_row, False, False, 0)

        return self.body_box

    def on_server_name_changed(self, entry):
        self.profile_name = entry.get_text()
        print("Profile name changed to: " + self.profile_name)

    def set_profile_data(self, profile_name, remote_host):
        if hasattr(self, 'entry_profile_name'):
            self.entry_profile_name.set_text(remote_host + " [" + profile_name + "]")
        if hasattr(self, 'entry_server_name'):
            self.entry_server_name.set_text(remote_host)

        self.profile_name = profile_name
        self.remote_host = remote_host

    def on_toggle_password_visibility(self, button):
        current = self.entry_private_key_password.get_visibility()
        self.entry_private_key_password.set_visibility(not current)

        icon_name = (
                "view-reveal-symbolic" if not current else "view-conceal-symbolic"
                )
        new_icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        self.toggle_visibility_btn.set_image(new_icon)

    def on_checkbox_toggled(self, button):
        if button.get_active():
            if self.password_row_cache == 0:
                self.password_row.pack_start(self.entry_private_key_password, False, False, 0)
                self.password_row.pack_start(self.toggle_visibility_btn, False, False, 0)
                self.password_row_cache += 1
            self.password_row.show_all()
        else:
            self.password_row.hide()

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
        profiles_button.connect("clicked", self.on_profiles_btn_click)
        self.footer_box.pack_start(profiles_button, False, False, 0)

        connect_button = Gtk.Button(label="CONNECT")
        connect_button.get_style_context().add_class("add-footer-btn")
        connect_button.set_margin_bottom(20)
        connect_button.set_margin_right(20)
        connect_button.connect("clicked", self.on_connect_btn_click)
        self.footer_box.pack_start(connect_button, False, False, 0)

        return self.footer_box

    def on_profiles_btn_click(self, button):
        ReadWriteJSON().update_config("profiles", self.profile_name, )
        self.imported_callback

    def on_connect_btn_click(self, button):

        self.imported_callback






