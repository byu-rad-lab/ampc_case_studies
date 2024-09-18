import numpy as np
from ..tabbed_plot_window import TabbedPlotWindow, FigureSpacing
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, legend: bool=True, deg: bool=True,
                 fontsize: int=12, fig_size: tuple[int,int]=(800,600)):
        # self.time = time
        self.legend = legend
        self.deg = deg
        self.fontsize = fontsize + 0.5
        self.window = TabbedPlotWindow('Multirotor Simulation Data', fig_size)

        self.u_ax: list[plt.Axes] = []

        self.has_cost_data = False
        self.has_state_data = False
        self.has_input_data = False
        self.has_solvetime_data = False
        self.has_mincosts_data = False
        self.has_cvk_data = False

    def _setupCostPlot(self):
        self.cost_fig, self.cost_ax = plt.subplots(1)
        self.cost_ax.set_xlabel('c', fontsize=self.fontsize)
        self.cost_ax.set_ylabel(r'$\int$cost', fontsize=self.fontsize)
        self.window.addTab('Cost', self.cost_fig)
        self.has_cost_data = True

    def _setupStatePlot(self):
        self.pos_fig, self.pos_ax = plt.subplots(3, sharex=True)
        ax: list[plt.Axes] = self.pos_ax
        ax[0].set_ylabel(r'$p_n$ (m)', fontsize=self.fontsize)
        ax[1].set_ylabel(r'$p_e$ (m)', fontsize=self.fontsize)
        ax[2].set_ylabel(r'$p_d$ (m)', fontsize=self.fontsize)
        ax[2].set_xlabel('time (s)', fontsize=self.fontsize)
        self.window.addTab('Position', self.pos_fig)

        self.att_fig, self.att_ax = plt.subplots(3, sharex=True)
        ax: list[plt.Axes] = self.att_ax
        if self.deg:
            ax[0].set_ylabel(r'$\phi$ (deg)', fontsize=self.fontsize)
            ax[1].set_ylabel(r'$\theta$ (deg)', fontsize=self.fontsize)
            ax[2].set_ylabel(r'$\psi$ (deg)', fontsize=self.fontsize)
        else:
            ax[0].set_ylabel(r'$\phi$ (rad)', fontsize=self.fontsize)
            ax[1].set_ylabel(r'$\theta$ (rad)', fontsize=self.fontsize)
            ax[2].set_ylabel(r'$\psi$ (rad)', fontsize=self.fontsize)
        ax[2].set_xlabel('time (s)', fontsize=self.fontsize)
        self.window.addTab('Attitude', self.att_fig)

        self.vel_fig, vel_ax = plt.subplots(3, sharex=True)
        self.vel_ax: list[plt.Axes] = vel_ax
        ax: list[plt.Axes] = self.vel_ax
        ax[0].set_ylabel(r'$v_x$ (m/s)', fontsize=self.fontsize)
        ax[1].set_ylabel(r'$v_y$ (m/s)', fontsize=self.fontsize)
        ax[2].set_ylabel(r'$v_z$ (m/s)', fontsize=self.fontsize)
        ax[2].set_xlabel('time (s)', fontsize=self.fontsize)
        self.window.addTab('Velocity', self.vel_fig)
        self.has_state_data = True

    def _setupInputPlot(self):
        self.u_fig, u_ax = plt.subplots(4)
        self.u_ax: list[plt.Axes] = u_ax
        ax: list[plt.Axes] = self.u_ax
        ax[0].set_ylabel('s', fontsize=self.fontsize)
        ax[1].set_ylabel(r'$\omega_x$', fontsize=self.fontsize)
        ax[2].set_ylabel(r'$\omega_y$', fontsize=self.fontsize)
        ax[3].set_ylabel(r'$\omega_z$', fontsize=self.fontsize)
        ax[3].set_xlabel('time (s)', fontsize=self.fontsize)
        self.window.addTab('Inputs', self.u_fig)
        self.has_input_data = True

    def _setupSolveTimePlot(self):
        self.st_fig, self.st_ax = plt.subplots(1)
        ax: plt.Axes = self.st_ax
        ax.set_ylabel('solve time (s)', fontsize=self.fontsize)
        ax.set_xlabel('simulation time (s)', fontsize=self.fontsize)
        self.window.addTab('Solve Times', self.st_fig)
        self.has_solvetime_data = True

    def _setupMinCostsPlot(self):
        self.mincost_fig, self.mincost_ax = plt.subplots(2)
        ax: plt.Axes = self.mincost_ax[0]
        ax.set_ylabel(r'$\int$cost', fontsize=self.fontsize)
        ax: plt.Axes = self.mincost_ax[1]
        ax.set_xlabel('k', fontsize=self.fontsize)
        ax.set_ylabel('c', fontsize=self.fontsize)
        self.window.addTab('min costs', self.mincost_fig)
        self.has_mincosts_data = True

    def _setupCvKPlot(self):
        self.cvk_fig, self.cvk_ax = plt.subplots(2)
        ax: plt.Axes = self.cvk_ax[0]
        ax.set_xlabel('k', fontsize=self.fontsize)
        ax.set_ylabel(r'$\int$cost', fontsize=self.fontsize)
        ax: plt.Axes = self.cvk_ax[1]
        ax.set_xlabel('c', fontsize=self.fontsize)
        ax.set_ylabel(r'$\int$cost', fontsize=self.fontsize)
        self.window.addTab('c vs k', self.cvk_fig)
        self.has_cvk_data = True

    def plotStateLine(self, time: np.ndarray, x_hist: np.ndarray, *args, **kwargs):
        if not self.has_state_data:
            self._setupStatePlot()

        x_ax: list[plt.Axes] = [*self.pos_ax, *self.att_ax, *self.vel_ax]
        for i,ax in enumerate(x_ax):
            if i in [3,4,5]:
                data = np.rad2deg(x_hist[:,i])
            else:
                data = x_hist[:,i]
            ax.plot(time, data, *args, **kwargs)

    def plotInputLine(self, time: np.ndarray, u_hist: np.ndarray, *args, **kwargs):
        if not self.has_input_data:
            self._setupInputPlot()
        u_ax: list[plt.Axes] = self.u_ax
        for i, ax in enumerate(u_ax):
            ax.plot(time[:-1], u_hist[:,i], drawstyle='steps-post', *args, **kwargs)

    def plotCosts(self, c_arr: list, cost_arr: list, *args, **kwargs):
        if not self.has_cost_data:
            self._setupCostPlot()
        ax: plt.Axes = self.cost_ax
        ax.plot(c_arr, cost_arr, *args, **kwargs)

    def plotSolveTimes(self, time: np.ndarray, st_hist: np.ndarray, *args, **kwargs):
        if not self.has_solvetime_data:
            self._setupSolveTimePlot()
        ax: plt.Axes = self.st_ax
        ax.plot(time[:-1], st_hist, *args, **kwargs)

    def plotMinCosts(self, k_list: np.ndarray, min_costs: np.ndarray,
                     min_c_list: np.ndarray, *args, **kwargs):
        if not self.has_mincosts_data:
            self._setupMinCostsPlot()
        ax: plt.Axes = self.mincost_ax[0]
        ax.plot(k_list, min_costs, *args, **kwargs)
        ax: plt.Axes = self.mincost_ax[1]
        ax.plot(k_list, min_c_list, '.', *args, **kwargs)

    def plotCvK(self, c_list: np.ndarray, k_list: np.ndarray, costs: np.ndarray):
        if not self.has_cvk_data:
            self._setupCvKPlot()
        ax: plt.Axes = self.cvk_ax[0]
        for i,c in enumerate(c_list):
            ax.plot(k_list, costs.T[i], label=f'c = {c:.1f}')
        ax: plt.Axes = self.cvk_ax[1]
        for i,k in enumerate(k_list):
            ax.plot(c_list, costs[i], label=f'k = {k:.0f}')

    def show(self):
        leg_fontsize = self.fontsize - 4
            # self.vel_ax.legend()
        # self.window.pause(0.0)
        if self.has_cost_data:
            if self.legend and len(self.cost_ax.get_lines()) > 1:
                self.cost_ax.legend(fontsize=leg_fontsize)
            self.cost_fig.tight_layout()
        if self.has_state_data:
            if self.legend and len(self.pos_ax[0].get_lines()) > 4:
                self.pos_ax[0].legend(loc=2, bbox_to_anchor=(1,1), fontsize=leg_fontsize)
                self.att_ax[0].legend(loc=2, bbox_to_anchor=(1,1), fontsize=leg_fontsize)
                self.vel_ax[0].legend(loc=2, bbox_to_anchor=(1,1), fontsize=leg_fontsize)
                self.pos_fig.subplots_adjust(left=0.11, right=0.8, bottom=0.09)
                self.att_fig.subplots_adjust(left=0.11, right=0.8, bottom=0.09)
                self.vel_fig.subplots_adjust(left=0.11, right=0.8, bottom=0.09)
            elif self.legend and len(self.pos_ax[0].get_lines()) > 1:
                self.pos_ax[0].legend(fontsize=leg_fontsize)
                self.att_ax[0].legend(fontsize=leg_fontsize)
                self.vel_ax[0].legend(fontsize=leg_fontsize)
                self.pos_fig.tight_layout()
                self.att_fig.tight_layout()
                self.vel_fig.tight_layout()
        if self.has_input_data:
            if self.legend and len(self.u_ax[0].get_lines()) > 4:
                self.u_ax[0].legend(loc=2, bbox_to_anchor=(1,1), fontsize=leg_fontsize)
                self.u_fig.subplots_adjust(left=0.1, right=0.8, bottom=0.09, hspace=0.45)
            elif self.legend and len(self.u_ax[0].get_lines()) > 1:
                self.u_ax[0].legend(fontsize=leg_fontsize)
                self.u_fig.tight_layout()
        if self.has_solvetime_data:
            ax: plt.Axes = self.st_ax
            if self.legend and len(ax.get_lines()) > 4:
                ax.legend(fontsize=leg_fontsize)
                self.st_fig.subplots_adjust(left=0.1, bottom=0.1)
            elif self.legend and len(ax.get_lines()) > 1:
                ax.legend(fontsize=leg_fontsize)
                self.st_fig.tight_layout()
        if self.has_mincosts_data:
            if self.legend:
                ax: list[plt.Axes] = self.mincost_ax
                ax[0].legend(fontsize=leg_fontsize)
                ax[1].legend(fontsize=leg_fontsize)
                ax: list[plt.Axes] = self.cvk_ax
                ax[0].legend(fontsize=leg_fontsize)
                ax[1].legend(fontsize=leg_fontsize)
            self.mincost_fig.tight_layout()
        self.window.show()

    def savePlots(self, path: str, image_type: str='svg'):
        # if self.legend:
        #     self.pos_ax.legend(fontsize=self.fontsize-1)

        if path[-1] != '/':
            path += '/'
        if self.has_cost_data:
            # xlabel = self.cost_ax.get_xlabel()
            # self.cost_ax.set_xlabel(xlabel, fontsize=20)
            # self.cost_fig.tight_layout()
            self.cost_fig.savefig(f'{path}cost.{image_type}')
        if self.has_state_data:
            # xlabel = self.vel_ax.get_xlabel()
            # self.vel_ax.set_xlabel(xlabel, fontsize=12)
            # self.x_fig.tight_layout()
            self.pos_fig.savefig(f'{path}position.{image_type}')
            self.att_fig.savefig(f'{path}attitude.{image_type}')
            self.vel_fig.savefig(f'{path}velocity.{image_type}')
        if self.has_input_data:
            # self.u_fig.subplots_adjust(left=0.1, bottom=0.1)
            # self.u_fig.tight_layout()
            self.u_fig.savefig(f'{path}inputs.{image_type}')
        if self.has_solvetime_data:
            # self.st_fig.subplots_adjust(left=0.07)
            # self.st_fig.tight_layout()
            self.st_fig.savefig(f'{path}solve_times.{image_type}')
        if self.has_mincosts_data:
            self.mincost_fig.savefig(f'{path}mincosts.{image_type}')
        if self.has_cvk_data:
            self.cvk_fig.savefig(f'{path}c_vs_k.{image_type}')
