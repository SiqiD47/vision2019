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
        mat = self.get_mat4()
        R = mat[0:3, 0:3]
        angle1, angle2, angle3 = mat2euler(R, axes)
        euler_angles = [0, 0, 0]  # alpha, beta, gamma
        euler_idx = self.correct_euler_order(axes)
        euler_angles[euler_idx[0]], euler_angles[euler_idx[1]], euler_angles[euler_idx[2]] = angle1, angle2, angle3
        x, y, z = mat[0:3, -1]
        return [x, y, z, euler_angles[0], euler_angles[1], euler_angles[2]]


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


def readCameraLog(fn):
    print("armMat = zeros(4, 4, 20);\n")

    file = open(fn, "r")
    lines = file.readlines()
    res = []
    for line in lines:
        l = []
        for t in line.split():
            try:
                l.append(float(t))
            except ValueError:
                pass
        res.append(l)

    for m in range(1, len(res) + 1):
        dof6 = [res[m - 1][1]/1000, -res[m - 1][0]/1000, res[m - 1][2]/1000, res[m - 1][5]*math.pi/180, res[m - 1][4]*math.pi/180, res[m - 1][3]*math.pi/180]
        homo = Matrix4(dof6=dof6, axes='rzyx')
        mat = homo.get_mat4()
        for i in range(1, 5):
            for j in range(1, 5):
                a = mat[i - 1][j - 1]
                print("armMat(", i, ',', j, ',', m, ') =', a, ';')
        print('\n')
    print("save armMat armMat")


def readCameraLogPlus(fn):
    print("armMat = zeros(4, 4, 13);\n")

    file = open(fn, "r")
    lines = file.readlines()
    res = []
    for line in lines:
        l = []
        for t in line.split():
            try:
                l.append(float(t))
            except ValueError:
                pass
        res.append(l)

    mat_list = []
    for m in range(1, len(res) + 1):
        dof6 = [res[m - 1][1]/1000, -res[m - 1][0]/1000, res[m - 1][2]/1000, res[m - 1][5]*math.pi/180, res[m - 1][4]*math.pi/180, res[m - 1][3]*math.pi/180]
        homo = Matrix4(dof6=dof6, axes='rzyx')
        mat = homo.get_mat4()
        mat_list.append(mat)

    mat_list_correct = []
    mat_0 = np.zeros((4,4))
    mat_0[3][3] = 1
    mat_0[0][0] = 1
    mat_0[1][1] = 1
    mat_0[2][2] = 1
    mat_list_correct.append(mat_list[0])
    for i in range(1, len(mat_list)):
        A = mat_list[0]
        B = mat_list[i]
        X = np.linalg.inv(A) @ B
        mat_list_correct.append(X)

    for m in range(1, len(mat_list_correct)+1):
        mat = mat_list_correct[m-1]
        for i in range(1, 5):
            for j in range(1, 5):
                a = mat[i - 1][j - 1]
                print("armMat(", i, ',', j, ',', m, ') =', a, ';')
        print('\n')
    print("save armMat armMat")



if __name__ == "__main__":
    readCameraLog("CameraLog.txt")

    # 以下为使用示例:
    # mat = np.matrix([[-0.4541,  -0.8515 ,   0.2621 ,   0.4994],
    #                  [-0.5582  ,  0.0426  , -0.8286  ,  1.0584],
    #                  [0.6945  , -0.5226  , -0.4946   , 1.2000],
    #                  [0, 0, 0, 1]])
    #
    # homo = Matrix4(np_mat=mat)
    # dof6 = homo.get_dof6(axes='rzyx')
    # # dof6[3] = dof6[3] * 180 / math.pi
    # # dof6[4] = dof6[4] * 180 / math.pi
    # # dof6[5] = dof6[5] * 180 / math.pi
    # print(dof6)

    # ans = homo.matrix @ homo.matrix
    # print(ans)
    #
    # dof6_ = homo.get_dof6('rxyz')
    # print(dof6_)
    # homo.get_mat4_change_axes(axes1='rxyz', axes2='rzyx')


    #
    # p = np.array([[ , , , ], [ , , , ], [ , , , ], [ , , , ]])
    # print(p)

    #
    # cam2base_mat = np.zeros((4, 4))
    # obj2cam_mat = np.zeros((4, 4))
    #
    # homo = Matrix4(dof6=dof6, axes='rxyz')
    # cam2base = Matrix4(cam2base_mat)  # from camera to robot 相机到机器人
    # obj2cam = Matrix4(obj2cam_mat)  # from object to camera 物体到相机
    #
    # # from object to robot coordinate 物体到机器人 = 相机到机器人 x 物体到相机
    # info = cam2base.get_mat4() @ obj2cam.get_mat4() @ homo.get_mat4()
    # info_obj = Matrix4(np_mat=info)
    #
    # # convert the axes order from 'xyz' to 'zyx'
    # ans = info_obj.get_mat4_change_axes('rxyz', 'rzyx')  # transformation matrix for robot arm
    # ans_obj = Matrix4(np_mat=ans)
    # quarternion, translation = ans_obj.get_quarternion_and_translation('rzyx')  # get quaternion and translation vector
    #
    # print(ans)
    # print(quarternion, translation)

