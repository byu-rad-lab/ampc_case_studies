import numpy as np
from enum import Enum, auto


class Mode(Enum):
    STEP = auto()
    LINE = auto()
    SINE = auto()
    POLY = auto()


class Trajectory1D:
    def __init__(self, mode: Mode = Mode.LINE, params: list = [0,0]) -> None:
        '''
        Trajectory constructor.

        LINE: params = [velocity, offset]
        SINE: params = [magnitude, period, phase_shift, offset]
        POLY: params = [..., jerk, acceleration, velocity, offset]

        Note that polynomials can be n-th order (any size).
        '''
        self.setMode(mode, params)

    def setMode(self, mode: Mode, params: list) -> None:
        '''
        Set the mode of the trajectory with accompanying parameters.

        STEP: params = [offset]
        LINE: params = [velocity, offset]
        SINE: params = [magnitude, period, phase_shift, offset]
        POLY: params = [..., jerk, acceleration, velocity, offset]

        Note that polynomials can be n-th order (any size).
        '''
        self._params = [*params]
        self._mode = mode
        if mode is Mode.STEP:
            self.eval = self._evalStep
        elif mode is Mode.LINE:
            self.eval = self._evalLine
        elif mode is Mode.SINE:
            self.eval = self._evalSine
            self._params[1] = 2*np.pi / self._params[1]
        elif mode is Mode.POLY:
            self.eval = self._evalPoly

    def _evalStep(self, t: np.ndarray | float, deriv_num: int) -> np.ndarray | float:
        if deriv_num == 0:
            return self._params[0]
        else:
            return 0.0

    def _evalLine(self, t: np.ndarray | float, deriv_num: int) -> np.ndarray | float:
        if deriv_num == 0:
            return self._params[0]*t + self._params[1]
        elif deriv_num == 1:
            return self._params[0]
        else:
            return 0.0

    def _evalSine(self, t: np.ndarray | float, deriv_num: int) -> np.ndarray | float:
        freq_pow = pow(self._params[1], deriv_num)
        sine = np.sin(self._params[1]*t + self._params[2] + deriv_num*np.pi*0.5)
        return self._params[0]*freq_pow*sine + self._params[3]*(deriv_num == 0)

    def _evalPoly(self, t: np.ndarray | float, deriv_num: int) -> np.ndarray | float:
        raise NotImplementedError()

def main():
    traj = Trajectory1D(Mode.LINE)
    traj.setMode(Mode.SINE, [1.0, 1.0, np.pi/2, 0])
    p = traj.eval(0.0, 0)
    print(p)

if __name__ == '__main__':
    main()
