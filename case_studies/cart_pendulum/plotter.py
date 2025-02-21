import numpy as np
import matplotlib.pyplot as plt

from ..plot_application import PlotApplication, TabbedWindow, FigureSpacing


class PlotWindow:
    def __init__(self, name: str, legend: bool=True, deg: bool=True,
                 fontsize: int=12, fig_size: tuple[int,int]=(800,600)):
        self.legend = legend
        self.deg = deg
        self.legend_fontsize = fontsize - 4
        self.window = TabbedWindow(name, fig_size)
        self.tabs = []

    def _setupCostPlot(self):
        self.cost_fig, self.cost_ax = plt.subplots(1)
        self.cost_ax.set_xlabel('c')
        self.cost_ax.set_ylabel(r'$\int$cost')
        name = 'Costs'
        self.window.addTab(name, self.cost_fig)
        self.tabs.append(name)

    def _setupStatePlot(self):
        self.pos_fig, self.pos_ax = plt.subplots(2, sharex=True)
        ax: list[plt.Axes] = self.pos_ax
        ax[0].set_ylabel(r'$z$ (m)')
        if self.deg:
            ax[1].set_ylabel(r'$\theta$ (deg)')
        else:
            ax[1].set_ylabel(r'$\theta$ (rad)')
        ax[1].set_xlabel('time (s)')
        name = 'Position'
        self.window.addTab(name, self.pos_fig)
        self.tabs.append(name)

        self.vel_fig, vel_ax = plt.subplots(2, sharex=True)
        self.vel_ax: list[plt.Axes] = vel_ax
        ax: list[plt.Axes] = self.vel_ax
        ax[0].set_ylabel(r'$\dot{z}$ (m/s)')
        ax[1].set_ylabel(r'$\dot{\theta}$ (rad/s)')
        ax[1].set_xlabel('time (s)')
        name = 'Velocity'
        self.window.addTab(name, self.vel_fig)
        self.tabs.append(name)

    def _setupInputPlot(self):
        self.u_fig, self.u_ax = plt.subplots(1)
        ax: plt.Axes = self.u_ax
        ax.set_ylabel('F')
        ax.set_xlabel('time (s)')
        name = 'Inputs'
        self.window.addTab(name, self.u_fig)
        self.tabs.append(name)

    def _setupSolveTimePlot(self):
        self.st_fig, self.st_ax = plt.subplots(1)
        ax: plt.Axes = self.st_ax
        ax.set_ylabel('solve time (s)')
        ax.set_xlabel('simulation time (s)')
        name = 'Solve Times'
        self.window.addTab(name, self.st_fig)
        self.tabs.append(name)

    def _setupMinCostsPlot(self):
        self.mincost_fig, self.mincost_ax = plt.subplots(2)
        ax: plt.Axes = self.mincost_ax[0]
        ax.set_ylabel(r'$\int$cost')
        ax: plt.Axes = self.mincost_ax[1]
        ax.set_xlabel('k')
        ax.set_ylabel('c')
        name = 'min costs'
        self.window.addTab(name, self.mincost_fig)
        self.tabs.append(name)

    def _setupCvKPlot(self):
        self.cvk_fig, self.cvk_ax = plt.subplots(2)
        ax: plt.Axes = self.cvk_ax[0]
        ax.set_xlabel('k')
        ax.set_ylabel(r'$\int$cost')
        ax: plt.Axes = self.cvk_ax[1]
        ax.set_xlabel('c')
        ax.set_ylabel(r'$\int$cost')
        name = 'c vs k'
        self.window.addTab(name, self.cvk_fig)
        self.tabs.append(name)

    def plotStateLine(self, time: np.ndarray, x_hist: np.ndarray, *args, **kwargs):
        if not 'Position' in self.tabs:
            self._setupStatePlot()

        x_ax: list[plt.Axes] = [*self.pos_ax, *self.vel_ax]
        for i,ax in enumerate(x_ax):
            if i in [1] and self.deg:
                data = np.rad2deg(x_hist[:,i])
            else:
                data = x_hist[:,i]
            ax.plot(time, data, *args, **kwargs)

    def plotInputLine(self, time: np.ndarray, u_hist: np.ndarray, *args, **kwargs):
        if not 'Inputs' in self.tabs:
            self._setupInputPlot()
        ax: plt.Axes = self.u_ax
        ax.plot(time[:-1], u_hist, drawstyle='steps-post', *args, **kwargs)

    def plotCosts(self, c_arr: list, cost_arr: list, *args, **kwargs):
        if not 'Costs' in self.tabs:
            self._setupCostPlot()
        ax: plt.Axes = self.cost_ax
        ax.plot(c_arr, cost_arr, *args, **kwargs)

    def plotSolveTimes(self, time: np.ndarray, st_hist: np.ndarray, *args, **kwargs):
        if not 'Solve Times' in self.tabs:
            self._setupSolveTimePlot()
        ax: plt.Axes = self.st_ax
        ax.plot(time[:-1], st_hist, *args, **kwargs)

    def plotMinCosts(self, k_list: np.ndarray, min_costs: np.ndarray,
                     min_c_list: np.ndarray, *args, **kwargs):
        if not 'min costs' in self.tabs:
            self._setupMinCostsPlot()
        ax: plt.Axes = self.mincost_ax[0]
        ax.plot(k_list, min_costs, *args, **kwargs)
        ax: plt.Axes = self.mincost_ax[1]
        ax.plot(k_list, min_c_list, '.', *args, **kwargs)

    def plotCvK(self, c_list: np.ndarray, k_list: np.ndarray, costs: np.ndarray):
        if not 'c vs k' in self.tabs:
            self._setupCvKPlot()
        ax: plt.Axes = self.cvk_ax[0]
        for i,c in enumerate(c_list):
            ax.plot(k_list, costs.T[i], label=f'c = {c:.1f}')
        ax: plt.Axes = self.cvk_ax[1]
        for i,k in enumerate(k_list):
            ax.plot(c_list, costs[i], label=f'k = {k:.0f}')

    def show(self):
        self.window.show()
        leg_fontsize = self.legend_fontsize
        if 'Costs' in self.tabs:
            self.window.tabs.setCurrentIndex(self.tabs.index('Costs'))
            if self.legend and len(self.cost_ax.get_lines()) > 1:
                self.cost_ax.legend(fontsize=leg_fontsize)
            self.cost_fig.tight_layout()
        if 'Position' in self.tabs:
            if self.legend and 6 > len(self.pos_ax[0].get_lines()) > 1:
                self.pos_ax[0].legend(fontsize=leg_fontsize)
                self.vel_ax[0].legend(fontsize=leg_fontsize)
            self.window.tabs.setCurrentIndex(self.tabs.index('Position'))
            self.pos_fig.tight_layout()
            self.window.tabs.setCurrentIndex(self.tabs.index('Velocity'))
            self.vel_fig.tight_layout()
        if 'Inputs' in self.tabs:
            self.window.tabs.setCurrentIndex(self.tabs.index('Inputs'))
            if self.legend and 5 > len(self.u_ax.get_lines()) > 1:
                self.u_ax.legend(fontsize=leg_fontsize)
            self.u_fig.tight_layout()
        if 'Solve Times' in self.tabs:
            self.window.tabs.setCurrentIndex(self.tabs.index('Solve Times'))
            ax: plt.Axes = self.st_ax
            if self.legend and 5 > len(ax.get_lines()) > 1:
                ax.legend(fontsize=leg_fontsize)
            self.st_fig.tight_layout()
        if 'min costs' in self.tabs:
            self.window.tabs.setCurrentIndex(self.tabs.index('min costs'))
            if self.legend:
                ax: list[plt.Axes] = self.mincost_ax
                ax[0].legend(fontsize=leg_fontsize)
                ax[1].legend(fontsize=leg_fontsize)
                if 6 > len(self.cvk_ax[0].get_lines()) > 1:
                    ax: list[plt.Axes] = self.cvk_ax
                    ax[0].legend(fontsize=leg_fontsize)
                    ax[1].legend(fontsize=leg_fontsize)
            self.mincost_fig.tight_layout()
        if 'c vs k' in self.tabs:
            self.window.tabs.setCurrentIndex(self.tabs.index('c vs k'))
            self.cvk_fig.tight_layout()
        self.window.tabs.setCurrentIndex(0)

    def savePlots(self, path: str, end: str='', image_type: str='svg'):
        if path[-1] != '/':
            path += '/'
        if 'Costs' in self.tabs:
            self.cost_fig.savefig(f'{path}cost.{image_type}')
        if 'Position' in self.tabs:
            self.pos_fig.savefig(f'{path}position{end}.{image_type}')
            self.vel_fig.savefig(f'{path}velocity{end}.{image_type}')
        if 'Inputs' in self.tabs:
            self.u_fig.savefig(f'{path}inputs{end}.{image_type}')
        if 'Solve Times' in self.tabs:
            self.st_fig.savefig(f'{path}solve_times{end}.{image_type}')
        if 'min costs' in self.tabs:
            self.mincost_fig.savefig(f'{path}mincosts.{image_type}')
        if 'c vs k' in self.tabs:
            self.cvk_fig.savefig(f'{path}c_vs_k.{image_type}')


class Plotter:

    def __init__(self, legend: bool=True, deg: bool=True,
                 fontsize: int=12, fig_size: tuple[int,int]=(800,600)):
        self.legend = legend
        self.deg = deg
        self.fontsize = fontsize
        self.fig_size = fig_size
        self.plot_app = PlotApplication(fontsize)
        self.windows: list[PlotWindow] = []

    def addWindow(self, window: PlotWindow):
        self.windows.append(window)
        self.plot_app.addWindow(window.window)
        window.show()

    def createPlotWindow(self, name: str='Robot Arm Simulation Data') -> PlotWindow:
        window = PlotWindow(name, self.legend, self.deg, self.fontsize, self.fig_size)
        self.windows.append(window)
        self.plot_app.addWindow(window.window)
        # window.show()
        return window

    def show(self):
        for window in self.windows:
            window.show()
        self.plot_app.show()

    def pause(self, n_sec: int):
        for window in self.windows:
            window.show()
        self.plot_app.pause(n_sec)
