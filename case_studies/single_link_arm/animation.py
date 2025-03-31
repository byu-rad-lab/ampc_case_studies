import numpy as np
import matplotlib.pyplot as plt

from ..animation import SystemAnimator


class ArmAnimator(SystemAnimator):
    def __init__(self, ax: plt.Axes, x, color='b'):
        self.ax = ax
        self.theta_hist = x[0]
        self.length = 0.3

        theta0 = self.theta_hist[0]
        c0 = np.cos(theta0)
        s0 = np.sin(theta0)

        baseline = ax.plot([0,self.length], [0,0], 'k:')
        point = ax.plot([0], [0], '.', color=color, markersize=25)
        self.arm, = ax.plot([0,self.length*c0], [0,self.length*s0], color=color, linewidth=5)
        lims = self.length*np.array([-1.25, 1.25])
        ax.set_aspect('equal')
        ax.set_xlim(lims)
        ax.set_ylim(lims)

    def update(self, i):
        theta = self.theta_hist[i]
        c0 = np.cos(theta)
        s0 = np.sin(theta)
        self.arm.set_xdata([0, self.length*c0])
        self.arm.set_ydata([0, self.length*s0])
        return self.arm,
