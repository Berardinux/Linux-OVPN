import gi
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GdkPixbuf
import subprocess
import tempfile
from read_write_json import ReadWriteJSON
from window_components.graph_widget import VPNGraphWidget

class ProfilesWindowUIComponents:
    def __init__(self):
        self.header_box = None
        self.header_label = None
        self.body_box = None
        self.footer_box = None
        self.revealer = None
        self.config=ReadWriteJSON().read_config()
        self.theme = self.config.get("theme", "light")
        self.turn_off_vpn_cancel = False

    def create_profiles_header_box(self, hamburger_button_clicked, list_button_clicked):
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.header_box.set_size_request(500, 55)
        self.header_box.set_name("custom-header")
       
        # Hamburger button
        icon = Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
        icon.set_pixel_size(32)
        hamburger_button = Gtk.Button()
        hamburger_button.set_image(icon)
        hamburger_button.set_relief(Gtk.ReliefStyle.NONE)
        hamburger_button.get_style_context().add_class("hamburger-btn")
        hamburger_button.connect("clicked", hamburger_button_clicked)
        self.header_box.pack_start(hamburger_button, False, False, 0)

        # Header label
        self.header_label = Gtk.Label("Profiles")
        self.header_label.set_halign(Gtk.Align.CENTER)
        self.header_label.get_style_context().add_class("Profiles")
        self.header_box.pack_start(self.header_label, True, True, 0)

        # Scroll button
        path = "../images/" + self.theme + "/ovpn_scroll.png"
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                path , 32, 32,
                preserve_aspect_ratio=True
                )
        view_icon = Gtk.Image.new_from_pixbuf(pixbuf)
        list_button = Gtk.Button()
        list_button.set_image(view_icon)
        list_button.set_relief(Gtk.ReliefStyle.NONE)
        list_button.get_style_context().add_class("list-btn")
        list_button.connect("clicked", list_button_clicked)
        self.header_box.pack_start(list_button, False, False, 0)

        return self.header_box

    def create_profiles_body_box(self, edit_profile_button_clicked):
        self.edit_profile_button_clicked = edit_profile_button_clicked
    
        if not self.body_box:
            self.body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.body_box.set_name("custom-body")
            self.body_box.set_margin_top(20)
            self.body_box.set_margin_left(40)
            self.body_box.set_margin_right(40)
    
        # Clear previous content if any
        for child in self.body_box.get_children():
            self.body_box.remove(child)
    
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.body_box.pack_start(self.content_box, True, True, 0)
    
        disconnected_label = Gtk.Label(label="DISCONNECTED")
        disconnected_label.get_style_context().add_class("h5")
        disconnected_label.get_style_context().add_class("color3")
        disconnected_label.set_halign(Gtk.Align.START)
        disconnected_label.set_valign(Gtk.Align.START)
        disconnected_label.set_margin_bottom(20)
        self.content_box.pack_start(disconnected_label, False, False, 0)
    
        config = ReadWriteJSON().read_config()
        self.profiles = config.get("profiles", {})
    
        for profile_name, profile_data in self.profiles.items():
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.set_margin_bottom(20)
    
            vpn_profile_switch = Gtk.Switch()
            vpn_profile_switch.set_halign(Gtk.Align.START)
            vpn_profile_switch.set_name(profile_name)
            vpn_profile_switch.set_size_request(70, -1)
            vpn_profile_switch.connect("state-set", self.on_profile_button_click, profile_name, profile_data)
    
            profile_name_label = Gtk.Label(label=profile_name)
            profile_name_label.get_style_context().add_class("h5")
            profile_name_label.get_style_context().add_class("color1")
            profile_name_label.set_halign(Gtk.Align.CENTER)
            profile_name_label.set_hexpand(True)
    
            edit_profile_button = Gtk.Button()
            edit_profile_button.set_relief(Gtk.ReliefStyle.NONE)
            edit_icon = Gtk.Image.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.BUTTON)
            edit_icon.set_pixel_size(24)
            edit_profile_button.set_image(edit_icon)
            edit_profile_button.set_tooltip_text("Edit profile")
            edit_profile_button.get_style_context().add_class("color1")
            edit_profile_button.connect("clicked", self.on_edit_profile_button_click,
                                        profile_name, profile_data, edit_profile_button_clicked)
    
            row.pack_start(vpn_profile_switch, False, False, 0)
            row.pack_start(profile_name_label, True, True, 0)
            row.pack_start(edit_profile_button, False, False, 0)
            self.content_box.pack_start(row, False, False, 0)
    
        return self.body_box
    
    def refresh_connected_view(self, profile_name, profile_data):
        for child in self.body_box.get_children():
            self.body_box.remove(child)

        self.connected_body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.connected_body_box.set_name("custom-body")

        connected_label = Gtk.Label(label="CONNECTED")
        connected_label.get_style_context().add_class("h5")
        connected_label.get_style_context().add_class("color3")
        connected_label.set_halign(Gtk.Align.START)
        connected_label.set_valign(Gtk.Align.START)
        connected_label.set_margin_bottom(20)
        self.connected_body_box.pack_start(connected_label, False, False, 0)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.set_margin_bottom(20)

        vpn_profile_switch = Gtk.Switch()
        vpn_profile_switch.set_active(True)
        vpn_profile_switch.set_name(profile_name)
        vpn_profile_switch.set_size_request(70, 35)
        vpn_profile_switch.connect("state-set", self.on_profile_button_click, profile_name, profile_data)

        profile_name_label = Gtk.Label(label=profile_name)
        profile_name_label.get_style_context().add_class("h5")
        profile_name_label.get_style_context().add_class("color1")
        profile_name_label.set_halign(Gtk.Align.CENTER)
        profile_name_label.set_hexpand(True)

        spacer = Gtk.Box()
        spacer.set_size_request(36, -1)

        row.pack_start(vpn_profile_switch, False, False, 0)
        row.pack_start(profile_name_label, True, True, 0)
        row.pack_start(spacer, False, False, 0)
        self.connected_body_box.pack_start(row, False, False, 0)

        graph_widget = VPNGraphWidget()
        self.connected_body_box.pack_start(graph_widget, True, True, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_propagate_natural_height(False)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.connected_body_box)

        self.body_box.pack_start(scrolled_window, True, True, 0)
        self.body_box.show_all()

    def on_edit_profile_button_click(self, button, profile_name, profile_data, edit_profile_button_clicked):
        print("Edit button clicked { ")
        print("Profile name: " + profile_name)
        print("Profile data: ", profile_data)
        print("}")
        edit_profile_button_clicked(self, profile_name, profile_data)

    def _recreate_profiles_ui(self):
        """Clear and rebuild the profiles body box."""
        for child in self.body_box.get_children():
            self.body_box.remove(child)
        self.create_profiles_body_box(self.edit_profile_button_clicked)
        self.body_box.show_all()

    def on_profile_button_click(self, switch, state, profile_name, profile_data):
        print(">>> on_profile_button_click called with state =", state)
    
        if self.turn_off_vpn_cancel:
            self.turn_off_vpn_cancel = False
            return True
        elif state:
            print("User clicked ON")
    
            used_passwd = profile_data.get("used_passwd")
            passwd = profile_data.get("passwd")
            filename = profile_data.get("filename")
            vpn_path = os.path.join(
                "/opt/LinuxOVPN/docs/user_ovpn_files", filename
            )
   
            temp_pass_file = None

            try:
                if used_passwd:
                    temp_pass_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
                    temp_pass_file.write(passwd + "\n")
                    temp_pass_file.close()
                    openvpn_args = ["pkexec", "openvpn", "--config", vpn_path, "--askpass", temp_pass_file.name]
                else:
                    openvpn_args = ["pkexec", "openvpn", "--config", vpn_path]
    
                process = subprocess.Popen(
                    openvpn_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
    
                vpn_initialized = False
                for line in process.stdout:
                    print(line, end="")
                    if "Initialization Sequence Completed" in line:
                        vpn_initialized = True
                        break
    
                    if process.poll() is not None:
                        if process.returncode != 0:
                            print("pkexec canceled or failed.")
                            self._recreate_profiles_ui()
                            return True
                        else:
                            break
    
                if not vpn_initialized:
                    print("VPN did not initialize properly.")
                    self._recreate_profiles_ui()
                    return True
    
                print("Started VPN process with PID:", process.pid)
                self.vpn_process = process
    
                switch.set_active(True)
    
                for child in self.body_box.get_children():
                    self.body_box.remove(child)
                self.refresh_connected_view(profile_name, profile_data)
    
                return True
    
            except Exception as e:
                print("Error launching OpenVPN:", e)
                self._recreate_profiles_ui()
                return True

            finally:
                if used_passwd and temp_pass_file:
                    try:
                        os.unlink(temp_pass_file.name)
                        print("Deleted temp password file: ", temp_pass_file.name)
                    except Exception as e:
                        print("Could not delete temp password file: ", e)

        else:
            print("Switch is off")
        
            if hasattr(self, "vpn_process") and self.vpn_process:
                pid = str(self.vpn_process.pid)
                kill_args = ["pkexec", "kill", "-9", pid]

                process = subprocess.Popen(
                    kill_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
        
                output = ""
                for line in process.stdout:
                    print(line, end="")
                    output += line
        
                process.wait()
        
                if process.returncode != 0:
                    print("pkexec canceled or failed. VPN still running.")
                    self.turn_off_vpn_cancel = True
                    switch.set_active(True)
                    return True
        
                print("VPN process stopped.")
                self.vpn_process = None
        
                switch.set_active(False)
        
            for child in self.body_box.get_children():
                self.body_box.remove(child)
            self.create_profiles_body_box(self.edit_profile_button_clicked)
            self.body_box.show_all()
        
            return True

 
    def create_profiles_footer_box(self, callback):
        self.footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.footer_box.set_size_request(500, 100)
        self.footer_box.set_name("custom-footer")

        self.footer_box.pack_start(Gtk.Box(), True, True, 0)

        # Import profile button
        path = "../images/" + self.theme + "/ovpn_plus.png"
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                path, 60, 60,
                preserve_aspect_ratio=True
                )
        view_icon = Gtk.Image.new_from_pixbuf(pixbuf)
        import_profile_button = Gtk.Button()
        import_profile_button.set_image(view_icon)
        import_profile_button.set_relief(Gtk.ReliefStyle.NONE)
        import_profile_button.get_style_context().add_class("import_profile_btn")
        import_profile_button.connect("clicked", callback)
        self.footer_box.pack_start(import_profile_button, False, False, 0)

        return self.footer_box

    def create_sidebar(
            self, overlay,
            import_profile_callback=None,
            proxies_callback=None,
            cert_and_tok_callback = None,
            settings_callback=None,
            statistics_callback=None,
            dimmer=None
            ):
        self.profiles_dimmer = dimmer
        self.import_profile_callback = import_profile_callback
        self.proxies_callback = proxies_callback
        self.cert_and_tok_callback = cert_and_tok_callback
        self.settings_callback = settings_callback
        self.statistics_callback = statistics_callback

        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.revealer.set_transition_duration(300)

        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar.set_size_request(250, -1)
        sidebar.set_name("sidebar")
        sidebar.get_style_context().add_class("sidebar")

        # Spacer
        spacer = Gtk.Box()
        spacer.set_size_request(-1, 40)
        sidebar.pack_start(spacer, False, False, 0)

        buttons = {
                "Import Profile": lambda btn: (self.close_sidebar(), self.import_profile_callback(btn)),
                "Proxies": lambda btn: (self.close_sidebar(), self.proxies_callback(btn)),
                "Certificates & Tokens": lambda btn: (self.close_sidebar(), self.cert_and_tok_callback(btn)),
                "Settings": lambda btn: (self.close_sidebar(), self.settings_callback(btn)),
                "Statistics": lambda btn: (self.close_sidebar(), self.statistics_callback(btn))
                }

        for label, handler in buttons.items():
            button = Gtk.Button(label=label)
            button.set_margin_left(20)
            button.set_margin_right(20)
            button.connect("clicked", handler)
            sidebar.pack_start(button, False, False, 0)

        self.revealer.add(sidebar)
        self.revealer.set_reveal_child(False)
        self.revealer.set_halign(Gtk.Align.START)
        self.revealer.set_valign(Gtk.Align.FILL)
        overlay.add_overlay(self.revealer)

        self.click_catcher = Gtk.EventBox()
        self.click_catcher.set_visible_window(True)
        self.click_catcher.set_above_child(True)
        self.click_catcher.connect("button-press-event", self._on_click_outside)

        click_area = Gtk.Box()
        click_area.set_size_request(1, 1)
        self.click_catcher.add(click_area)
        
        self.click_catcher.set_margin_left(250)
        self.click_catcher.set_hexpand(True)
        self.click_catcher.set_vexpand(True)
        self.click_catcher.set_valign(Gtk.Align.FILL)
        self.click_catcher.set_halign(Gtk.Align.FILL)
        overlay.add_overlay(self.click_catcher)
        self.click_catcher.set_no_show_all(True)
        self.click_catcher.hide()

    def open_sidebar(self, button=None):
        self.revealer.set_reveal_child(True)
        if self.click_catcher:
            self.profiles_dimmer.show()
            self.click_catcher.show()

    def close_sidebar(self):
        self.revealer.set_reveal_child(False)
        if self.click_catcher:
            self.click_catcher.hide()
            self.profiles_dimmer.hide()

    def _on_click_outside(self, widget, event):
        self.close_sidebar()
        return True
