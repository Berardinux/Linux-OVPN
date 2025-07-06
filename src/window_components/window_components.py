import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from load_css import LoadCSS
from read_write_json import ReadWriteJSON
from window_components.profiles_window_components import ProfilesWindowUIComponents
from window_components.statistics_window_components import StatisticsWindowUIComponents
from window_components.settings_window_components import SettingsWindowUIComponents
from window_components.cert_and_tok_window_components import CertAndTokWindowUIComponents
from window_components.add_proxy_window_components import AddProxyWindowUIComponents
from window_components.proxies_window_components import ProxiesWindowUIComponents
from window_components.import_profile_window_components import ImportProfileWindowUIComponents
from window_components.imported_profile_window_components import ImportedProfileWindowUIComponents
from window_components.edit_profile_window_components import EditProfileWindowUIComponents
from window_components.logs_window_components import LogsWindowUIComponents

class WindowUIComponents:
    def __init__(self):
        self.win = None
        self.stack = None
        self.overlay = None

    def create_window(self):
        self.win = Gtk.Window()
        self.win.set_title("LinuxOVPN")
        self.win.set_default_size(500, 800)
        self.win.set_resizable(False)
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.connect("destroy", Gtk.main_quit)
        self.win.set_keep_above(True)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.stack.set_transition_duration(0)

        screen = Gdk.Screen.get_default()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.win.set_visual(visual)

        self.win.set_app_paintable(True)
        self.win.connect("draw", self.on_draw_background)

        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        frame.set_name("main-frame")
        frame.add(self.stack)


        self.overlay = Gtk.Overlay()
        self.overlay.add(frame)

        self.win.add(self.overlay)
        return self.overlay, self.stack
        
    def on_draw_background(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        return False

class InitWindows:
    def __init__(self, callback):
        LoadCSS().load_styles_css()
        LoadCSS().load_theme_css()
        self.callback = callback
        self.win_ui = WindowUIComponents()
        self.overlay, self.stack = self.win_ui.create_window()

    def init_profiles_window(self):
        self.pro_ui = ProfilesWindowUIComponents()
        header_box = self.pro_ui.create_profiles_header_box(
                hamburger_button_clicked=self.pro_ui.open_sidebar, 
                list_button_clicked=self.callback.logs_window
                )
        body_box = self.pro_ui.create_profiles_body_box(
                edit_profile_button_clicked=self.callback.edit_profile_window
                )
        footer_box = self.pro_ui.create_profiles_footer_box(callback=self.callback.import_profile_window)
        profiles_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        profiles_view.pack_start(header_box, False, False, 0)
        profiles_view.pack_start(body_box, True, True, 0)
        profiles_view.pack_start(footer_box, False, False, 0)

        profiles_overlay = Gtk.Overlay()
        profiles_overlay.add(profiles_view)

        self.profiles_dimmer = Gtk.EventBox()
        self.profiles_dimmer.set_visible_window(True)
        self.profiles_dimmer.override_background_color(
                Gtk.StateFlags.NORMAL,
                Gdk.RGBA(0, 0, 0, 0.5)
                )

        self.profiles_dimmer.set_halign(Gtk.Align.FILL)
        self.profiles_dimmer.set_valign(Gtk.Align.FILL)
        self.profiles_dimmer.set_hexpand(True)
        self.profiles_dimmer.set_vexpand(True)
        self.profiles_dimmer.set_no_show_all(True)
        self.profiles_dimmer.hide()

        profiles_overlay.add_overlay(self.profiles_dimmer)

        self.stack.add_named(profiles_overlay, "profiles")

        self.stack.set_visible_child_name("profiles")
        self.pro_ui.create_sidebar(
                self.overlay,
                import_profile_callback=self.callback.import_profile_window,
                proxies_callback=self.callback.proxies_window,
                cert_and_tok_callback=self.callback.cert_and_tok_window,
                settings_callback=self.callback.settings_window,
                statistics_callback=self.callback.statistics_window,
                dimmer=self.profiles_dimmer
                )
    def update_edit_profile_data(self, profile_name, profile_data):
        if hasattr(self, 'edpr_ui'):
            self.edpr_ui.set_profile_data(profile_name, profile_data)
            self.edpr_ui.profiles_window_ui = self.pro_ui

    def init_statistics_window(self):
        sta_ui = StatisticsWindowUIComponents()
        statistics_header_box = sta_ui.create_statistics_header_box(callback=self.callback.profiles_window)
        statistics_body_box = sta_ui.create_statistics_body_box()
        statistics_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        statistics_view.pack_start(statistics_header_box, False, False, 0)
        statistics_view.pack_start(statistics_body_box, True, True, 0)
        sta_ui.update_labels()
        sta_ui.start_updating()
        self.stack.add_named(statistics_view, "statistics")
        self.sta_ui = sta_ui

    def init_settings_window(self):
        set_ui = SettingsWindowUIComponents()
        settings_header_box = set_ui.create_settings_header_box(callback=self.callback.profiles_window)
        settings_body_box = set_ui.create_settings_body_box(callback=self.reload_theme_dependent_pages)
        settings_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        settings_view.pack_start(settings_header_box, False, False, 0)
        settings_view.pack_start(settings_body_box, True, True, 0)
        self.stack.add_named(settings_view, "settings")

    def reload_theme_dependent_pages(self, theme_value):
        cert_widget = self.stack.get_child_by_name("cert_and_tok")
        if cert_widget:
            self.stack.remove(cert_widget)
        proxies_widget = self.stack.get_child_by_name("proxies")
        if proxies_widget:
            self.stack.remove(proxies_widget)
        import_widget = self.stack.get_child_by_name("import_profile")
        if import_widget:
            self.stack.remove(import_widget)

        self.init_cert_and_tok_window()
        self.init_proxies_window()
        self.init_import_profile_window()

    def init_cert_and_tok_window(self):
        cer_ui = CertAndTokWindowUIComponents()
        cert_and_tok_header_box = cer_ui.create_cert_and_tok_header_box(callback=self.callback.profiles_window)
        cert_and_tok_body_box = cer_ui.create_cert_and_tok_body_box()
        cert_and_tok_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        cert_and_tok_view.pack_start(cert_and_tok_header_box, False, False, 0)
        cert_and_tok_view.pack_start(cert_and_tok_body_box, True, True, 0)
        self.stack.add_named(cert_and_tok_view, "cert_and_tok")

    def init_add_proxy_window(self):
        apr_ui = AddProxyWindowUIComponents()
        add_proxy_header_box = apr_ui.create_add_proxy_header_box(callback=self.callback.proxies_window)
        add_proxy_body_box = apr_ui.create_add_proxy_body_box()
        add_proxy_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        add_proxy_view.pack_start(add_proxy_header_box, False, False, 0)
        add_proxy_view.pack_start(add_proxy_body_box, True, True, 0)
        self.stack.add_named(add_proxy_view, "add_proxy")

    def init_proxies_window(self):
        prx_ui = ProxiesWindowUIComponents()
        proxies_header_box = prx_ui.create_proxies_header_box(callback=self.callback.profiles_window)
        proxies_body_box = prx_ui.create_proxies_body_box()
        proxies_footer_box = prx_ui.create_proxies_footer_box(callback=self.callback.add_proxy_window)
        proxies_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        proxies_view.pack_start(proxies_header_box, False, False, 0)
        proxies_view.pack_start(proxies_body_box, True, True, 0)
        proxies_view.pack_start(proxies_footer_box, False, False, 0)
        self.stack.add_named(proxies_view, "proxies")

    def init_import_profile_window(self):
        imp_ui = ImportProfileWindowUIComponents()
        import_profile_header_box = imp_ui.create_import_profile_header_box(callback=self.callback.profiles_window)
        import_profile_body_box = imp_ui.create_import_profile_body_box(callback=self.callback.imported_profile_window)
        import_profile_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        import_profile_view.pack_start(import_profile_header_box, False, False, 0)
        import_profile_view.pack_start(import_profile_body_box, True, True, 0)
        self.stack.add_named(import_profile_view, "import_profile")

    def init_imported_profile_window(self):
        self.imped_ui = ImportedProfileWindowUIComponents()
        self.imped_ui.win_ui = self.win_ui
        self.imped_ui.init = self
        self.imped_ui.profiles_window_ui = self.pro_ui
        imported_profile_header_box = self.imped_ui.create_imported_profile_header_box(callback=self.callback.import_profile_window)
        imported_profile_body_box = self.imped_ui.create_imported_profile_body_box(
                name_without_ext="", remote_host=""
                )
        imported_profile_footer_box = self.imped_ui.create_imported_profile_footer_box(callback=self.reload_profiles_window)
        self.imped_ui.go_back_callback = self.callback.profiles_window
        imported_profile_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        imported_profile_view.pack_start(imported_profile_header_box, False, False, 0)
        imported_profile_view.pack_start(imported_profile_body_box, True, True, 0)
        imported_profile_view.pack_start(imported_profile_footer_box, False, False, 0)
        self.stack.add_named(imported_profile_view, "imported_profile")

    def activate_profile_switch(self, profile_name):
        if not hasattr(self, "pro_ui"):
            print("[window_components] No pro_ui available.")
            return
    
        switches = self.pro_ui.profile_switch
        print("Switches after reload:", list(switches.keys()))
    
        switch = switches.get(profile_name)
        if switch:
            if not switch.get_active():
                print(f"[window_components] Toggling switch for {profile_name}")
                switch.set_active(True)
            else:
                print(f"[window_components] VPN already active for {profile_name}")
        else:
            print(f"[window_components] No switch found for {profile_name}")

    def update_imported_profile_data(self, filename, profile_name, remote_host):
        if hasattr(self, 'imped_ui'):
            self.imped_ui.set_profile_data(filename, profile_name, remote_host)

    def reload_profiles_window(self):
        prof_widget = self.stack.get_child_by_name("profiles")
        if prof_widget:
            self.stack.remove(prof_widget)

        self.init_profiles_window()
        self.callback.profiles_window() 

    def init_edit_profile_window(self):
        self.edpr_ui = EditProfileWindowUIComponents()
        edit_profile_header_box = self.edpr_ui.create_edit_profile_header_box(
                callback=self.callback.profiles_window,
                save_profile_callback=self.reload_profiles_window
                )
        self.edpr_ui.go_back_callback = self.callback.profiles_window
        edit_profile_body_box = self.edpr_ui.create_edit_profile_body_box()
        edit_profile_footer_box = self.edpr_ui.create_edit_profile_footer_box(callback=self.reload_profiles_window)
        edit_profile_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        edit_profile_view.pack_start(edit_profile_header_box, False, False, 0)
        edit_profile_view.pack_start(edit_profile_body_box, True, True, 0)
        edit_profile_view.pack_start(edit_profile_footer_box, False, False, 0)
        self.stack.add_named(edit_profile_view, "edit_profile")

    def init_logs_window(self):
        log_ui = LogsWindowUIComponents()
        log_ui.start_redirecting_output()
        logs_header_box = log_ui.create_logs_header_box(callback=self.callback.profiles_window)
        logs_body_box = log_ui.create_logs_body_box()
        logs_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        logs_view.pack_start(logs_header_box, False, False, 0)
        logs_view.pack_start(logs_body_box, True, True, 0)
        self.stack.add_named(logs_view, "logs")
