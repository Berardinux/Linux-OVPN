import gi
import os
import sys
from stream_redirect import StreamRedirect
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GdkPixbuf, Pango
from read_write_json import ReadWriteJSON

class LogsWindowUIComponents:
    def __init__(self):
        self.header_box = None
        self.header_label = None
        self.body_box = None
        self.scrolled_window = None
        self.log_textview = None
        self.log_buffer = None
        self.redirector = None

        self.config = ReadWriteJSON().read_config()
        self.theme = self.config.get("theme", "light")

    def create_logs_header_box(self, callback):
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
        self.header_label = Gtk.Label("Logs File")
        self.header_label.set_halign(Gtk.Align.CENTER)
        self.header_label.get_style_context().add_class("Logs")
        self.header_box.pack_start(self.header_label, True, True, 0)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_size_request(80, -1)
        self.header_box.pack_start(spacer, False, False, 0)

        return self.header_box

    def create_logs_body_box(self):
        self.body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.body_box.set_name("main-frame")

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.get_style_context().add_class("logs-scrolled-window")
        self.scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC
        )
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_cursor_visible(False)

        font_desc = Pango.FontDescription("Monospace 10")
        self.log_textview.modify_font(font_desc)

        if self.theme == "dark":
            background = Gdk.RGBA(31/255.0, 36/255.0, 37/255.0, 1)   # #1f2425
            text_color = Gdk.RGBA(1, 1, 1, 1)                        # white
        else:
            background = Gdk.RGBA(242/255.0, 242/255.0, 242/255.0, 1) # #f2f2f2
            text_color = Gdk.RGBA(0, 0, 0, 1)                        # black
        
        self.log_textview.override_background_color(Gtk.StateFlags.NORMAL, background)
        self.log_textview.override_color(Gtk.StateFlags.NORMAL, text_color)

        self.log_buffer = self.log_textview.get_buffer()

        self.scrolled_window.add(self.log_textview)

        self.body_box.pack_start(self.scrolled_window, True, True, 0)

        return self.body_box

    def append_log_line(self, line):
        if self.log_buffer is None:
            return

        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, line + "\n")

        mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), True)
        self.log_textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def start_redirecting_output(self):            # [NEW]
        self.redirector = StreamRedirect(self.append_log_line, also_print=True)
        self.redirector.start()
