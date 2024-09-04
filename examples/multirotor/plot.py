import numpy as np
from ..tabbed_plot_window import TabbedPlotWindow, FigureSpacing
import matplotlib.pyplot as plt


class Plotter:
    def __init__(self, time: np.ndarray, legend: bool=True, deg: bool=True,
                 fontsize: int=12, fig_size: tuple[int,int]=(800,600)):
        self.time = time
        self.legend = legend
        self.deg = deg
        self.fontsize = fontsize + 0.5
        self.window = TabbedPlotWindow('Robot Arm Simulation Data', fig_size)

        self.cost_data = False
        self.state_data = False
        self.input_data = False
        self.solve_time_data = False

    def _setupCostPlot(self):
        self.cost_fig, self.cost_ax = plt.subplots(1)
        self.cost_ax.set_xlabel('c', fontsize=self.fontsize)
        self.cost_ax.set_ylabel(r'$\int$cost', fontsize=self.fontsize)
        self.window.addTab('Cost', self.cost_fig)

    def _setupStatePlot(self):
        self.x_fig, self.x_ax = plt.subplots(2, sharex=True)
        self.pos_ax: plt.Axes = self.x_ax[0]
        self.vel_ax: plt.Axes = self.x_ax[1]
        if self.deg:
            self.pos_ax.set_ylabel(r'$\theta$ (deg)', fontsize=self.fontsize)
        else:
            self.pos_ax.set_ylabel(r'$\theta$ (rad)', fontsize=self.fontsize)
        self.vel_ax.set_ylabel(r'$\dot{\theta}$ (rad/s)', fontsize=self.fontsize)
        self.vel_ax.set_xlabel('time (s)', fontsize=self.fontsize)
        self.x_fig.tight_layout()
        self.window.addTab('States', self.x_fig)

    def _setupInputPlot(self):
        self.u_fig, self.u_ax = plt.subplots(1)
        self.u_ax.set_ylabel('torque', fontsize=self.fontsize)
        self.u_ax.set_xlabel('time (s)', fontsize=self.fontsize)
        self.window.addTab('Inputs', self.u_fig)

    def _setupSolveTimePlot(self):
        self.st_fig, self.st_ax = plt.subplots(1)
        self.st_ax.set_ylabel('solve time (s)', fontsize=self.fontsize)
        self.st_ax.set_xlabel('simulation time (s)', fontsize=self.fontsize)
        self.window.addTab('Solve Times', self.st_fig)

    def plotStateLine(self, x_hist: np.ndarray, *args, **kwargs):
        if not self.state_data:
            self._setupStatePlot()
            self.state_data = True
        if self.deg:
            self.pos_ax.plot(self.time, np.rad2deg(x_hist[:, 0]), *args, **kwargs)
        else:
            self.pos_ax.plot(self.time, x_hist[:, 0], *args, **kwargs)
        self.vel_ax.plot(self.time, x_hist[:, 1], *args, **kwargs)

    def plotInputLine(self, u_hist: np.ndarray, *args, **kwargs):
        if not self.input_data:
            self._setupInputPlot()
            self.input_data = True
        self.u_ax.plot(self.time[:-1], u_hist, drawstyle='steps-post', *args, **kwargs)
        self.u_fig.tight_layout()

    def plotCosts(self, c_arr: list, cost_arr: list, *args, **kwargs):
        if not self.cost_data:
            self._setupCostPlot()
            self.cost_data = True
        self.cost_ax.plot(c_arr, cost_arr, *args, **kwargs)

    def plotSolveTimes(self, st_hist: np.ndarray, *args, **kwargs):
        if not self.solve_time_data:
            self._setupSolveTimePlot()
            self.solve_time_data = True
        self.st_ax.plot(self.time[:-1], st_hist, *args, **kwargs)

    def show(self):
        if self.legend:
            self.pos_ax.legend()
            # self.vel_ax.legend()
        # self.window.MainWindow.resize(800, 600)
        self.window.pause(0.0)
        if self.cost_data:
            self.cost_fig.tight_layout()
        if self.state_data:
            self.x_fig.tight_layout()
        if self.input_data:
            # xlabel = self.u_ax.get_xlabel()
            # self.u_ax.set_xlabel(xlabel, fontsize=18)
            self.u_fig.tight_layout()
        if self.solve_time_data:
            self.st_fig.tight_layout()
        self.window.show()

    def savePlots(self, path: str, image_type: str='pdf'):
        # if self.legend:
        #     self.pos_ax.legend(fontsize=self.fontsize-1)

        if path[-1] != '/':
            path += '/'
        if self.cost_data:
            # xlabel = self.cost_ax.get_xlabel()
            # self.cost_ax.set_xlabel(xlabel, fontsize=20)
            # self.cost_fig.tight_layout()
            self.cost_fig.savefig(f'{path}cost.{image_type}')
        if self.state_data:
            # xlabel = self.vel_ax.get_xlabel()
            # self.vel_ax.set_xlabel(xlabel, fontsize=12)
            # self.x_fig.tight_layout()
            self.x_fig.savefig(f'{path}states.{image_type}')
        if self.input_data:
            # self.u_fig.subplots_adjust(left=0.1, bottom=0.1)
            # self.u_fig.tight_layout()
            self.u_fig.savefig(f'{path}inputs.{image_type}')
        if self.solve_time_data:
            # self.st_fig.subplots_adjust(left=0.07)
            # self.st_fig.tight_layout()
            self.st_fig.savefig(f'{path}solve_times.{image_type}')
