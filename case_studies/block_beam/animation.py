import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class Animation:
    def __init__(self, x0, length=0.5):
        self.fig, self.ax = plt.subplots(1)
        self.length = length
        self.block_width = length / 10
        ax: plt.Axes = self.ax
        buffer = length/5
        ax.axis([-buffer, length+buffer, -length, length]) # Change the x,y axis limits
        ax.plot([0.0, length], [0.0, 0.0], 'y--')    # Draw a base line
        self._drawBlock(x0)
        self._drawBeam(x0[1])
        ax.axis('equal')

    def update(self, x):
        z,theta = x[:2]
        c0 = np.cos(theta)
        s0 = np.sin(theta)
        pts = np.array([[0, self.length*c0, (z - self.block_width / 2) * c0],
                        [0, self.length*s0, (z - self.block_width / 2) * s0]])
        # bottom_left_corner = (x, y)
        # self.block.set(xy=bottom_left_corner, angle=np.rad2deg(theta))
        self.block.set(xy=pts[:,-1], angle=np.rad2deg(theta))
        self.beam.set_xdata(pts[0,:2])
        self.beam.set_ydata(pts[1,:2])

    def _drawBlock(self, x0):
        z, theta = x0[:2]
        x = (z - self.block_width / 2) * np.cos(theta)
        y = (z - self.block_width / 2) * np.sin(theta)
        bottom_left_corner = (x, y)

        self.block = mpatches.Rectangle(
            xy=bottom_left_corner, width=self.block_width, height=self.block_width,
            angle=np.rad2deg(theta), rotation_point='xy',
            fc='limegreen', ec='black'
            )
        self.ax.add_patch(self.block)
        return

    def _drawBeam(self, theta):
        x = [0, self.length*np.cos(theta)]
        y = [0, self.length*np.sin(theta)]
        ax: plt.Axes = self.ax
        self.beam, = ax.plot(x, y, lw=2, c='black')


if __name__ == '__main__':
    from ..tabbed_plot_window import TabbedPlotWindow
    length = 0.5
    x = np.array([0.1, np.radians(0), 0, 0])
    animation = Animation(x, length)
    pw = TabbedPlotWindow(size=[800,800])
    pw.addTab('animation', animation.fig)
    for theta in np.arange(0, np.radians(45), 0.01):
        x[0] += 0.01
        x[1] = theta
        animation.update(x)
        pw.pause(0.1)

    pw.show()
