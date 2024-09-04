import numpy as np
from .. import model

class SingleLinkArm(model.ModelBase):
    def __init__(self, mass, length, damping, gravity=9.8):
        self.m = mass
        self.len = length
        self.b = damping
        self.g = gravity

    def _f(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        damping = self.b * x[1]
        f_gravity = 0.5*self.m*self.g*self.len*np.cos(x[0])

        xdot = np.empty_like(x)
        xdot[0] = x[1]
        xdot[1] = (u[0] - damping - f_gravity) * 3/(self.m*self.len**2)
        return xdot

    def affinize(self, x_p: np.ndarray, u_p: np.ndarray) -> model.AffineModel:
        '''
        Affinize continuous-time dynamics around affinization point.

        Args:
        x_p: affinization state (n,)
        u_p: affinization input (m,)

        Returns:
        A: affinized state matrix (n, n)
        B: affinized input matrix (n, m)
        w: affinized constant term (n,)
        '''
        A = np.array([[0, 1],
                      [1.5*self.g/self.len*np.sin(x_p[0]), -3*self.b/(self.m*self.len**2)]])
        B = np.array([[0], [3/(self.m*self.len**2)]])
        w = self._f(x_p, u_p) - A @ x_p - B @ u_p
        return model.AffineModel(A, B, w)

    def linearize(self, x_eq: np.ndarray, u_eq: np.ndarray) -> model.LinearModel:
        '''
        Linearize continuous-time dynamics around equilibrium point.

        Args:
        x_eq: equilibrium state (n,)
        u_eq: equilibrium input (m,)

        Returns:
        A: linearized state matrix (n, n)
        B: linearized input matrix (n, m)
        '''
        xdot = self._f(x_eq, u_eq)
        assert xdot @ xdot < 1e-15, 'Not an equilibrium point'

        sys = self.affinize(x_eq, u_eq)
        return model.LinearModel(sys.A, sys.B)

    def getEquilibriumTorque(self, angle: float) -> float:
        '''
        Calculate the torque required to hold the arm at a given angle.

        Args:
        angle: angle in radians

        Returns:
        torque: torque required to hold the arm at the given angle
        '''
        return 0.5*self.m*self.g*self.len*np.cos(angle)


def main():
    arm = SingleLinkArm(mass=0.5, length=0.3, damping=0.1)

    angles = [0., np.radians(30), -np.radians(45), np.radians(60), np.radians(90)]

    for angle in angles:
        x_eq = np.array([angle, 0])
        u_eq = np.array([arm.getEquilibriumTorque(x_eq[0])])
        sys = arm.linearize(x_eq, u_eq)
        sys = arm.affinize(x_eq, u_eq)

    x = np.array([0.0, 0.0])
    u = np.array([0.5 + arm.getEquilibriumTorque(x[0])])
    x_next = arm.integrateRK4(x, u)
    print('x_next:', x_next)
    x_next = sys.integrateRK4(x, u, dt=0.01)
    print('x_next:', x_next)
    sys_d = model.c2d(sys, dt=0.01, terms=5)
    x_next = sys_d._f(x, u)
    print('x_next:', x_next)
    print(sys.A)
    print(sys.B)
    print(sys.w)

if __name__ == '__main__':
    main()
