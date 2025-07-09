import gi
import os

from window_components import graph_widget
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from gi.repository import GdkPixbuf
from datetime import datetime
import subprocess
import getpass
import threading
import time
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
        self.keep_running_statistics = True
        self.stats_thread = None
        self.profile_switch = {}

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
        self.profile_switch.clear()
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
            self.profile_switch[profile_name] = vpn_profile_switch
    
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

        vpn_config = {}

        with open(self.vpn_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split(None, 1)
                if len(parts) == 2:
                    key, value = parts
                    vpn_config[key] = value
                else:
                    vpn_config[parts[0]] = ""

        proto = vpn_config.get("proto", "unknown")
        remote = vpn_config.get("remote", "unknown")

        if remote != "unknown":
            remote_parts = remote.split()
            if len(remote_parts) == 2:
                server, port = remote_parts
            elif len(remote_parts) == 1:
                server, port = remote_parts[0], "unknown"
            else:
                server, port = "unknown", "unknown"
        else:
            server, port = "unknown", "unknown"

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

        graph_widget = VPNGraphWidget(self.status_path)
        graph_widget.set_size_request(-1, 450)
        graph_widget.set_margin_right(10)
        self.connected_body_box.pack_start(graph_widget, True, True, 0)

        bits_in_label = Gtk.Label(label="BITS IN ⬇️")
        bits_in_label.get_style_context().add_class("h6")
        bits_in_label.get_style_context().add_class("color1")
        bits_in_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(bits_in_label, False, False, 0)

        bits_in_value_label = Gtk.Label()
        bits_in_value_label.get_style_context().add_class("h6")
        bits_in_value_label.get_style_context().add_class("color0")
        bits_in_value_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(bits_in_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.connected_body_box.pack_start(v_spacer, False, False, 0)

        bits_out_label = Gtk.Label(label="BITS OUT ⬆️")
        bits_out_label.get_style_context().add_class("h6")
        bits_out_label.get_style_context().add_class("color1")
        bits_out_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(bits_out_label, False, False, 0)

        bits_out_value_label = Gtk.Label()
        bits_out_value_label.get_style_context().add_class("h6")
        bits_out_value_label.get_style_context().add_class("color0")
        bits_out_value_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(bits_out_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.connected_body_box.pack_start(v_spacer, False, False, 0)

        duration_and_packet_received_label = Gtk.Label(label="DURATION")
        duration_and_packet_received_label.get_style_context().add_class("h6")
        duration_and_packet_received_label.get_style_context().add_class("color1")
        duration_and_packet_received_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(duration_and_packet_received_label, False, False, 0)

        duration_value_label = Gtk.Label()
        duration_value_label.get_style_context().add_class("h6")
        duration_value_label.get_style_context().add_class("color0")
        duration_value_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(duration_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.connected_body_box.pack_start(v_spacer, False, False, 0)

        packet_received_label = Gtk.Label(label="PACKET RECEIVED")
        packet_received_label.get_style_context().add_class("h6")
        packet_received_label.get_style_context().add_class("color1")
        packet_received_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(packet_received_label, False, False, 0)

        packet_received_value_label = Gtk.Label()
        packet_received_value_label.get_style_context().add_class("h6")
        packet_received_value_label.get_style_context().add_class("color0")
        packet_received_value_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(packet_received_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.connected_body_box.pack_start(v_spacer, False, False, 0)

        server_public_ip_label = Gtk.Label(label="SERVER PUBLIC IP")
        server_public_ip_label.get_style_context().add_class("h6")
        server_public_ip_label.get_style_context().add_class("color1")
        server_public_ip_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(server_public_ip_label, False, False, 0)

        server_public_ip_value_label = Gtk.Label(label=f"{server}")
        server_public_ip_value_label.get_style_context().add_class("h6")
        server_public_ip_value_label.get_style_context().add_class("color0")
        server_public_ip_value_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(server_public_ip_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.connected_body_box.pack_start(v_spacer, False, False, 0)

        port_and_vpn_protocol_label = Gtk.Label(
                label="PORT                                       VPN PROTOCOL"
                )
        port_and_vpn_protocol_label.get_style_context().add_class("h6")
        port_and_vpn_protocol_label.get_style_context().add_class("color1")
        port_and_vpn_protocol_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(port_and_vpn_protocol_label, False, False, 0)

        port_and_vpn_protocol_value_label = Gtk.Label(
                label=f"{port}                                           {proto}"
                )
        port_and_vpn_protocol_value_label.get_style_context().add_class("h6")
        port_and_vpn_protocol_value_label.get_style_context().add_class("color0")
        port_and_vpn_protocol_value_label.set_halign(Gtk.Align.START)
        self.connected_body_box.pack_start(port_and_vpn_protocol_value_label, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_propagate_natural_height(False)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        viewport = Gtk.Viewport()
        viewport.add(self.connected_body_box)
        scrolled_window.add(viewport)

        self.body_box.pack_start(scrolled_window, True, True, 0)
        self.body_box.show_all()
        
        elapsed_seconds = 0

        def update_labels():
            nonlocal elapsed_seconds
            elapsed_seconds += 1
        
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            duration_value_label.set_text(duration_str)
        
            bits_in_value_label.set_text(
                f"{graph_widget.last_download_mbps:.2f} Mbps"
            )
            bits_out_value_label.set_text(
                f"{graph_widget.last_upload_mbps:.2f} Mbps"
            )
        
            bytes_received = 0
            try:
                with open(self.status_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("TUN/TAP read bytes"):
                            parts = line.split(",")
                            if len(parts) == 2:
                                bytes_received = int(parts[1])
                                break
            except FileNotFoundError:
                packet_received_value_label.set_text("VPN stopped")
                if hasattr(self, "update_bits_timeout_id") and self.update_bits_timeout_id:
                    GLib.source_remove(self.update_bits_timeout_id)
                    self.update_bits_timeout_id = None
                    print("Stopped update_labels timer because VPN stopped.")
                self.status_path = None
                return False
            except Exception as e:
                print(f"Error reading status file: {e}")
                return False
        
            if bytes_received == 0:
                packet_received_value_label.set_text("waiting...")
            else:
                packet_received_value_label.set_text(f"{bytes_received:,} bytes")
        
            return True
        
        self.update_bits_timeout_id = GLib.timeout_add(1000, update_labels)

    def _stats_worker(self):
        while self.keep_running_statistics:
            keep_going = self.update_statistics_file()
            if not keep_going:
                break
            time.sleep(1)

    def update_statistics_file(self):
        tun_bytes_in = 0
        tun_bytes_out = 0
        tcp_bytes_in = 0
        tcp_bytes_out = 0
        tun_packets_in = 0
        tun_packets_out = 0
        tcp_packets_in = 0
        tcp_packets_out = 0
    
        if not os.path.exists(self.status_path):
            print("[DEBUG] VPN is off. Keeping previous statistics.json unchanged.")
            return False
    
        time.sleep(1)
    
        try:
            with open(self.status_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TUN/TAP read bytes"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tun_bytes_in = int(parts[1])
                    elif line.startswith("TUN/TAP write bytes"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tun_bytes_out = int(parts[1])
                    elif line.startswith("TCP/UDP read bytes"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tcp_bytes_in = int(parts[1])
                    elif line.startswith("TCP/UDP write bytes"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tcp_bytes_out = int(parts[1])
                    elif line.startswith("TUN/TAP read packets"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tun_packets_in = int(parts[1])
                    elif line.startswith("TUN/TAP write packets"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tun_packets_out = int(parts[1])
                    elif line.startswith("TCP/UDP read packets"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tcp_packets_in = int(parts[1])
                    elif line.startswith("TCP/UDP write packets"):
                        parts = line.split(",")
                        if len(parts) == 2:
                            tcp_packets_out = int(parts[1])
        except Exception as e:
            print(f"Error reading status file: {e}")
            return True
    
        packets_in = tun_packets_in + tcp_packets_in
        packets_out = tun_packets_out + tcp_packets_out
    
        rw_json = ReadWriteJSON()
        stats = {
            "tun_bytes_in": tun_bytes_in,
            "tun_bytes_out": tun_bytes_out,
            "tcp_bytes_in": tcp_bytes_in,
            "tcp_bytes_out": tcp_bytes_out,
            "tun_packets_in": tun_packets_in,
            "tun_packets_out": tun_packets_out,
            "packets_in": packets_in,
            "packets_out": packets_out,
        }
        rw_json.write_statistics(stats)
        return True

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
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.status_path = f"/tmp/openvpn-status-{profile_name}-{timestamp}.log"

        if self.turn_off_vpn_cancel:
            self.turn_off_vpn_cancel = False
            return True
        elif state:
            print("User clicked ON")
    
            used_passwd = profile_data.get("used_passwd")
            passwd = profile_data.get("passwd")
            filename = profile_data.get("filename")
            self.vpn_path = os.path.join(
                "/opt/LinuxOVPN/docs/user_ovpn_files", filename
            )
   
            try:
                username = getpass.getuser()
                script_path = "../scripts/start_vpn_connection.sh"
                script_args = ["pkexec", script_path, self.vpn_path, self.status_path, username]

                if not used_passwd:
                    passwd=""
                script_args.append(passwd)

                process = subprocess.Popen(
                        script_args,
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
                            print("VPN script canceled or failed.")
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

                if self.stats_thread is None or not self.stats_thread.is_alive():
                    self.keep_running_statistics = True
                    self.stats_thread = threading.Thread(target=self._stats_worker, daemon=True)
                    self.stats_thread.start()

                return True
    
            except Exception as e:
                print("Error launching VPN script:", e)
                self._recreate_profiles_ui()
                return True

        else:
            print("Switch is off")
            self.keep_running_statistics = False

            if getattr(self, "stats_thread", None) is not None and self.stats_thread.is_alive():
                self.stats_thread.join(timeout=2)
                self.stats_thread = None
        
            if hasattr(self, "vpn_process") and self.vpn_process:
                bash_pid = str(self.vpn_process.pid)

                try:
                    with open("/tmp/openvpn.pid", "r") as f:
                        openvpn_pid = f.read().strip()
                except FileNotFoundError:
                    print("Could not read /tmp/openvpn.pid; OpenVPN process might not have started.")
                    openvpn_pid = None

                kill_args = ["pkexec", "kill", "-9", bash_pid]
                if openvpn_pid:
                    kill_args.append(openvpn_pid)

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
