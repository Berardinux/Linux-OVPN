import gi
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from gi.repository import GdkPixbuf
from read_write_json import ReadWriteJSON

class StatisticsWindowUIComponents:
    def __init__(self):
        self.header_box = None
        self.header_label = None
        self.body_box = None
        self.config=ReadWriteJSON().read_config()
        self.theme = self.config.get("theme", "light")

        self.bits_in_value_label = None
        self.bits_out_value_label = None
        self.tun_bytes_in_value_label = None
        self.tun_bytes_out_value_label = None
        
        self.update_bits_timeout_id = None

    def create_statistics_header_box(self, callback):
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
        self.header_label = Gtk.Label("Statistics")
        self.header_label.set_halign(Gtk.Align.CENTER)
        self.header_label.get_style_context().add_class("Statistics")
        self.header_box.pack_start(self.header_label, True, True, 0)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_size_request(80, -1)
        self.header_box.pack_start(spacer, False, False, 0)

        return self.header_box

    def create_statistics_body_box(self):
        self.body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.body_box.set_name("custom-body")
        self.body_box.set_margin_top(20)
        self.body_box.set_margin_left(40)
        self.body_box.set_margin_right(40)

        bits_in_label = Gtk.Label(label="BYTES IN ⬇️")
        bits_in_label.get_style_context().add_class("h6")
        bits_in_label.get_style_context().add_class("color1")
        bits_in_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(bits_in_label, False, False, 0)

        self.bits_in_value_label = Gtk.Label()
        self.bits_in_value_label.get_style_context().add_class("h6")
        self.bits_in_value_label.get_style_context().add_class("color0")
        self.bits_in_value_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(self.bits_in_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.body_box.pack_start(v_spacer, False, False, 0)

        bits_out_label = Gtk.Label(label="BYTES OUT ⬆️")
        bits_out_label.get_style_context().add_class("h6")
        bits_out_label.get_style_context().add_class("color1")
        bits_out_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(bits_out_label, False, False, 0)

        self.bits_out_value_label = Gtk.Label()
        self.bits_out_value_label.get_style_context().add_class("h6")
        self.bits_out_value_label.get_style_context().add_class("color0")
        self.bits_out_value_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(self.bits_out_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.body_box.pack_start(v_spacer, False, False, 0)

        tun_bytes_in_label = Gtk.Label(label="TUN BYTES IN ⬇️")
        tun_bytes_in_label.get_style_context().add_class("h6")
        tun_bytes_in_label.get_style_context().add_class("color1")
        tun_bytes_in_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(tun_bytes_in_label, False, False, 0)

        self.tun_bytes_in_value_label = Gtk.Label()
        self.tun_bytes_in_value_label.get_style_context().add_class("h6")
        self.tun_bytes_in_value_label.get_style_context().add_class("color0")
        self.tun_bytes_in_value_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(self.tun_bytes_in_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.body_box.pack_start(v_spacer, False, False, 0)

        tun_bytes_out_label = Gtk.Label(label="TUN BYTES OUT ⬆️")
        tun_bytes_out_label.get_style_context().add_class("h6")
        tun_bytes_out_label.get_style_context().add_class("color1")
        tun_bytes_out_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(tun_bytes_out_label, False, False, 0)

        self.tun_bytes_out_value_label = Gtk.Label()
        self.tun_bytes_out_value_label.get_style_context().add_class("h6")
        self.tun_bytes_out_value_label.get_style_context().add_class("color0")
        self.tun_bytes_out_value_label.set_halign(Gtk.Align.START)
        self.body_box.pack_start(self.tun_bytes_out_value_label, False, False, 0)

        v_spacer = Gtk.Label(label="")
        self.body_box.pack_start(v_spacer, False, False, 0)

        self.body_box.show_all()

        return self.body_box

    def update_labels(self):
        rw_json = ReadWriteJSON()
        stats = rw_json.read_statistics()

        self.bits_in_value_label.set_text(self.format_bytes(stats.get("tcp_bytes_in", 0)))
        self.bits_out_value_label.set_text(self.format_bytes(stats.get("tcp_bytes_out", 0)))
        self.tun_bytes_in_value_label.set_text(self.format_bytes(stats.get("tun_bytes_in", 0)))
        self.tun_bytes_out_value_label.set_text(self.format_bytes(stats.get("tun_bytes_out", 0)))

        return True

    def start_updating(self, interval_ms=1000):
        if self.update_bits_timeout_id:
            GLib.source_remove(self.update_bits_timeout_id)
        self.update_labels()
        self.update_bits_timeout_id = GLib.timeout_add(interval_ms, self.update_labels)

    def stop_updating(self):
        if self.update_bits_timeout_id:
            GLib.source_remove(self.update_bits_timeout_id)
            self.update_bits_timeout_id = None

    @staticmethod
    def format_bytes(num_bytes):
        for unit in ["bytes", "KB", "MB", "GB", "TB"]:
            if num_bytes < 1024.0:
                return f"{num_bytes:.2f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.2f} PB"
