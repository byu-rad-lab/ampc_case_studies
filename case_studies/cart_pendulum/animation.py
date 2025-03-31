import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from ..animation import SystemAnimator


class CartPendulumAnimator(SystemAnimator):
    def __init__(self, ax: plt.Axes, x, color='b'):
        self.ax = ax
        self.z_hist = x[0]
        self.theta_hist = x[1]
        self.color = color

        self.length = 1.0
        self.cart_width = self.length / 2
        self.cart_height = self.length * 0.15
        self.gap = 0.005
        self.radius = self.length * 0.06
        self.buffer = self.length * 3

        span = 100000
        groundline, = ax.plot([-span, span], [0, 0], 'k')

        z0 = self.z_hist[0]
        theta0 = self.theta_hist[0]
        ax.grid(True)
        ax.set_xlim(z0-self.buffer, z0+self.buffer)
        ax_w,ax_h = ax.bbox.size
        ratio = ax_h / ax_w
        ax.set_ylim(np.array([-self.buffer, self.buffer]) * ratio)

        self._drawCart(z0, color)
        self._drawPendulum(z0, theta0, color)

    def update(self, i):
        z = self.z_hist[i]
        theta = self.theta_hist[i]
        c0 = np.cos(theta)
        s0 = np.sin(theta)
        bottom = self.gap + self.cart_height
        pts = np.array([[z, z + self.length*s0, z - self.cart_width/2],
                        [bottom, bottom + self.length*c0, self.gap]])
        self.cart.set(xy=pts[:,-1])
        self.pendulum.set_xdata(pts[0,:2])
        self.pendulum.set_ydata(pts[1,:2])
        self.bob.set_data(pts[0,1], pts[1,1])
        self._updateLimits(z)
        return self.cart, self.pendulum, self.bob

    def _drawCart(self, z0, color):
        x = z0 - self.cart_width / 2
        y = self.gap
        bottom_left_corner = x, y

        self.cart = mpatches.Rectangle(
            xy=bottom_left_corner, width=self.cart_width, height=self.cart_height,
            rotation_point='xy', fc=color, ec='black'
        )
        self.ax.add_patch(self.cart)

    def _drawPendulum(self, z0, theta0, color):
        bottom = self.gap + self.cart_height
        x = [z0, z0 + self.length*np.sin(theta0)]
        y = [bottom, bottom + self.length*np.cos(theta0)]
        ax: plt.Axes = self.ax
        self.pendulum, = ax.plot(x, y, lw=1, c=color)
        self.bob, = self.ax.plot(x, y, 'o', c=color)

    def _updateLimits(self, z):
        ax: plt.Axes = self.ax
        low,high = ax.get_xlim()
        dist2right = high - z
        dist2left = z - low
        shift = 0.0
        buffer = 1.5
        if dist2right < buffer:
            shift = z + buffer - high
        if dist2left < buffer:
            shift = z - buffer - low
        high += shift
        low += shift
        ax.set_xlim(low, high)
