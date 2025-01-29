import numpy as np
from ..trajectory1d import Mode, Trajectory1D


class EulerStateTrajectory:
    def __init__(self, horizon, dt):
        self.n_traj = Trajectory1D()
        self.e_traj = Trajectory1D()
        self.d_traj = Trajectory1D()
        self.y_traj = Trajectory1D()
        self.x_traj = np.zeros([9,horizon])
        self.T = horizon
        self.dt = dt
        # self.horizon = np.arange(horizon)*dt

    def eval(self, t: float):
        '''
        Evaluate the trajectory over the prediction horizon starting at time t.

        Args:
        t: current time

        Returns x_traj: (T, n)
        '''
        time = np.linspace(t+self.dt, t+self.T*self.dt, self.T)
        self.x_traj[0] = self.n_traj.eval(time, 0)
        self.x_traj[1] = self.e_traj.eval(time, 0)
        self.x_traj[2] = self.d_traj.eval(time, 0)

        self.x_traj[5] = self.y_traj.eval(time, 0)

        self.x_traj[6] = self.n_traj.eval(time, 1)
        self.x_traj[7] = self.e_traj.eval(time, 1)
        self.x_traj[8] = self.d_traj.eval(time, 1)
        return self.x_traj.T

    def setNorthMode(self, mode: Mode, params: list):
        self.n_traj.setMode(mode, params)

    def setEastMode(self, mode: Mode, params: list):
        self.e_traj.setMode(mode, params)

    def setDownMode(self, mode: Mode, params: list):
        self.d_traj.setMode(mode, params)

    def setYawMode(self, mode: Mode, params: list):
        self.y_traj.setMode(mode, params)
