import numpy as np
from time import time as now
from typing import Callable
import affine_mpc_py as ampc

from . import dynamics
from . import trajectory as traj


class Simulator:
    n,m = 4,1
    sys = dynamics.BlockBeam(block_mass=0.35, beam_mass=2., length=0.5)
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
        xp = np.array([self.sys.len*0.25, np.radians(30), -0.1, 0.1])
        up = np.array([0.1]) + self.sys.getEquilibriumInput(xp[0])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt)
        u_max = np.array([15.0])
        self.mpc.setInputLimits(-u_max, u_max)
        self.mpc.setStateWeights(self.Q)
        xr = np.array([self.sys.len*0.75, np.radians(0), 0, 0])
        self.mpc.setReferenceState(xr)
        self.mpc.initializeSolver()

    def updateControlModel(self, x: np.ndarray, xr_traj: np.ndarray, c: int,
                           k: int, u_prev: np.ndarray, anchor_pt: str):
        xr = xr_traj[k]
        if 'xe' in anchor_pt:
            mask = np.array([1, 0, 0, 0])
        else:
            mask = np.ones_like(x)
        xp = (1-c)*x*mask + c*xr*mask
        if 'ut' in anchor_pt:
            up = u_prev
        else:
            up = np.zeros(self.m) + self.sys.getEquilibriumInput(xp[0])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt, 1e-8)

    def run(self, anchor_pt: str, c: int, k: int):
        x = self.x0.copy()
        x_hist = [x.copy()]
        xr_hist = [self.getRefTrajectory(0)[0].copy()]
        u_hist = []
        solve_times = []
        cost_integral = 0.0
        u_star = np.array([self.sys.getEquilibriumInput(x[0])])
        self._setupMPC()

        for t in self.time[:-1]:
            start = now()
            xr_traj = self.getRefTrajectory(t)
            self.mpc.setReferenceStateTrajectory(xr_traj.flatten())
            self.updateControlModel(x, xr_traj, c, k, u_star, anchor_pt)
            solved = self.mpc.solve(x)
            if solved:
                u_star = self.mpc.getNextInput()
            else:
                print(':(')
            solve_times.append(now() - start)
            u_hist.append(u_star.copy())

            x = self.sys.integrateRK4(x, u_star, self.dt)
            x_hist.append(x.copy())
            xr = xr_traj[0]
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
    x0 = np.array([0.05, np.radians(0), 0, 0])
    T = 100
    Q = np.array(args.weights) if args.weights is not None else np.array([1., .1, .1, .1])
    assert len(Q) == len(x0)
    print(f'{Q = }')
    ref_types = ['step', 'cos', 'ramp']

    traj_fn = traj.BlockBeamTrajectory(T, dt)
    reference_type = args.ref_type
    print(f'{reference_type = }: ', end='')
    if reference_type == 'step':
        # Q = np.array([1.0, 1.0])
        default_params = [0.1]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = params[0]
        traj_fn.setZMode(traj.Mode.STEP, [x0[0] + amplitude])
        print(f'amplitude = {params[0]}')
    elif reference_type == 'cos':
        # Q = np.array([1.0, 1.0])
        # Q = np.array([1.0, 0.1])
        # Q = np.array([1.0, 0.01])
        default_params = [.15, 1.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = -params[0]
        period = tf / params[1]
        offset = x0[0] - amplitude
        phase = np.radians(90)
        traj_fn.setZMode(traj.Mode.SINE, [amplitude, period, phase, offset])
        print(f'amplitude = {params[0]:.1f}, period = tf/{params[1]:.1f}')
    elif reference_type == 'ramp':
        # Q = np.array([1.0, 1.0])
        # Q = np.array([1.0, 0.1])
        # Q = np.array([1.0, 0.01])
        default_params = [.3]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel =  params[0] / tf
        traj_fn.setZMode(traj.Mode.LINE, [vel, x0[0]])
        print(f'ref = ramp: vel = {params[0]:.1f}/tf')
    else:
        raise ValueError(f'Unrecognized reference type {args.ref_type} - must be in {ref_types}')

    return Simulator(tf, dt, T, x0, Q, traj_fn.eval)


def main():
    pass


if __name__ == '__main__':
    main()
