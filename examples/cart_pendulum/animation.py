import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class Animation:
    def __init__(self, x0, length=1):
        self.fig, self.ax = plt.subplots(1)
        self.length = length
        self.cart_width = length / 2
        self.cart_height = length * 0.15
        self.gap = 0.005
        self.radius = length * 0.06
        ax: plt.Axes = self.ax
        self.buffer = length*3
        ax.axis([x0[0]-self.buffer, x0[0]+self.buffer, -self.length/10, self.buffer]) # Change the x,y axis limits
        ax.set_xlim(x0[0]-self.buffer, x0[0]+self.buffer) # Change the x,y axis limits
        ax.axis('equal')
        span = 1000
        # ax.plot([-span, span], [0, 0], 'k')    # Draw a ground line
        self._drawCart(x0)
        self._drawPendulum(x0)

    def update(self, x):
        z,theta = x[:2]
        c0 = np.cos(theta)
        s0 = np.sin(theta)
        bottom = self.gap + self.cart_height
        pts = np.array([[z, z + self.length*s0, z - self.cart_width/2],
                        [bottom, bottom + self.length*c0, self.gap]])
        # bottom_left_corner = (x, y)
        # self.block.set(xy=bottom_left_corner, angle=np.rad2deg(theta))
        self.cart.set(xy=pts[:,-1])
        self.pendulum.set_xdata(pts[0,:2])
        self.pendulum.set_ydata(pts[1,:2])
        self.bob.set_data(pts[0,1], pts[1,1])
        ax: plt.Axes = self.ax
        ax.set_xlim(z-self.buffer, z+self.buffer)

    def _drawCart(self, x0):
        z, theta = x0[:2]
        x = z - self.cart_width / 2
        y = self.gap
        bottom_left_corner = (x, y)

        self.cart = mpatches.Rectangle(
            xy=bottom_left_corner, width=self.cart_width, height=self.cart_height,
            rotation_point='xy', fc='blue', ec='black'
            )
        self.ax.add_patch(self.cart)
        self.bob, = self.ax.plot(x, y, 'o', c='black')
        return

    def _drawPendulum(self, x0):
        z, theta = x0[:2]
        bottom = self.gap + self.cart_height
        x = [z, z + self.length*np.sin(theta)]
        y = [bottom, bottom + self.length*np.cos(theta)]
        ax: plt.Axes = self.ax
        self.pendulum, = ax.plot(x, y, lw=1, c='black')


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
