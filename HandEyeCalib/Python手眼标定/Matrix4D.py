"""
This program contains a Matrix4 class to provide necessary information for the robot arm to paint.
A 4x4 homogeneous matrix will be created. Based on this matrix and the euler rotational axis,
we can get information such as 6-DOF values, quaternion vector, translation vector, etc.

Author: Siqi Dai
"""


import numpy as np
from transforms3d.euler import euler2mat, euler2quat, mat2euler
import math
import matlab


class Matrix4:
    matrix = np.zeros((4, 4))

    def __init__(self, dof6=None, axes=None, np_mat=None, mat4=None):
        if dof6 is not None and axes is not None:
            """
            Get a 4x4 matrix from the 6-DOF values and the rotational axis. 
            To create a Matrix4 object: x = Matrix4(dof6= ..., axes= ...)
            :param dof6: 6-DOF list: [x y z alpha beta gamma]
            :param axes: euler rotational axis
            """
            mat = np.zeros((4, 4))
            x, y, z = dof6[0], dof6[1], dof6[2]  # x, y, z
            euler_angles = [dof6[3], dof6[4], dof6[5]]  # alpha, beta, gamma
            euler_idx = self.correct_euler_order(axes)  # euler angle idx according to rotation sequence
            R = euler2mat(euler_angles[euler_idx[0]], euler_angles[euler_idx[1]], euler_angles[euler_idx[2]], axes)
            T = np.matrix([[x, y, z]])
            mat[0:3, -1], mat[0:3, 0:3], mat[-1, -1] = T.reshape(3, ), R, 1
            self.matrix = mat

        elif np_mat is not None:
            """
            Copy the content of a given 4x4 numpy matrix
            To create a Matrix4 object: x = Matrix4(np_mat= ...)
            :param np_mat: 4x4 numpy matrix
            """
            self.matrix = np.copy(np_mat) if np_mat.shape == (4, 4) else np.zeros((4, 4))

        elif mat4 is not None:
            """
            Copy the matrix of a given Matrix4 object
            To create a Matrix4 object: x = Matrix4(mat4= ...)
            :param np_mat: Matrix4 object
            """
            self.matrix = mat4.get_mat4()

        else:
            self.matrix = np.zeros((4, 4))


    def get_mat4(self):
        """
        Access the 4x4 numpy matrix from a Matrix4 object
        """
        return self.matrix


    def get_mat4_change_axes(self, axes1='rxyz', axes2='rzyx'):
        """
        Change the 4x4 matrix based on the new rotational axis
        :param axes1: old euler rotational axes
        :param axes2: new euler rotational axes
        :return: a 4x4 numpy matrix
        """
        euler_angles = [0, 0, 0]  # alpha, beta, gamma
        euler_idx1 = self.correct_euler_order(axes1)
        euler_idx2 = self.correct_euler_order(axes2)

        mat_old, mat_new = self.get_mat4(), np.zeros((4, 4))
        mat_new[0:3, -1] = mat_old[0:3, -1]  # translation vector remains the same
        angle1, angle2, angle3 = mat2euler(mat_old[0:3, 0:3], axes1)
        euler_angles[euler_idx1[0]], euler_angles[euler_idx1[1]], euler_angles[euler_idx1[2]] = angle1, angle2, angle3
        mat_new[0:3, 0:3] = euler2mat(euler_angles[euler_idx2[0]], euler_angles[euler_idx2[1]], euler_angles[euler_idx2[2]], axes2)
        mat_new[-1, -1] = 1
        return mat_new


    def get_dof6(self, axes='rxyz'):
        """
        Get the 6-DOF value from the Matrix4 object
        :param axes: euler rotational axis
        :return: 6-DOF list: [x, y, z, alpha, beta, gamma]
        """
        R = np.zeros((3, 3))
        mat = self.get_mat4()
        R = mat[0:R.shape[0], 0:R.shape[1]]
        angle1, angle2, angle3 = mat2euler(R, axes)
        euler_angles = [0, 0, 0]  # alpha, beta, gamma
        euler_idx = self.correct_euler_order(axes)
        euler_angles[euler_idx[0]], euler_angles[euler_idx[1]], euler_angles[euler_idx[2]] = angle1, angle2, angle3
        x, y, z = mat[0:3, -1]
        return [x, y, z, euler_angles[0]/math.pi*180, euler_angles[1]/math.pi*180, euler_angles[2]/math.pi*180]


    def get_quarternion_and_translation(self, axes='rxyz'):
        """
        Get the quaternion and translation from the Matrix4 object
        :param axes: euler rotational axis
        :return: quaternion list: [w, x, y, z]; translation list: [x, y, z]
        """
        mat = self.get_mat4()
        translation = list(mat[0:3, -1])  # x, y, z
        R = mat[0:3, 0:3]
        angle1, angle2, angle3 = mat2euler(R, axes)
        quarternion = list(euler2quat(angle1, angle2, angle3, axes))
        return quarternion, translation


    def correct_euler_order(self, axes):
        """
        Return the correct order of euler rotation angles
        :param axes: euler rotational axis
        """
        if "xyz" in axes:
            return 0, 1, 2
        elif "xzy" in axes:
            return 0, 2, 1
        elif "yzx" in axes:
            return 1, 2, 0
        elif "yxz" in axes:
            return 1, 0, 2
        elif "zxy" in axes:
            return 2, 0, 1
        elif "zyx" in axes:
            return 2, 1, 0
        elif "zxz" in axes:
            return 2, 0, 2
        elif "zyz" in axes:
            return 2, 1, 2
        elif "xyx" in axes:
            return 0, 1, 0
        elif "xzx" in axes:
            return 0, 2, 0
        elif "yzy" in axes:
            return 1, 2, 1
        else:  # "yxy" in axes
            return 1, 0, 1
