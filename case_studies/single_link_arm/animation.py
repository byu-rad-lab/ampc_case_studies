import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as mlines
import os
from tqdm import tqdm

from ..animation import SystemAnimator, DataAnimator


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


class ArmAnimation:
    def __init__(self, axes, t_hist, x_hist, xr_hist, color, label='Best Aff'):
        self.t_hist = t_hist
        self.x_hist = x_hist
        self.xr_hist = xr_hist
        xr_color = 'tab:red'

        ax: plt.Axes = axes[0]
        self.arm = ArmAnimator(ax, color=color)
        # ax.set_title(f'Animation: {label}')

        ax: plt.Axes = axes[1]
        self.p_data = DataAnimator(ax, t_hist, np.degrees(x_hist[:,0]),
                                   np.degrees(xr_hist[:,0]), color, xr_color,
                                   legend=True)
        ax.set_title(f'Time Tracking: {label}')
        ax.set_ylabel(r'$\theta$ (deg)')

        ax: plt.Axes = axes[2]
        self.v_data = DataAnimator(ax, t_hist, x_hist[:,1], xr_hist[:,1], color, xr_color)
        ax.set_ylabel(r'$\dot{\theta}$ (rad/s)')
        ax.set_xlabel('time (s)')

    def update(self, i):
        arm = self.arm.update(self.x_hist[i, 0])
        p_data = self.p_data.update(i)
        v_data = self.v_data.update(i)
        return arm + p_data + v_data

class StackedAnimation:
    # def __init__(self, t_hist, x_hist_top, x_hist_bot, xr_hist, color_top, color_bot,
    #              label_top, label_bot):
    def __init__(self, fig: plt.Figure, t_hist, x_hists, xr_hist, colors, labels):
        self.fig = fig
        self.dt = t_hist[1] - t_hist[0]
        self.steps = len(t_hist)

        dim = self.fig.get_size_inches()
        ratio = dim[0] / dim[1]
        if ratio < 1:
            ratio = 1/ratio
        gs = fig.add_gridspec(5, 3, width_ratios=[1,1.5,0.125], height_ratios=[1,1,0.05,1,1])
        # gs = fig.add_gridspec(5, 2, width_ratios=[1,1.5], height_ratios=[1,1,0.05,1,1])

        hline = mlines.Line2D([0,1], [0.5]*2, transform=fig.transFigure, color='black')
        fig.lines.extend([hline])

        ani_ax = fig.add_subplot(gs[:2,0])
        p_ax = fig.add_subplot(gs[0,1])
        v_ax = fig.add_subplot(gs[1,1])
        axes = [ani_ax, p_ax, v_ax]
        # self.ref_ani = ArmAnimation(axes, t_hist, xr_hist, xr_hist, 'tab:red', labels[0])
        self.top_ani = ArmAnimation(axes, t_hist, x_hists[0], xr_hist, colors[0], labels[0])
        fig.text(0.025, 0.75, labels[0], va='center', ha='center', rotation=90,
                 transform=fig.transFigure, fontsize=20)

        ani_ax = fig.add_subplot(gs[3:,0])
        # ani_ax.set_ylabel(labels[1], fontsize=24)
        p_ax = fig.add_subplot(gs[3, 1])
        v_ax = fig.add_subplot(gs[4, 1])
        axes = [ani_ax, p_ax, v_ax]
        self.bot_ani = ArmAnimation(axes, t_hist, x_hists[1], xr_hist, colors[1], labels[1])
        fig.text(0.025, 0.25, labels[1], va='center', ha='center', rotation=90,
                 transform=fig.transFigure, fontsize=20)

    def save(self, filename):
        s2ms = 1000
        ani = animation.FuncAnimation(self.fig, self._update, frames=self.steps,
                                      interval=self.dt*s2ms, blit=True)
        progress_bar = tqdm(total=self.steps, desc="Saving Animation", leave=False)

        def update_progress(frame, total_frames):
            progress_bar.n = frame+1
            progress_bar.refresh()
        ani.save(os.path.expanduser(filename), writer='ffmpeg', progress_callback=update_progress)#, dpi=600)

    def animate(self):
        # for i in range(self.steps):
        #     self._update(i)
        #     # plt.pause(self.dt)
        #     plt.pause(0.0001)
        ani = animation.FuncAnimation(self.fig, self._update, frames=self.steps,
                                      interval=0.0001, blit=False, repeat=False)
        plt.show()

    def _update(self, i):
        # ref = self.ref_ani.update(i)
        top_objects = self.top_ani.update(i)
        bot_objects = self.bot_ani.update(i)
        return top_objects + bot_objects
        return ref + top_objects + bot_objects


if __name__ == '__main__':
    from ..tabbed_plot_window import TabbedPlotWindow
    animation = StackedAnimation()
    pw = TabbedPlotWindow(size=[800,800])
    pw.addTab('animation', animation.fig)
    for theta in np.arange(0, np.radians(180), 0.1):
        animation._update(theta)
        pw.pause(0.1)

    pw.show()
