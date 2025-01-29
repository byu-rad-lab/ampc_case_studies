import numpy as np


class Attitude:
    def __init__(self, euler):
        self.Sx, self.Sy, self.Sz = np.sin(euler)
        self.Cx, self.Cy, self.Cz = np.cos(euler)
        self.SECy = 1 / self.Cy
        self.Ty = self.Sy * self.SECy

    @property
    def Rx(self):
        return np.array([[1, 0, 0], [0, self.Cx, -self.Sx], [0, self.Sx, self.Cx]])

    @property
    def Ry(self):
        return np.array([[self.Cy, 0, self.Sy], [0, 1, 0], [-self.Sy, 0, self.Cy]])

    @property
    def Rz(self):
        return np.array([[self.Cz, -self.Sz, 0], [self.Sz, self.Cz, 0], [0, 0, 1]])

    @property
    def R_b2i(self):
        return self.Rz @ self.Ry @ self.Rx
        R_b2i = np.array([[Cy*Cz, Sx*Sy*Cz - Cx*Sz, Cx*Sy*Cz + Sx*Sz],
                          [Cy*Sz, Sx*Sy*Sz + Cx*Cz, Cx*Sy*Sz - Sx*Cz],
                          [-Sy,   Sx*Cy,            Cx*Cy]])

    @property
    def dRx(self):
        return np.array([[0, 0, 0], [0, -self.Sx, -self.Cx], [0, self.Cx, -self.Sx]])

    @property
    def dRy(self):
        return np.array([[-self.Sy, 0, self.Cy], [0, 0, 0], [-self.Cy, 0, -self.Sy]])

    @property
    def dRz(self):
        return np.array([[-self.Sz, -self.Cz, 0], [self.Cz, -self.Sz, 0], [0, 0, 0]])

    @property
    def dR_rpy(self):
        Rx, Ry, Rz = self.Rx, self.Ry, self.Rz
        dRx, dRy, dRz = self.dRx, self.dRy, self.dRz
        mat = np.array([Rz @ Ry @ dRx, Rz @ dRy @ Rx, dRz @ Ry @ Rx])
        return mat.transpose(1,0,2)
        # 3D array multiplication works, but just doing mat @ vec3 gives the
        # transpose of the result wanted here. The resulting matrix can be
        # transposed or switching the first 2 axes (as is returned here) also
        # transposes the result. Note, however, that if transposing the
        # rotations (i2b rather than b2i) mat would need to be transposed along
        # the last 2 axes (mat.transpose(0,2,1))...but the resulting matrix will
        # also be transposed so you'd want to use mat.transpose(2,0,1). Since
        # this mat is already returned transposed, you can transpose the
        # returned matrix with transpose(2,1,0) to get the equivalent of
        # mat.transpose(2,0,1). A little bit confusing, but it works.

    @property
    def T(self):
        return np.array([[1, self.Sx*self.Ty, self.Cx*self.Ty],
                         [0, self.Cx, -self.Sx],
                         [0, self.Sx*self.SECy, self.Cx*self.SECy]])

    @property
    def dT_r(self):
        return np.array([[0, self.Cx*self.Ty, -self.Sx*self.Ty],
                         [0, -self.Sx, -self.Cx],
                         [0, self.Cx*self.SECy, -self.Sx*self.SECy]])

    @property
    def dT_p(self):
        return np.array([[0, self.Sx*self.SECy**2, self.Cx*self.SECy**2],
                         [0, 0, 0],
                         [0, self.Sx*self.SECy*self.Ty, self.Cx*self.SECy*self.Ty]])

    @property
    def dT_y(self):
        return np.zeros([3,3])

    @property
    def dT_rpy(self):
        return np.array([self.dT_r, self.dT_p, self.dT_y]).transpose(1,0,2)


def main():
    rpy = np.array([np.radians(90)]*3)
    att = Attitude(rpy)

    x = np.array([1,0,0])
    y = np.array([0,1,0])
    z = np.array([0,0,1])

    np.set_printoptions(precision=3)

    print(att.Rx @ y, z)
    print(att.Ry @ z, x)
    print(att.Rz @ x, y)
    print(att.dRx)
    print(att.dRy)
    print(att.dRz)


    att = Attitude([0,0,np.radians(45)])
    print(att.Rz)
    print(att.dR_rpy)
    print(att.dR_rpy.transpose(1,0,2))

if __name__ == '__main__':
    main()
