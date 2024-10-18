import numpy as np

from .. import model


class CartPendulum(model.ModelBase):
    def __init__(self, cart_mass: float, pendulum_mass: float,
                 pendulum_length: float, damping: float,
                 gravity: float=9.8):
        self.m_c = cart_mass
        self.m_p = pendulum_mass
        self.len = pendulum_length
        self.b = damping
        self.g = gravity

    def _f(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        tmp = self.m_p*self.len*0.5*np.cos(x[1])
        M = np.array([[self.m_c + self.m_p, tmp],
                      [tmp, self.m_p*self.len**2/3]])
        c = np.array([self.m_p*0.5*self.len*x[3]**2*np.sin(x[1]) + u[0] - self.b*x[2],
                      0.5*self.m_p*self.g*self.len*np.sin(x[1])])

        xdot = np.empty_like(x)
        xdot[0] = x[2]
        xdot[1] = x[3]
        xdot[2:] = np.linalg.solve(M, c)
        return xdot

    def affinize(self, x_p: np.ndarray, u_p: np.ndarray) -> model.AffineModel:
        '''
        Affinize continuous-time dynamics around affinization point.

        :param (n,) x_p: affinization state (n,)
        :param (m,) u_p: affinization input (m,)

        :return: AffineModel(A, B, w)
        '''
        S,C = np.sin(x_p[1]), np.cos(x_p[1])
        S2,C2 = np.sin(2*x_p[1]), np.cos(2*x_p[1])

        den = 3*self.m_p*S**2 + self.m_p + 4*self.m_c

        dx2_x1 = -3*self.g*C2 + 2*self.len*x_p[3]**2*C
        dx2_x1 *= 3*self.m_p*S**2 + self.m_p + 4*self.m_c
        tmp = 8*self.b*x_p[2] + 3*self.g*self.m_p*S2
        tmp -= 4*self.len*self.m_p*x_p[3]**2*S + 8*u_p[0]
        tmp *= 3*S*C
        dx2_x1 += tmp
        dx2_x1 *= self.m_p / den**2

        dx2_x2 = -4*self.b / den

        dx2_x3 = 4*self.len*self.m_p*x_p[3]*S / den

        dx3_x1 = 4*self.b*x_p[2]*C + 4*self.g*S*(self.m_p + self.m_c)
        dx3_x1 -= self.len*self.m_p*x_p[3]**2*S2 + 4*u_p[0]*C
        dx3_x1 *= -3*self.m_p*S*C
        tmp = -2*self.b*x_p[2]*S + 2*self.g*(self.m_p + self.m_c)*C
        tmp += 2*u_p[0]*S - self.len*self.m_p*x_p[3]**2*C2
        dx3_x1 += (3*self.m_p*S**2 + self.m_p + 4*self.m_c) * tmp
        dx3_x1 *=  3 / (self.len*den**2)

        dx3_x2 = 6*self.b*C / (self.len*den)

        dx3_x3 = -3*self.m_p*x_p[3]*S2 / den

        A = np.array([[0, 0, 1, 0],
                      [0, 0, 0, 1],
                      [0, dx2_x1, dx2_x2, dx2_x3],
                      [0, dx3_x1, dx3_x2, dx3_x3]])

        B = np.array([[0],
                      [0],
                      [4 / den],
                      [-6*C / (self.len*den)]])

        w = self._f(x_p, u_p) - A @ x_p - B @ u_p
        return model.AffineModel(A, B, w)

    def linearize(self, x: np.ndarray, u: np.ndarray) -> model.LinearModel:
        '''
        Linearize continuous-time dynamics around operating point.

        :param (n,) x: operating state (n,)
        :param (m,) u: operating input (m,)

        :return: LinearModel(A, B)
        '''
        den = self.m_p + 4*self.m_c

        dx2_x1 = -3*self.g*self.m_p / den
        dx2_x2 = -4*self.b / den
        dx3_x1 = 3 * (2*self.g*(self.m_p + self.m_c)) / (self.len*den)
        dx3_x2 = 6*self.b / (self.len*den)

        A = np.array([[0, 0, 1, 0],
                      [0, 0, 0, 1],
                      [0, dx2_x1, dx2_x2, 0],
                      [0, dx3_x1, dx3_x2, 0]])

        B = np.array([[0],
                      [0],
                      [4 / den],
                      [-6 / (self.len*den)]])
        return model.LinearModel(A, B)

    def getEquilibriumInput(self, x: float) -> float:
        return 0.0


def main():
    sys = CartPendulum(pendulum_mass=0.25, cart_mass=1, pendulum_length=1, damping=0.05)

    x_eq = np.zeros(4)
    u_up = np.zeros(1)

    x_p = np.array([0.25, -np.radians(15), 0.1, 0.01])
    u_p = np.array([0.5])

    aff_sys = sys.affinize(x_p, u_p)
    print('A:', aff_sys.A)
    print('B:', aff_sys.B)
    print('w:', aff_sys.w)

    lin_sys = sys.linearize(x_eq, u_up)
    print('A:', lin_sys.A)
    print('B:', lin_sys.B)

    return


if __name__ == '__main__':
    main()
