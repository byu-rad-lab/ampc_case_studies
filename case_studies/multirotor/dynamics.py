import numpy as np
from enum import Enum, auto
from .. import model
from . import rotations as rot

def skew(vec3):
    x,y,z = vec3
    return np.array([[0,-z,y], [z,0,-x], [-y,x,0]])


class Multirotor(model.ModelBase):
    class VelocityMode(Enum):
        BODY = auto()
        INERTIAL = auto()

    def __init__(self, equilibrium_throttle: float, damping: float,
                 gravity: float=9.8, mode: VelocityMode=VelocityMode.BODY):
        self.s_eq = equilibrium_throttle
        self.cd = damping
        self.g = gravity
        self.setVelocityMode(mode)

    def setVelocityMode(self, mode: VelocityMode) -> None:
        if mode == self.VelocityMode.BODY:
            self._f = self._f_bodyVelocity
            self.affinize = self.affinize_bodyVelocity
            self.linearize = self.linearize_bodyVelocity
        else:
            self._f = self._f_inertialVelocity
            self.affinize = self.affinize_inertialVelocity
            self.linearize = self.linearize_inertialVelocity

    def getEquilibriumInput(self, x=None) -> np.ndarray:
        return np.array([self.s_eq, 0,0,0])

    def _f_bodyVelocity(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        p = slice(0,3)
        a = slice(3,6)
        v = slice(6,9)
        w = slice(1,4)

        att = rot.Attitude(x[a])
        vel_b = x[v]
        s = u[0]
        angvel = u[w]

        R_b2i = att.R_b2i
        M = np.diag([1,1,0])

        gravity_b = self.g * R_b2i[2]
        force_b = np.array([0, 0, self.g*s/self.s_eq])
        drag_b = self.cd * M @ vel_b
        coriolis = np.cross(angvel, vel_b)

        xdot = np.empty_like(x)
        xdot[p] = R_b2i @ vel_b
        xdot[a] = att.T @ angvel
        xdot[v] = gravity_b - force_b - drag_b - coriolis
        return xdot

    def _f_inertialVelocity(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        p = slice(0,3)
        a = slice(3,6)
        v = slice(6,9)
        w = slice(1,4)

        att = rot.Attitude(x[a])
        vel_i = x[v]
        s = u[0]

        R_b2i = att.R_b2i
        M = np.diag([1,1,0])

        gravity_i = np.array([0,0,self.g])
        force_i = self.g*s/self.s_eq * R_b2i[:,2]
        vel_b = R_b2i.T @ vel_i
        drag_b = self.cd * M @ vel_b
        drag_i = R_b2i @ drag_b

        xdot = np.empty_like(x)
        xdot[p] = vel_i
        xdot[a] = att.T @ u[w]
        xdot[v] = gravity_i - force_i - drag_i
        return xdot

    def affinize_bodyVelocity(self, x_p: np.ndarray, u_p: np.ndarray) -> model.AffineModel:
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
        p = slice(0,3)
        a = slice(3,6)
        v = slice(6,9)
        w = slice(1,4)

        att = rot.Attitude(x_p[a])
        vel_b = x_p[v]

        dR_rpy = att.dR_rpy
        R_b2i = att.R_b2i
        M = np.diag([1,1,0])

        A = np.zeros([9,9])
        A[p,a] = dR_rpy @ vel_b
        A[p,v] = R_b2i
        A[a,a] = att.dT_rpy @ u_p[w]
        A[v,a] = dR_rpy.transpose(2,1,0) @ np.array([0,0,self.g])
        A[v,v] = -self.cd*M - skew(u_p[w])

        B = np.zeros([9,4])
        B[a,w] = att.T
        B[v,0] = np.array([0, 0, -self.g/self.s_eq])
        B[v,w] = skew(vel_b)

        w = self._f_bodyVelocity(x_p, u_p) - A @ x_p - B @ u_p
        return model.AffineModel(A, B, w)

    def affinize_inertialVelocity(self, x_p: np.ndarray, u_p: np.ndarray) -> model.AffineModel:
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
        p = slice(0,3)
        a = slice(3,6)
        v = slice(6,9)
        w = slice(1,4)

        att = rot.Attitude(x_p[a])
        vel_i = x_p[v]
        s = u_p[0]

        dR_rpy = att.dR_rpy
        R_b2i = att.R_b2i
        vel_b = R_b2i.T @ vel_i
        M = np.diag([1,1,0])
        force_b = np.array([0,0,self.g*s/self.s_eq])

        A = np.zeros([9,9])
        A[p,v] = np.eye(3)
        A[a,a] = att.dT_rpy @ u_p[w]
        A[v,a] = -dR_rpy @ force_b
        A[v,a] -= self.cd * (dR_rpy @ (M @ vel_b) + R_b2i @ M @ (dR_rpy.transpose(1,0,2) @ vel_i))
        A[v,v] = -self.cd * R_b2i @ M @ R_b2i.T

        B = np.zeros([9,4])
        B[a,w] = att.T
        B[v,0] = -self.g/self.s_eq * R_b2i[:,2]

        w = self._f_inertialVelocity(x_p, u_p) - A @ x_p - B @ u_p
        return model.AffineModel(A, B, w)

    def linearize_bodyVelocity(self, x_eq: np.ndarray, u_eq: np.ndarray) -> model.LinearModel:
        '''
        Linearize continuous-time dynamics around equilibrium point.

        Args:
        x_eq: equilibrium state (n,)
        u_eq: equilibrium input (m,)

        Returns:
        A: linearized state matrix (n, n)
        B: linearized input matrix (n, m)
        '''
        yaw = x_eq[5]
        # att = rot.Attitude([0,0,yaw])

        # Sz = np.sin(yaw)
        # Cz = np.cos(yaw)

        # Rz_y = np.array([[Cz, -Sz, 0],
        #                  [Sz,  Cz, 0],
        #                  [0,   0,  1]])
        Rz_y = rot.Attitude([0,0,yaw]).Rz
        I = np.eye(3)
        M = np.diag([1,1,0])

        p = slice(0,3)
        a = slice(3,6)
        v = slice(6,9)
        A = np.zeros([9,9])
        A[p,v] = Rz_y
        A[v,a] = self.g * np.array([[0,-1,0],[1,0,0],[0,0,0]])
        A[v,v] = -self.cd * M

        w = slice(1,4)
        B = np.zeros([9,4])
        B[a,w] = I
        B[v,0] = np.array([0, 0, -self.g/self.s_eq])

        return model.LinearModel(A, B)

    def linearize_inertialVelocity(self, x_eq: np.ndarray, u_eq: np.ndarray) -> model.LinearModel:
        '''
        Linearize continuous-time dynamics around equilibrium point.

        Args:
        x_eq: equilibrium state (n,)
        u_eq: equilibrium input (m,)

        Returns:
        A: linearized state matrix (n, n)
        B: linearized input matrix (n, m)
        '''
        yaw = x_eq[5]
        Sz = np.sin(yaw)
        Cz = np.cos(yaw)
        dR_y = np.array([[-Sz, -Cz, 0],
                         [Cz,  -Sz, 0],
                         [0,    0,  0]])
        I = np.eye(3)
        M = np.diag([1,1,0])
        e3 = np.array([0,0,1])

        p = slice(0,3)
        a = slice(3,6)
        v = slice(6,9)
        A = np.zeros([9,9])
        A[p,v] = I
        A[v,a] = dR_y * self.g
        A[v,v] = -self.cd*M

        w = slice(1,4)
        B = np.zeros([9,4])
        B[a,w] = I
        B[v,0] = -self.g/self.s_eq * e3

        return model.LinearModel(A, B)


def deriv_test() -> None:
    sys = Multirotor(equilibrium_throttle=0.5, damping=0.1)
    x_eq = np.array([0,0,-5, 0,0,np.radians(90), 0,0,0])
    u_eq = np.array([sys.s_eq, 0,0,0])
    x = x_eq.copy()
    x[3] = np.radians(10)
    x[6] = -0.1
    u = u_eq.copy()
    u[1] = 1.0

    xd_nl = sys._f_bodyVelocity(x, u)
    xd_aff = sys.affinize_bodyVelocity(x, u)._f(x, u)
    xd_lin = sys.linearize_bodyVelocity(x, u)._f(x-x_eq, u-u_eq)
    print(xd_nl)
    print(xd_aff)
    print(xd_lin)

    xd_nl = sys._f_inertialVelocity(x, u)
    xd_aff = sys.affinize_inertialVelocity(x, u)._f(x, u)
    xd_lin = sys.linearize_inertialVelocity(x, u)._f(x-x_eq, u-u_eq)
    print(xd_nl)
    print(xd_aff)
    print(xd_lin)

def sim_test() -> None:
    import matplotlib.pyplot as plt
    sys = Multirotor(equilibrium_throttle=0.5, damping=0.1)

    x0 = np.array([0,0,-5., 0,0,0, 0,0,0])
    u_list = np.array([
        [sys.s_eq, 0,0,0],
        [sys.s_eq+0.15, 0,0,0],
        [sys.s_eq-0.15, 0,0,0],
        [sys.s_eq, 0,0,0.5],
        [sys.s_eq, 0,0,-0.5],
        [sys.s_eq, 0.5,0,0],
        [sys.s_eq, -0.5,0,0],
        [sys.s_eq, 0,0.5,0],
        [sys.s_eq, 0,-0.5,0]
    ])
    dt = 0.02
    time = np.arange(50)*dt

    for u in u_list:
        x_nl_b = x0.copy()
        x_nl_i = x0.copy()
        x_lin_b = x0.copy()
        x_lin_i = x0.copy()
        x_aff_b = x0.copy()
        x_aff_i = x0.copy()

        x_nl_b_hist = [x0.copy()]
        x_nl_i_hist = [x0.copy()]
        x_lin_b_hist = [x0.copy()]
        x_lin_i_hist = [x0.copy()]
        x_aff_b_hist = [x0.copy()]
        x_aff_i_hist = [x0.copy()]

        for t in time[:-1]:
            sys.setVelocityMode(Multirotor.VelocityMode.BODY)
            x_nl_b = sys.integrateRK4(x_nl_b, u, dt)
            x_nl_b_hist.append(x_nl_b.copy())

            aff_b = model.c2d(sys.affinize(x_nl_b, u), dt, terms=9, return_G=False)
            x_aff_b = aff_b.A @ x_aff_b + aff_b.B @ u + aff_b.w
            x_aff_b_hist.append(x_aff_b.copy())

            x_eq = np.array([0,0,0, 0,0,x_nl_b[5], 0,0,0])
            u_eq = np.array([sys.s_eq, 0,0,0])
            # lin_b = sys.linearize(x_eq, u_eq)
            lin_b = model.c2d(sys.linearize(x_eq, u_eq), dt, terms=9, return_G=False)
            # lin_b = model.c2d(sys.affinize(x_eq, u_eq), dt, terms=9, return_G=False)
            # x_lin_b = lin_b.integrateRK4(x_lin_b-x_eq, u-u_eq) + x_eq
            x_lin_b += lin_b.A @ (x_lin_b - x_eq) + lin_b.B @ (u - u_eq)
            # x_lin_b = lin_b.A @ x_lin_b + lin_b.B @ u + lin_b.w
            x_lin_b_hist.append(x_lin_b.copy())

            sys.setVelocityMode(Multirotor.VelocityMode.INERTIAL)
            x_nl_i = sys.integrateRK4(x_nl_i, u, dt)
            x_nl_i_hist.append(x_nl_i.copy())

            aff_i = model.c2d(sys.affinize(x_nl_i, u), dt, terms=9, return_G=False)
            x_aff_i = aff_i.A @ x_aff_i + aff_i.B @ u + aff_i.w
            x_aff_i_hist.append(x_aff_i.copy())

            x_eq = np.array([0,0,0, 0,0,x_nl_i[5], 0,0,0])
            u_eq = np.array([sys.s_eq, 0,0,0])
            lin_i = sys.linearize(x_eq, u_eq)
            # lin_i = model.c2d(sys.linearize(x_eq, u_eq), dt, terms=9, return_G=False)
            test = model.c2d(sys.linearize(x_eq, u_eq), dt, terms=9, return_G=False)
            lin_i = model.c2d(sys.affinize(x_eq, u_eq), dt, terms=9, return_G=False)
            assert np.linalg.norm(test.A - lin_i.A) < 1e-15
            assert np.linalg.norm(test.B - lin_i.B) < 1e-15
            # x_lin_i = lin_i.integrateRK4(x_lin_i-x_eq, u-u_eq) + x_eq
            # x_lin_i += lin_i.A @ (x_lin_i - x_eq) + lin_i.B @ (u - u_eq)
            x_lin_i = lin_i.A @ x_lin_i + lin_i.B @ u + lin_i.w
            x_lin_i_hist.append(x_lin_i.copy())

        x_nl_b_hist = np.array(x_nl_b_hist)
        x_nl_i_hist = np.array(x_nl_i_hist)
        x_lin_b_hist = np.array(x_lin_b_hist)
        x_lin_i_hist = np.array(x_lin_i_hist)
        x_aff_b_hist = np.array(x_aff_b_hist)
        x_aff_i_hist = np.array(x_aff_i_hist)

        fig,ax = plt.subplots(3,3)
        a: plt.Axes = ax[0,0]
        a.plot(time, x_nl_b_hist[:,0], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,0], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,0], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,0], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,0], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,0], '-.', label='x_lin_i')
        a.legend()
        a: plt.Axes = ax[1,0]
        a.plot(time, x_nl_b_hist[:,1], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,1], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,1], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,1], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,1], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,1], '-.', label='x_lin_i')
        a: plt.Axes = ax[2,0]
        a.plot(time, x_nl_b_hist[:,2], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,2], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,2], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,2], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,2], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,2], '-.', label='x_lin_i')

        a: plt.Axes = ax[0,1]
        a.plot(time, x_nl_b_hist[:,3], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,3], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,3], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,3], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,3], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,3], '-.', label='x_lin_i')
        a.legend()
        a: plt.Axes = ax[1,1]
        a.plot(time, x_nl_b_hist[:,4], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,4], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,4], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,4], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,4], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,4], '-.', label='x_lin_i')
        a: plt.Axes = ax[2,1]
        a.plot(time, x_nl_b_hist[:,5], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,5], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,5], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,5], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,5], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,5], '-.', label='x_lin_i')

        a: plt.Axes = ax[0,2]
        a.plot(time, x_nl_b_hist[:,6], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,6], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,6], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,6], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,6], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,6], '-.', label='x_lin_i')
        a.legend()
        a: plt.Axes = ax[1,2]
        a.plot(time, x_nl_b_hist[:,7], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,7], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,7], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,7], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,7], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,7], '-.', label='x_lin_i')
        a: plt.Axes = ax[2,2]
        a.plot(time, x_nl_b_hist[:,8], label='x_nl_b')
        a.plot(time, x_nl_i_hist[:,8], label='x_nl_i')
        a.plot(time, x_aff_b_hist[:,8], '--', label='x_aff_b')
        a.plot(time, x_aff_i_hist[:,8], '--', label='x_aff_i')
        a.plot(time, x_lin_b_hist[:,8], '-.', label='x_lin_b')
        a.plot(time, x_lin_i_hist[:,8], '-.', label='x_lin_i')

        plt.show()


if __name__ == '__main__':
    sim_test()
