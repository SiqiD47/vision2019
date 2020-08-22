"""
Eye-to-hand calibration.

Author: Siqi Dai
"""


import cv2
import numpy as np
from Matrix4D import Matrix4
import math
import glob
import os


def save_image(dirname, filename, img):
    """
    This function saves the image to a designated directory
    """
    if os.path.exists(dirname) == 0:
        os.makedirs(dirname)
    cv2.imwrite(dirname+filename+".bmp", img)


def gripper2base(dof6_log):
    """
    This function computes the homogeneous matrix that transforms a point
    expressed in the gripper frame to the robot base frame (bTg).
    :param dof6_log: log file that saves dof6 from tool to base
    :return: R_gripper2base, t_gripper2base
    """
    # read log，get homogeneous transformation matrix from gripper frame to robot base frame
    file = open(dof6_log, "r")
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

    R_gripper2base, t_gripper2base = [], []
    for m in res:
        # read dof6
        dof6 = [m[1], -m[0], m[2], m[5] * math.pi / 180,
                m[4] * math.pi / 180, m[3] * math.pi / 180]
        homo = Matrix4(dof6=dof6, axes='rzyx')
        mat = homo.get_mat4()
        # mat = homo.get_mat4_change_axes(axes1='rzyx', axes2='rxyz')
        mat = np.linalg.inv(mat)
        r = np.zeros((3, 3))
        r = mat[0:r.shape[0], 0:r.shape[1]]
        t = mat[0:3, -1]
        R_gripper2base.append(r)
        t_gripper2base.append(t)

    return R_gripper2base, t_gripper2base


def target2cam(imgdir, imgfmt):
    """
    This function computes the homogeneous matrix that transforms a point
    expressed in the target frame to the camera frame (cTt).
    :param imgdir: image directory
    :param imgfmt: image format (e.g. '.bmp', '.jpg', etc.)
    :return: R_target2cam, t_target2cam
    """
    global square_width, row, col
    R_target2cam, t_target2cam = [], []

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, square_width, 0.001)

    # arrays to store object points and image points from all the images
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane
    images = glob.glob(imgdir + '*' + imgfmt)
    images.sort()
    print(images)

    gray = np.zeros((0, 0))
    for fname in images:
        ind_line = fname.rindex(os.sep)
        ind_dot = fname.rindex('.')
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        objp = np.zeros((row * col, 3), np.float32)
        objp[:, :2] = np.mgrid[0:row, 0:col].T.reshape(-1, 2)
        ret, corners = cv2.findChessboardCorners(gray, (row, col), None)

        # if the chess board corners are found, add object points and image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
            imgpoints.append(corners2)
            img = cv2.drawChessboardCorners(img, (row, col), corners2, ret)
            save_image(fname[0:ind_line + 1] + "success/", fname[ind_line + 1:ind_dot], img)
    _, mtx, dist, rr, tt = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None, criteria=criteria)

    qq = np.ones((4, 1))
    for fname in images:
        objectpoints = []  # 3d point in real world space
        imagepoints = []  # 2d points in image plane
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        objp = np.zeros((row*col, 3), np.float32)
        objp[:, :2] = np.mgrid[0:row, 0:col].T.reshape(-1, 2)
        ret, corners = cv2.findChessboardCorners(gray, (row, col), None)

        # if the chess board corners are found, add object points and image points (after refining them)
        if ret == True:
            objectpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),criteria)
            imagepoints.append(corners2)
            objectpoints = np.asarray(objectpoints)[0]
            imagepoints = np.asarray(imagepoints)[0]

            _, rvec, tvec = cv2.solvePnP(objectpoints, imagepoints, mtx, dist, flags=cv2.SOLVEPNP_EPNP)

            R = cv2.Rodrigues(rvec)[0]  # converts a rotation vector to a rotation matrix
            R_target2cam.append(R)
            t_target2cam.append(tvec)

        if fname == 'Images/21.bmp':
            print("ldkaldjdkasjdka")
            q = corners2[0]
            print(q)
            qq[0:2][:] = q.reshape(2, 1)
            qq[2][0] = 0
            print(qq)



    p = imgpoints[0][0]
    pp = np.ones((4, 1))
    pp[0:2][:] = p.reshape(2,1)
    pp[2][0] = 0
    print(pp)

    return R_target2cam, t_target2cam, pp, qq


square_width = 15  # square width of chessboard (mm)
row = 11  # 行角点数
col = 8  # 列角点数

R_gripper2base, t_gripper2base = gripper2base('CameraLog.txt')
R_target2cam, t_target2cam, p, q = target2cam('Images/', '.bmp')
R_cam2base, t_cam2base = cv2.calibrateHandEye(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, method=cv2.CALIB_HAND_EYE_TSAI)

# get homogeneous matrix from R_cam2base, t_cam2base
# homo = np.zeros((4, 4))
# homo[0:R_cam2base.shape[0], 0:R_cam2base.shape[1]] = R_cam2base
# homo[0:3, -1] = t_cam2base.reshape(3,)
# homo[-1][-1] = 1
# print(homo, '\n')
#
# ans = Matrix4(np_mat=homo)
# dof6 = ans.get_dof6(axes='rzyx')
# print(dof6)  # dof6 from camera to base

mat = np.matrix([[-0.4541  , -0.8515   , 0.2621   , 0.4994],
                     [-0.5582  ,  0.0426  , -0.8286  ,  1.0584],
                     [0.6945  , -0.5226  , -0.4946   , 1.2000],
                     [0, 0, 0, 1]])

point_1 = mat @ p
print('\n', point_1)

point_2 = mat @ q
print('\n', point_2)

