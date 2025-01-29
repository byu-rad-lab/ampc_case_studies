import numpy as np
import matplotlib.pyplot as plt


class Animation:
    def __init__(self):
        self.fig, self.ax = plt.subplots(1)
        self.line, = self.ax.plot([0, 1], [0, 0], 'b', linewidth=5)
        self.pt = self.ax.plot([0], [0], 'k.', markersize=15)
        lims = [-1.25, 1.25]
        self.ax.set_xlim(lims)
        self.ax.set_ylim(lims)

    def update(self, theta):
        c0 = np.cos(theta)
        s0 = np.sin(theta)
        self.line.set_xdata([0, c0])
        self.line.set_ydata([0, s0])


if __name__ == '__main__':
    from tabbed_plot_window import TabbedPlotWindow
    animation = Animation()
    pw = TabbedPlotWindow(size=[800,800])
    pw.addTab('animation', animation.fig)
    for theta in np.arange(0, np.radians(180), 0.1):
        animation.update(theta)
        pw.pause(0.1)

    pw.show()
