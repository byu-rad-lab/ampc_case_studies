import numpy as np
from ..trajectory1d import Mode, Trajectory1D


class CartPendulumTrajectory:
    def __init__(self, horizon, dt):
        self.z_traj = Trajectory1D()
        self.theta_traj = Trajectory1D()
        self.x_traj = np.zeros([4,horizon])
        self.T = horizon
        self.dt = dt

    def eval(self, t: float) -> np.ndarray:
        '''
        Evaluate the trajectory over the prediction horizon starting at time t.

        :param float t: current time, or start time of the prediction horizon
        :return x_traj (T x n): NDArray of size (T, n)
        '''
        time = np.linspace(t+self.dt, t+self.T*self.dt, self.T)
        self.x_traj[0] = self.z_traj.eval(time, 0)
        self.x_traj[1] = self.theta_traj.eval(time, 0)
        self.x_traj[2] = self.z_traj.eval(time, 1)
        self.x_traj[3] = self.theta_traj.eval(time, 1)
        return self.x_traj.T

    def setZMode(self, mode: Mode, params: list):
        self.z_traj.setMode(mode, params)

    def setThetaMode(self, mode: Mode, params: list):
        self.theta_traj.setMode(mode, params)
