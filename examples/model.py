import numpy as np

class ModelBase:
    def _f(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def integrateRK4(self, x: np.ndarray, u: np.ndarray, dt: float = 0.01) -> np.ndarray:
        '''
        RK4 integration of continuous-time dynamics.

        Args:
        x: current state (n, batch)
        u: input to apply for dt (u, batch)

        Returns:
        x_next: state at next time step (n, batch)
        '''
        k1 = self._f(x, u)
        k2 = self._f(x + k1*(dt/2), u)
        k3 = self._f(x + k2*(dt/2), u)
        k4 = self._f(x + k3*dt, u)
        x_next = x + (k1 + 2*(k2 + k3) + k4) * (dt/6)
        return x_next


class AffineModel(ModelBase):
    def __init__(self, A: np.ndarray, B: np.ndarray, w: np.ndarray):
        self.A = A
        self.B = B
        self.w = w

    def _f(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        return self.A @ x + self.B @ u + self.w


class LinearModel(ModelBase):
    def __init__(self, A: np.ndarray, B: np.ndarray):
        self.A = A
        self.B = B

    def _f(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        return self.A @ x + self.B @ u


def c2d(model: LinearModel|AffineModel, dt: float, terms: int=5, return_G: bool=False) -> LinearModel|AffineModel:
    '''
    Discretize continuous-time dynamics.

    Args:
    model: continuous-time model to discretize
    dt: time step

    Returns discretized model, which matches the type of the input model.
    '''
    At = model.A * dt
    G = np.eye(len(model.A))
    At_i = G.copy()
    Ad = G.copy()

    factorial = 1
    t_i = dt
    for i in range(2, terms):
        At_i = At_i @ At
        Ad += At_i / factorial
        factorial *= i
        G += At_i / factorial
        t_i *= dt
    G *= dt

    Bd = G @ model.B

    if type(model) is LinearModel:
        if return_G:
            return LinearModel(Ad, Bd), G
        else:
            return LinearModel(Ad, Bd)

    wd = G @ model.w
    if return_G:
        return AffineModel(Ad, Bd, wd), G
    else:
        return AffineModel(Ad, Bd, wd)
