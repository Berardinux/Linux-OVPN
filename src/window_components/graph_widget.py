import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from read_write_json import ReadWriteJSON

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import random

class VPNGraphWidget(Gtk.Box):
    def __init__(self):
        self.config=ReadWriteJSON().read_config()
        self.theme = self.config.get("theme", "light")

        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_vexpand(True)

        # dark = #1f2425
        # light = #f2f2f2
        if (self.theme == "dark"):
            background_color=("#1f2425")
            text_color=("white")
        else:
            background_color=("#f2f2f2")
            text_color=("black")

        self.fig = Figure(figsize=(5, 2), dpi=100)
        self.fig.patch.set_facecolor(background_color)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(background_color)
        self.ax.relim()
        self.ax.autoscale_view()

        self.ax.set_xlabel("Seconds", color=text_color)
        self.ax.set_ylabel("MBps", color=text_color)
        self.ax.tick_params(axis="x", colors=text_color)
        self.ax.tick_params(axis="y", colors=text_color)

        self.x_data = list(range(0, 121))
        self.download_data = [0] * 121
        self.upload_data = [0] * 121

        self.download_line, = self.ax.plot(
                self.download_data, 
                label="Download", 
                color="yellow"
                )
        self.upload_line, = self.ax.plot(
                self.upload_data, 
                label="Upload", 
                color="orange"
                )

        self.download_fill = self.ax.fill_between(
                range(len(self.download_data)), 
                self.download_data, 
                color="yellow", 
                alpha=0.3,
                )
        self.upload_fill = self.ax.fill_between(
                range(len(self.upload_data)), 
                self.upload_data, 
                color="orange", 
                alpha=0.3,
                )

        ticks = list(range(0, 121, 20))
        labels = [str(120 - t) for t in ticks]

        self.ax.set_xticks(ticks)
        self.ax.set_xticklabels(labels, color=text_color)

        self.ax.set_xlim(0, 120)

        legend = self.ax.legend(loc="upper left")
        legend.get_frame().set_facecolor(background_color)
        legend.get_frame().set_alpha(1.0)
        for text in legend.get_texts():
            text.set_color(text_color)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(text_color)
            spine.set_linewidth(0.8)

        self.canvas = FigureCanvas(self.fig)
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        frame.set_margin_top(1)
        frame.set_margin_bottom(0)
        frame.set_margin_left(0)
        frame.set_margin_right(0)
        frame.add(self.canvas)
        self.fig.tight_layout()
        self.pack_start(frame, True, True, 0)

        GLib.timeout_add(1000, self.update_graph)

    def update_graph(self):
        self.download_data.pop(0)
        self.upload_data.pop(0)

        self.download_data.append(random.randint(10, 100))
        self.upload_data.append(random.randint(5, 500))

        self.download_line.set_ydata(self.download_data)
        self.download_line.set_xdata(range(len(self.download_data)))

        self.upload_line.set_ydata(self.upload_data)
        self.upload_line.set_xdata(range(len(self.upload_data)))

        self.download_fill.remove()
        self.upload_fill.remove()
        self.download_fill = self.ax.fill_between(
                range(len(self.download_data)), self.download_data, color = "yellow", alpha=0.3
                )
        self.upload_fill = self.ax.fill_between(
                range(len(self.upload_data)), self.upload_data, color="orange", alpha=0.3
                )

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        return True
