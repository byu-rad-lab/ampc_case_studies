import numpy as np
from .. import model

class BlockBeam(model.ModelBase):
    def __init__(self, block_mass: float, beam_mass: float,
                 length: float, gravity: float=9.8):
        self.m1 = block_mass
        self.m2 = beam_mass
        self.len = length
        self.g = gravity

    def _f(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        force = u[0]*self.len*np.cos(x[1])
        friction = 2*self.m1*x[0]*x[2]*x[3]
        g_block = self.m1*self.g*x[0]*np.cos(x[1])
        g_beam = 0.5*self.m2*self.g*self.len*np.cos(x[1])
        inertia = self.m2*self.len**2/3 + self.m1*x[0]**2

        xdot = np.empty_like(x)
        xdot[0] = x[2]
        xdot[1] = x[3]
        xdot[2] = x[0]*x[3]**2 - self.g*np.sin(x[1])
        xdot[3] = (force - friction - g_block - g_beam) / inertia
        return xdot

    def affinize(self, x_p: np.ndarray, u_p: np.ndarray) -> model.AffineModel:
        '''
        Affinize continuous-time dynamics around affinization point.

        :param (n,) x_p: affinization state (n,)
        :param (m,) u_p: affinization input (m,)

        :return: AffineModel(A, B, w)
        '''
        Cx1 = np.cos(x_p[1])
        Sx1 = np.sin(x_p[1])
        inertia = self.m2*self.len**2/3 + self.m1*x_p[0]**2

        n1 = -2*self.m1*x_p[0]
        n2 = u_p[0]*self.len - self.m1*self.g*x_p[0] - 0.5*self.m2*self.g*self.len
        n3 = self.m1*self.g*Cx1 + 2*self.m1*x_p[2]*x_p[3]
        d = inertia

        dx3_x0 = n1*(n2*Cx1 + n1*x_p[2]*x_p[3])/d**2 - n3/d

        A = np.array([[0, 0, 1, 0],
                      [0, 0, 0, 1],
                      [x_p[3]**2, -self.g*Cx1, 0, 2*x_p[0]*x_p[3]],
                      [dx3_x0, -n2*Sx1/d, n1*x_p[3]/d, n1*x_p[2]/d]])
        B = np.array([[0],
                      [0],
                      [0],
                      [self.len*Cx1 / d]])
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

        # sys = self.affinize(x_eq, u_eq)

        inertia = self.m2*self.len**2/3 + self.m1*x_eq[0]**2
        dx3_x0 = -self.m1*self.g/inertia

        A = np.zeros((4,4))
        A[0,2] = 1
        A[1,3] = 1
        A[2,1] = -self.g
        A[3,0] = dx3_x0

        B = np.array([[0],
                      [0],
                      [0],
                      [self.len / inertia]])
        return model.LinearModel(A, B)

    def getEquilibriumInput(self, z: float) -> float:
        '''
        Calculate the torque required to hold the arm at a given angle.

        Args:
          angle: angle in radians

        Returns:
          torque: torque required to hold the arm at the given angle
        '''
        return (0.5*self.m2 + self.m1*z/self.len) * self.g


def main():
    sys = BlockBeam(block_mass=0.35, beam_mass=2., length=0.5)

    z_test = [0.1, 0.2, 0.3, 0.4]

    for z in z_test:
        x_eq = np.array([z, 0, 0, 0])
        u_eq = np.array([sys.getEquilibriumInput(x_eq[0])])
        sys_lin = sys.linearize(x_eq, u_eq)
        sys_aff = sys.affinize(x_eq, u_eq)
        print('f:', sys_aff._f(x_eq, u_eq))


    x = np.array([0.25, -np.radians(15), 0.1, 0.01])
    u = np.array([0.5 + sys.getEquilibriumInput(x[0])])
    sys_c = sys.affinize(x, u)
    x_next = sys.integrateRK4(x, u)
    print('x_next:', x_next)
    x_next = sys_aff.integrateRK4(x, u, dt=0.01)
    print('x_next:', x_next)
    sys_d = model.c2d(sys_c, dt=0.01, terms=5)
    x_next = sys_d._f(x, u)
    print('x_next:', x_next)

    print(sys_lin.A)
    print(sys_lin.B)

    print(sys_c.A)
    print(sys_c.B)
    print(sys_c.w)


if __name__ == '__main__':
    main()
