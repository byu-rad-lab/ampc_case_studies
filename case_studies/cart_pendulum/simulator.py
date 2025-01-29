import numpy as np
from time import time as now
from typing import Callable
import affine_mpc_py as ampc

from . import dynamics
from . import trajectory as traj


class Simulator:
    n,m = 4,1
    sys = dynamics.CartPendulum(pendulum_mass=0.25, cart_mass=1.0,
                                pendulum_length=1.0, damping=0.05)
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
        xp = np.array([0.25, np.radians(30), -0.1, 0.1])
        up = np.array([0.1]) + self.sys.getEquilibriumInput(xp[0])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt)
        u_max = np.array([50.0])
        self.mpc.setInputLimits(-u_max, u_max)
        self.mpc.setStateWeights(self.Q)
        xr = np.array([0.75, np.radians(0), 0, 0])
        self.mpc.setReferenceState(xr)
        self.mpc.initializeSolver()

    def updateControlModel(self, x: np.ndarray, xr_traj: np.ndarray, c: int,
                           k: int, u_prev: np.ndarray, method: str):
        xr = xr_traj[k]
        if method in ['lin', 'xeq']:
            mask = np.array([1, 0, 0, 0])
        else:
            mask = np.ones_like(x)
        xp = (1-c)*x*mask + c*xr*mask
        if method in ['uk', 'xeq']:
            up = u_prev
        else:
            up = np.array([self.sys.getEquilibriumInput(xp[0])])
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt, 1e-8)

    def run(self, c: int, k: int, method: str='uk'):
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
    x0 = np.array([0.0, np.radians(0), 0, 0])
    T = 100
    Q = np.array(args.weights) if args.weights is not None else np.array([1., 1, .1, .1])
    assert len(Q) == len(x0)
    print(f'{Q = }')
    ref_types = ['step', 'cos', 'ramp', 'stepz', 'cosz', 'rampz']

    traj_fn = traj.CartPendulumTrajectory(T, dt)
    reference_type = args.ref_type
    if 'z' not in reference_type:
        Q *= np.array([0, 1, 0, 1]) # can't penalize z or zdot when controlling theta
    print(f'{reference_type = }: ', end='')
    if reference_type == 'step':
        default_params = [5]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = np.radians(params[0])
        traj_fn.setThetaMode(traj.Mode.STEP, [amplitude])
        traj_fn.setZMode(traj.Mode.STEP, [x0[0]])
        print(f'amplitude = radians({params[0]})')
    elif reference_type == 'stepz':
        default_params = [1]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = params[0]
        traj_fn.setThetaMode(traj.Mode.STEP, [0.0])
        traj_fn.setZMode(traj.Mode.STEP, [x0[0] + amplitude])
        print(f'amplitude = {params[0]}')
    elif reference_type == 'cos':
        default_params = [5., 1.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = np.radians(-params[0])
        period = tf / params[1]
        offset = x0[0] - amplitude
        phase = np.radians(90)
        traj_fn.setThetaMode(traj.Mode.SINE, [amplitude, period, phase, offset])
        traj_fn.setZMode(traj.Mode.STEP, [x0[0]])
        print(f'ref = cos: amplitude = radians({params[0]:.1f}), period = tf/{params[1]:.1f}')
    elif reference_type == 'cosz':
        default_params = [1., 1.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = -params[0]
        period = tf / params[1]
        offset = x0[0] - amplitude
        phase = np.radians(90)
        traj_fn.setThetaMode(traj.Mode.STEP, [0.0])
        traj_fn.setZMode(traj.Mode.SINE, [amplitude, period, phase, offset])
        print(f'ref = cosz: amplitude = {params[0]:.1f}, period = tf/{params[1]:.1f}')
    elif reference_type == 'ramp':
        default_params = [5.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel =  np.radians(params[0])
        traj_fn.setThetaMode(traj.Mode.LINE, [vel, x0[1]])
        traj_fn.setZMode(traj.Mode.STEP, [0.0])
        print(f'ref = ramp: vel = radians({params[0]:.1f})')
    elif reference_type == 'rampz':
        default_params = [1]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel =  params[0]
        traj_fn.setThetaMode(traj.Mode.STEP, [0.0])
        traj_fn.setZMode(traj.Mode.LINE, [vel, x0[0]])
        print(f'ref = rampz: vel = {params[0]:.1f}')
    else:
        raise ValueError(f'Unrecognized reference type {args.ref_type} - must be in {ref_types}')

    return Simulator(tf, dt, T, x0, Q, traj_fn.eval)


def main():
    pass


if __name__ == '__main__':
    main()
