import numpy as np
from time import time as now
from typing import Callable
import affine_mpc_py as ampc

from ..multirotor.dynamics import Multirotor
from . import trajectory as traj


class Simulator:
    n,m = 9,4
    sys = Multirotor(equilibrium_throttle=0.5, damping=0.1,
                     mode=Multirotor.VelocityMode.INERTIAL)
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
        self.mpc.setReferenceState(xr)

        settings = ampc.OSQPSettings()
        # settings.warm_start = False
        self.mpc.initializeSolver(settings)

    def updateControlModel(self, x: np.ndarray, xr_traj: np.ndarray, c: int,
                           k: int, u_prev: np.ndarray, anchor_pt: str):
        xr = xr_traj[k]
        if 'xe' in anchor_pt:
            mask = np.array([0,0,0,0,0,1,0,0,0])
        else:
            mask = np.ones_like(x)
        xp = (1-c)*x*mask + c*xr*mask
        if 'ut' in anchor_pt:
            up = u_prev
        else:
            up = self.sys.getEquilibriumInput(xp)
        model = self.sys.affinize(xp, up)
        self.mpc.setModelContinuous2Discrete(model.A, model.B, model.w, self.dt)

    def run(self, anchor_pt: str, c: int, k: int=0):
        x = self.x0.copy()
        x_hist = [x.copy()]
        xr_hist = [self.getRefTrajectory(0)[0].copy()]
        u_hist = []
        solve_times = []
        cost_integral = 0.0
        u_star = self.sys.getEquilibriumInput(x)
        self._setupMPC()

        for t in self.time[:-1]:
            start = now()
            xr_traj = self.getRefTrajectory(t)
            self.mpc.setReferenceStateTrajectory(xr_traj.flatten())
            self.updateControlModel(x, xr_traj, c, k, u_star, anchor_pt)
            solved = self.mpc.solve(x)
            if solved:
                _ = self.mpc.getNextInput(u_star)
                # u_star = self.mpc.getNextInput()
            else:
                print(':(')
            solve_times.append(now() - start)
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


def getSimulator(args):
    tf = 10.0
    dt = 0.02
    T = 100
    x0 = np.array([0,0,-20., 0,0,0, 0,0,0])
    Q = np.array([1,1,10, 1,1,1, 2,2,2.], dtype=np.float64)
    ref_types = ['step', 'wavy', 'ramp1', 'ramp3']

    traj_fn = traj.EulerStateTrajectory(T, dt)
    if args.ref_type == 'step':
        default_params = [1.0, 2.0]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        pos_step = params[0]
        yaw_step = np.pi / params[1]
        traj_fn.setNorthMode(traj.Mode.STEP, [x0[0] + pos_step])
        traj_fn.setEastMode(traj.Mode.STEP, [x0[1] + pos_step])
        traj_fn.setDownMode(traj.Mode.STEP, [x0[2] - pos_step])
        traj_fn.setYawMode(traj.Mode.STEP, [x0[5] + yaw_step])
        print(f'ref = step: pos amplitude = {pos_step:.1f}, yaw amplitude = pi/{params[1]:.1f}')
    elif args.ref_type == 'wavy':
        default_params = [1., 5., 2., 6.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amp = params[0]
        period = params[1]
        evel = params[2]
        yvel = np.pi/params[3]
        traj_fn.setNorthMode(traj.Mode.SINE, [amp, period, 0, x0[0]])
        traj_fn.setEastMode(traj.Mode.LINE, [evel, x0[1]])
        traj_fn.setDownMode(traj.Mode.SINE, [amp, period, 0.0, x0[2]])
        traj_fn.setYawMode(traj.Mode.LINE, [yvel, x0[5]])
        print(f'ref = wavy: n/d amp = {amp:.1f}, n/d period = {period:.1f}, ', end='')
        print(f'e vel = {evel:.1f}, y vel = pi/{params[3]:.1f}')
    elif args.ref_type == 'ramp1':
        default_params = [5.0]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel = params[0]
        traj_fn.setNorthMode(traj.Mode.STEP, [x0[0]])
        traj_fn.setEastMode(traj.Mode.LINE, [vel, x0[1]])
        traj_fn.setDownMode(traj.Mode.STEP, [x0[2]])
        traj_fn.setYawMode(traj.Mode.STEP, [x0[5]])
        print(f'ref = ramp1: e vel = {vel:.1f}')
    elif args.ref_type == 'ramp3':
        default_params = [3.0]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel = params[0]
        traj_fn.setNorthMode(traj.Mode.LINE, [vel, x0[0]])
        traj_fn.setEastMode(traj.Mode.LINE, [vel, x0[1]])
        traj_fn.setDownMode(traj.Mode.LINE, [-vel, x0[2]])
        traj_fn.setYawMode(traj.Mode.STEP, [x0[5]])
        print(f'ref = ramp3: n/e/d vel = {vel:.1f}')
    else:
        raise ValueError(f'Unrecognized reference type {args.ref_type} - must be in {ref_types}')

    if args.weights is not None:
        Q = np.array(args.weights)
    print('Q =', Q)

    return Simulator(tf, dt, T, x0, Q, traj_fn.eval)
