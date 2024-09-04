import numpy as np


class Step:
    def __init__(self, x_ref: np.ndarray, T: int):
        self._x_ref = np.tile(x_ref, T)

    def __call__(self, t: float) -> np.ndarray:
        return self._x_ref


class Ramp:
    def __init__(self, velocity: float, offset: float, horizon: int, dt: float):
        self.vel = velocity
        self.c = offset
        self.T = horizon
        self.dt = dt

    def __call__(self, t: float|np.ndarray) -> np.ndarray:
        horizon = t+self.dt + np.arange(self.T)*self.dt
        traj = np.empty(2*self.T)
        traj[0::2] = self.vel*horizon + self.c
        traj[1::2] = self.vel
        return traj


class Sinusoidal:
    def __init__(self, amplitude: float, frequency_hz: float,
                 T: float, dt: float, method = 'sin') -> np.ndarray:
        self.A = amplitude
        hz2rad = 2*np.pi
        self.w = frequency_hz * hz2rad
        self.T = T
        self.dt = dt
        self.method = method

    def __call__(self, t: float) -> np.ndarray:
        horizon = t+self.dt + np.arange(self.T)*self.dt
        if self.method == 'cos':
            pos_ref = self.A * (1 - np.cos(self.w*horizon))
            vel_ref = self.w * self.A * np.sin(self.w*horizon)
        else: # sin
            pos_ref = self.A * np.sin(self.w*horizon)
            vel_ref = self.w * self.A * np.cos(self.w*horizon)
        traj = np.empty(2*self.T)
        traj[0::2] = pos_ref
        traj[1::2] = vel_ref
        return traj
