import numpy as np
from numpy.typing import NDArray
from typing import Type
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.animation as animation
import os
from tqdm import tqdm


class DataAnimator:
    live_ref = False

    def __init__(self, ax: plt.Axes, t: NDArray, x: NDArray, xr: NDArray,
                 x_color: str, xr_color: str, deg: bool=False, legend: bool=False):
        self.ax = ax
        self.t = t
        self.x = x if not deg else np.degrees(x)
        self.xr = xr if not deg else np.degrees(xr)
        self.x_line, = ax.plot(t[0], x[0], x_color, label='x')
        if self.live_ref:
            self.xr_line, = ax.plot(self.t[0], self.xr[0], '--', color=xr_color, label='ref')
        else:
            self.xr_line, = ax.plot(self.t, self.xr, '--', color=xr_color, label='ref')
            scale = (t[-1] - t[0]) / 20
            ax.set_xlim([t[0]-scale, t[-1]+scale])
        if legend:
            ax.legend()

    def update(self, i):
        self.x_line.set_data(self.t[:i+1], self.x[:i+1])
        if self.live_ref:
            self.xr_line.set_data(self.t[:i+1], self.xr[:i+1])
            self.ax.relim()
            self.ax.autoscale_view(scalex=True, scaley=True)
            return self.x_line, self.xr_line

        self.ax.relim()
        self.ax.autoscale_view(scaley=True)
        return self.x_line,

    def plot(self):
        self.x_line.set_data(self.t, self.x)
        self.xr_line.set_data(self.t, self.xr)
        plt.show(block=False)


class SystemAnimator:
    def __init__(self, ax: plt.Axes, x, color):
        raise NotImplementedError("This method should be implemented in derived classes.")

    def update(self, i):
        raise NotImplementedError("This method should be implemented in derived classes.")


class CombinedAnimator:
    """
    This class combines the SystemAnimator and DataAnimator classes to create a
    combined animation: system animation on the sys_ax and data animations on the
    data_axes.
    """

    def __init__(self, Animator: Type[SystemAnimator], sys_ax: plt.Axes,
                 data_axes: list[plt.Axes], t_hist, x_hist, xr_hist, data_idxs,
                 x_labels, color='tab:pink', label='Best Aff'):
        self.t_hist = t_hist
        self.x_hist = x_hist
        self.xr_hist = xr_hist
        xr_color = 'tab:red'

        self.animator = Animator(sys_ax, x_hist, color=color)

        self.x_data: list[DataAnimator] = []
        data_axes[0].set_title(f'Time Tracking: {label}')

        for i in range(len(x_hist[data_idxs])):
            ax: plt.Axes = data_axes[i]
            deg = 'deg' in x_labels[i]
            legend = i == 0
            data = DataAnimator(ax, t_hist, x_hist[data_idxs[i]], xr_hist[data_idxs[i]],
                                color, xr_color, deg, legend)
            self.x_data.append(data)
            ax.set_ylabel(x_labels[i])

        ax.set_xlabel('time (s)')

    def update(self, i):
        objects = self.animator.update(i)
        for d in self.x_data:
            objects += d.update(i)
        return objects


class StackedAnimation:
    """
    This class stacks two CombinedAnimator objects on top of each other. A figure
    is created with system animations on the left and data animations on the right.
    """

    def __init__(self, Animator: Type[SystemAnimator], fig: plt.Figure,
                 ani_axes: list[plt.Axes], data_axes: list[plt.Axes],
                 t_hist, x_hists, data_idxs, x_labels, xr_hist, colors, labels):
        self.num = len(x_hists)
        self.dt = t_hist[1] - t_hist[0]
        self.steps = len(t_hist)

        assert len(colors) == len(labels) == self.num

        x_top = x_hists[0]
        x_bot = x_hists[1]
        assert len(data_idxs) == len(x_labels)

        hline = mlines.Line2D([0,1], [0.5]*2, transform=fig.transFigure, color='black')
        fig.lines.extend([hline])

        self.top_animation = CombinedAnimator(Animator, ani_axes[0], data_axes[0],
                                              t_hist, x_top, xr_hist, data_idxs, x_labels,
                                              colors[0], labels[0])
        fig.text(0.025, 0.75, labels[0], va='center', ha='center', rotation=90,
                 transform=fig.transFigure, fontsize=20)

        self.bot_animation = CombinedAnimator(Animator, ani_axes[1], data_axes[1], t_hist, x_bot,
                                              xr_hist, data_idxs, x_labels, colors[1], labels[1])
        fig.text(0.025, 0.25, labels[1], va='center', ha='center', rotation=90,
                 transform=fig.transFigure, fontsize=20)

        self.fig = fig

    def update(self, i):
        objects = self.top_animation.update(i)
        objects += self.bot_animation.update(i)
        return objects

    def save(self, filename):
        interval = 1000*self.dt
        ani = animation.FuncAnimation(self.fig, self.update, frames=self.steps,
                                      interval=interval, blit=False, repeat=False)
        progress_bar = tqdm(total=self.steps, desc="Saving Animation", leave=False)

        def update_progress(frame, total_frames):
            progress_bar.n = frame + 1
            progress_bar.refresh()

        filename = os.path.expanduser(filename)
        ani.save(filename, writer='ffmpeg', progress_callback=update_progress)


    def animate(self, use_mpl_animation=True):
        dt = 0.0001
        if use_mpl_animation:
            ani = animation.FuncAnimation(self.fig, self.update, frames=self.steps,
                                          interval=dt, blit=False, repeat=False)
        else:
            for i in range(self.steps):
                self.update(i)
                plt.pause(dt)
        plt.show(block=True)
