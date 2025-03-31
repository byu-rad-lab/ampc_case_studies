import numpy as np
import mpl_toolkits.mplot3d as plt3d

from ..animation import SystemAnimator


def R(euler):
    roll,pitch,yaw = euler
    Rx = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])
    Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])
    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])
    R_b2i = Rz @ Ry @ Rx
    return R_b2i


class MultirotorAnimator(SystemAnimator):
    frame = 'ENU'
    # frame = 'NED'

    def __init__(self, ax: plt3d.Axes3D, x, color='b'):
        self.ax = ax
        self.pos_hist = x[:3]
        self.att_hist = x[3:6]
        self.vel_hist = x[6:]
        self.color = color

        self.length = 1.0
        lims = np.array([-1., 1]) * self.length*10

        scale = np.cos(np.pi/4) * self.length
        self.pts = np.array([[-1.,1,-1,1], [1,-1,-1,1], [0]*4]) * scale

        x0 = self.pos_hist[:,0]

        if self.frame == 'ENU':
            ax.set_xlabel('$East (m)$')
            ax.set_ylabel('$North (m)$')
            ax.set_zlabel('$altitude (m)$')

            self.R_ned2enu = np.array([[0,1,0], [1,0,0], [0,0,-1]])
            x0 = self.R_ned2enu @ x0
            self.pts = self.R_ned2enu @ self.pts
        if self.frame == 'NED':
            ax.set_xlabel('$p_x (m)$')
            ax.set_ylabel('$p_y (m)$')
            ax.set_zlabel('$p_z (m)$')

        ax.set_xlim3d(lims + x0[0])
        ax.set_ylim3d(lims + x0[1])
        ax.set_zlim3d(lims + x0[2])

        arm1, = ax.plot(*self.pts[:,:2], color, marker='o', markersize=5)
        arm2, = ax.plot(*self.pts[:,2:], color, marker='o', markersize=5)
        self.arm1: plt3d.axes3d.art3d.Line3D = arm1
        self.arm2: plt3d.axes3d.art3d.Line3D = arm2

        self._drawVehicle(self.pos_hist[:,0], self.att_hist[:,0])
        self._updateLimits(self.pos_hist[:,0])

    def update(self, i):
        pos = self.pos_hist[:,i]
        att = self.att_hist[:,i]
        vehicle = self._drawVehicle(pos, att)
        self._updateLimits(pos)
        return vehicle

    def _drawVehicle(self, pos, att):
        pts = R(att) @ self.pts + pos[:,None]
        if self.frame == 'ENU':
            pts = self.R_ned2enu @ pts
        self.arm1.set_data_3d(*pts[:,:2])
        self.arm2.set_data_3d(*pts[:,2:])
        return self.arm1, self.arm2

    def _updateLimits(self, pos):
        xlim = list(self.ax.get_xlim3d())
        ylim = list(self.ax.get_ylim3d())
        zlim = list(self.ax.get_zlim3d())
        lims = [xlim, ylim, zlim]

        if self.frame == 'ENU':
            pos = self.R_ned2enu @ pos

        buffer = 4.0
        for p,lim in zip(pos, lims):
            low, high = lim
            shift = 0.0
            if p > high - buffer:
                shift = buffer - (high - p)
            elif p - buffer < low:
                shift = p - low - buffer
            high += shift
            low += shift
            lim[0] = low
            lim[1] = high

        self.ax.set_xlim3d(lims[0])
        self.ax.set_ylim3d(lims[1])
        self.ax.set_zlim3d(lims[2])
        return
