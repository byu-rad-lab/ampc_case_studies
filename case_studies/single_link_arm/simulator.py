import numpy as np
from time import time as now
from typing import Callable
import affine_mpc_py as ampc

from . import dynamics as arm
from .. import trajectory as traj


class Simulator:
    n,m = 2,1
    sys = arm.SingleLinkArm(mass=0.5, length=0.3, damping=0.1)
    p = 5

    def __init__(self, tf: float, dt: float, T: int, x0: np.ndarray,
                 Q: np.ndarray, xref_gen: Callable):
        self.tf = tf
        self.dt = dt
        self.T = T
        self.x0 = x0.copy()
        self.time = np.arange(0.0, tf+self.dt, self.dt)
        self.Q = Q.copy()
        self.getRefTrajectory = xref_gen

    def _setupMPC(self):
        self.mpc = ampc.ImplicitMPC(self.n, self.m, self.T, self.p)
        xp = np.array([np.radians(30), 0.0])
        up = np.array([0.0]) + self.sys.getEquilibriumTorque(xp[0])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt)
        u_max = np.array([1.0])
        self.mpc.setInputLimits(-u_max, u_max)
        self.mpc.setStateWeights(self.Q)
        xr = np.array([np.radians(90), 0.0])
        self.mpc.setReferenceState(xr)
        self.mpc.initializeSolver()

    def updateControlModel(self, x: np.ndarray, xr_traj: np.ndarray, c: int,
                           k: int, u_prev: np.ndarray, method: str):
        xr = xr_traj[2*k:2*(k+1)]
        if method in ['lin', 'xeq']:
            mask = np.array([1, 0])
        else:
            mask = np.ones_like(x)
        xp = (1-c)*x*mask + c*xr*mask
        if method in ['uk', 'xeq']:
            up = u_prev
        else:
            up = np.zeros(self.m) + self.sys.getEquilibriumTorque(xp[0])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt, 1e-8)

    def run(self, c: int, k: int, method: str='lin'):
        x = self.x0.copy()
        x_hist = [x.copy()]
        xr_hist = [self.getRefTrajectory(0)[:2].copy()]
        u_hist = []
        solve_times = []
        cost_integral = 0.0
        u_star = np.array([self.sys.getEquilibriumTorque(x[0])])
        self._setupMPC()

        for t in self.time[:-1]:
            start = now()
            xr_traj = self.getRefTrajectory(t)
            self.mpc.setReferenceStateTrajectory(xr_traj)
            self.updateControlModel(x, xr_traj, c, k, u_star, method)
            solved = self.mpc.solve(x)
            if solved:
                u_star = self.mpc.getNextInput()
            else:
                print(':(')
            solve_times.append(now() - start)
            u_hist.append(u_star.copy())

            x = self.sys.integrateRK4(x, u_star, self.dt)
            x_hist.append(x.copy())
            xr = xr_traj[:2]
            xr_hist.append(xr.copy())

            error = xr - x
            cost_integral += self.Q @ error**2

        x_hist = np.array(x_hist)
        xr_hist = np.array(xr_hist)
        u_hist = np.array(u_hist)
        return cost_integral, x_hist, xr_hist, u_hist, solve_times


def getSimulator(args):
    tf = 10.0
    dt = 0.01
    x0 = np.array([np.radians(0), 0.0])
    T = 100
    Q = np.array(args.weights) if args.weights is not None else np.ones(2)
    assert len(Q) == 2
    print(f'{Q = }')
    ref_types = ['step', 'cos', 'ramp']

    reference_type = args.ref_type
    print(f'{reference_type = }: ', end='')
    if reference_type == 'step':
        # Q = np.array([1.0, 1.0])
        default_params = [30.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = np.radians(params[0])
        xr = np.array([amplitude, 0.0])
        traj_fn = traj.Step(xr, T)
        print(f'amplitude = radians({params[0]})')
    elif reference_type == 'cos':
        # Q = np.array([1.0, 1.0])
        # Q = np.array([1.0, 0.1])
        # Q = np.array([1.0, 0.01])
        default_params = [60., 2.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = np.radians(params[0])
        period = tf / params[1]
        frequency_hz = 1 / period
        offset = x0[0]
        traj_fn = traj.Sinusoidal(amplitude, frequency_hz, offset, T, dt, reference_type)
        print(f'amplitude = radians({params[0]:.1f}), period = tf/{params[1]:.1f}')
    elif reference_type == 'ramp':
        # Q = np.array([1.0, 1.0])
        # Q = np.array([1.0, 0.1])
        # Q = np.array([1.0, 0.01])
        default_params = [10.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        s = params[0]
        vel = 2*np.pi / s
        traj_fn = traj.Ramp(velocity=vel, offset=x0[0], horizon=T, dt=dt)
        print(f'ref = ramp: vel = 2pi/{s[0]:.1f}')
    else:
        raise ValueError(f'Unrecognized reference type {args.ref_type} - must be in {ref_types}')

    return Simulator(tf, dt, T, x0, Q, traj_fn)


def main():
    pass


if __name__ == '__main__':
    main()
