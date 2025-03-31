import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from ..animation import SystemAnimator


class BlockBeamAnimator(SystemAnimator):
    def __init__(self, ax: plt.Axes, x, color='b'):
        self.ax = ax
        self.z_hist = x[0]
        self.theta_hist = x[1]
        self.color = color

        self.length = 0.5
        self.block_width = self.length / 10
        buffer = self.length / 5

        ax.axis([-buffer, self.length+buffer, -self.length, self.length])
        baseline, = ax.plot([0.0, self.length], [0.0, 0.0], 'y--')

        z0 = self.z_hist[0]
        theta0 = self.theta_hist[0]
        self._drawBlock(z0, theta0)
        self._drawBeam(theta0)

        ax.axis('equal')

    def update(self, i):
        z = self.z_hist[i]
        theta = self.theta_hist[i]
        c0 = np.cos(theta)
        s0 = np.sin(theta)
        pts = np.array([[0, self.length*c0, (z - self.block_width / 2) * c0],
                        [0, self.length*s0, (z - self.block_width / 2) * s0]])
        self.block.set(xy=pts[:,-1], angle=np.rad2deg(theta))
        self.beam.set_xdata(pts[0,:2])
        self.beam.set_ydata(pts[1,:2])
        return self.block, self.beam

    def _drawBlock(self, z, theta):
        x = (z - self.block_width / 2) * np.cos(theta)
        y = (z - self.block_width / 2) * np.sin(theta)
        bottom_left_corner = (x, y)

        self.block = mpatches.Rectangle(
            xy=bottom_left_corner, width=self.block_width, height=self.block_width,
            angle=np.rad2deg(theta), rotation_point='xy',
            fc=self.color, ec=self.color
            )
        self.ax.add_patch(self.block)
        return

    def _drawBeam(self, theta):
        x = [0, self.length*np.cos(theta)]
        y = [0, self.length*np.sin(theta)]
        ax: plt.Axes = self.ax
        self.beam, = ax.plot(x, y, lw=2, c=self.color)
