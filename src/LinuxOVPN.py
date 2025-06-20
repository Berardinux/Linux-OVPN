import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import sys
import os
vendor_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'libs')
vendor_path = os.path.abspath(vendor_path)

if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

from load_css import LoadCSS
from read_write_json import ReadWriteJSON
from window_components.window_components import WindowUIComponents
from window_components.window_components import InitWindows

class MainGUI:
    def __init__(self):
        LoadCSS().load_styles_css()
        LoadCSS().load_theme_css()
        self.win_ui = WindowUIComponents()
        self.overlay, self.stack = self.win_ui.create_window()

        self.init = InitWindows(callback=self)
        self.overlay, self.stack = self.init.overlay, self.init.stack
        self.win_ui = self.init.win_ui

        self.init.init_logs_window()
        self.init.init_edit_profile_window()
        self.init.init_imported_profile_window()
        self.init.init_import_profile_window()
        self.init.init_add_proxy_window()
        self.init.init_proxies_window()
        self.init.init_cert_and_tok_window()
        self.init.init_settings_window()
        self.init.init_statistics_window()
        self.init.init_profiles_window()
        self.profiles_window()

    def profiles_window(self, button=None):
        self.win_ui.win.show_all()
        self.stack.set_visible_child_name("profiles")

    def statistics_window(self, button=None):
        self.stack.set_visible_child_name("statistics")
        self.win_ui.win.show_all()

    def settings_window(self, button=None):
        self.stack.set_visible_child_name("settings")
        self.win_ui.win.show_all()

    def cert_and_tok_window(self, button=None):
        self.stack.set_visible_child_name("cert_and_tok")
        self.win_ui.win.show_all()

    def add_proxy_window(self, button=None):
        self.stack.set_visible_child_name("add_proxy")
        self.win_ui.win.show_all()

    def proxies_window(self, button=None):
        self.stack.set_visible_child_name("proxies")
        self.win_ui.win.show_all()

    def import_profile_window(self, button=None):
        self.stack.set_visible_child_name("import_profile")
        self.win_ui.win.show_all()

    def imported_profile_window(self, _, filename=None, profile_name=None, remote_host=None):
        self.init.update_imported_profile_data(filename, profile_name, remote_host)
        self.stack.set_visible_child_name("imported_profile")
        self.win_ui.win.show_all()

    def edit_profile_window(self, button=None, profile_name=None, profile_data=None):
        self.init.update_edit_profile_data(profile_name, profile_data)
        self.stack.set_visible_child_name("edit_profile")
        self.win_ui.win.show_all()

    def logs_window(self, button=None):
        self.stack.set_visible_child_name("logs")
        self.win_ui.win.show_all()




if __name__ == "__main__":
    app = MainGUI()
    Gtk.main()
