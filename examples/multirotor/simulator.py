import numpy as np
from time import time as now
from ..multirotor.dynamics import Multirotor
from .. import ampc_py as ampc
from typing import Callable


class Simulator:
    n,m = 9,4
    sys = Multirotor(equilibrium_throttle=0.5, damping=0.1, mode=Multirotor.VelocityMode.INERTIAL)
    p = 5

    def __init__(self, tf: float, dt: float, T: int, Q: np.ndarray, xref_gen: Callable, k_ref: int):
        self.tf = tf
        self.dt = dt
        self.T = T
        self.time = np.arange(0.0, tf+self.dt, self.dt)
        self.Q = Q.copy()
        self.getRefTrajectory = xref_gen
        # self.c = 0.0
        self.k = k_ref
        # self._setupMPC()

    def _setupMPC(self):
        self.mpc = ampc.ImplicitMPC(self.n, self.m, self.T, self.p)
        xp = np.array([0,0,-5, .3,.3,.3, 0.1,0.1,0.1])
        up = np.array([self.sys.s_eq, 0.1,0.1,0.1])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt)
        w_max = np.pi
        u_max = np.array([1.0, *[w_max]*3])
        u_min = np.array([.0, *[-w_max]*3])
        self.mpc.setInputLimits(u_min, u_max)
        self.mpc.setStateWeights(self.Q)
        xr = np.array([1,1,-6, 0,0,np.radians(90), 0,0,0])
        self.mpc.setDesiredState(xr)

        settings = ampc.OSQPSettings()
        settings.warm_start = False
        self.mpc.initSolver(settings)

    def updateControlModel(self, x: np.ndarray, xr_traj: np.ndarray, c: int, u_prev: np.ndarray, linearize: bool):
        # xr = xr_traj[self.n*self.k:self.n*(self.k+1)]
        xr = xr_traj[self.k]
        if linearize:
            mask = np.array([0,0,0,0,0,1,0,0,0])
        else:
            mask = np.ones_like(x)
        xp = (1-c)*x*mask + c*xr*mask
        # up = u_prev
        up = np.array([self.sys.s_eq, 0,0,0])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt)

    def run(self, x0: np.ndarray, c: int, linearize: bool=False):
        x = x0.copy()
        x_hist = [x.copy()]
        xr_hist = [self.getRefTrajectory(0)[0].copy()]
        u_hist = []
        solve_times = []
        cost_integral = 0.0
        u_star = np.array([self.sys.s_eq, 0,0,0])
        self._setupMPC()

        for t in self.time[:-1]:
            start = now()
            xr_traj = self.getRefTrajectory(t)
            self.mpc.setDesiredStateTrajectory(xr_traj.flatten())
            self.updateControlModel(x, xr_traj, c, u_star, linearize)
            u_star, solved = self.mpc.calcNextInput(x)
            solve_times.append(now() - start)
            if not solved: print(':(')
            u_hist.append(u_star.copy())

            x = self.sys.integrateRK4(x, u_star, self.dt)
            x_hist.append(x.copy())
            xr = xr_traj[0]
            xr_hist.append(xr.copy())

            error = xr - x
            cost_integral += np.sqrt(self.Q @ error**2)

        x_hist = np.array(x_hist)
        xr_hist = np.array(xr_hist)
        u_hist = np.array(u_hist)
        return cost_integral, x_hist, xr_hist, u_hist, solve_times


def main():
    pass

if __name__ == '__main__':
    main()
