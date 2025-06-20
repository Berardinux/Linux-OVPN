import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import random

class VPNGraphWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_vexpand(True)

        self.fig = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("kbps")

        self.data = [0] * 50
        self.line, = self.ax.plot(self.data, label="Traffic")
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvas(self.fig)
        self.pack_start(self.canvas, True, True, 0)

        GLib.timeout_add(1000, self.update_graph)

    def update_graph(self):
        self.data.pop(0)
        self.data.append(random.randint(10, 100))
        self.line.set_ydata(self.data)
        self.line.set_xdata(range(len(self.data)))
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        return True
