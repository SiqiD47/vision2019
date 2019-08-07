"""
https://blog.csdn.net/weixin_36444883/article/details/84867362#_429
"""


import math
import numpy as np
from Matrix4D import Matrix4
import cv2
import glob
import os
import shutil
import scipy.linalg


def compute_matB(dof6_log):
    """
    compute matrix A
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

    mats = []
    for m in res:
        # read dof6
        dof6 = [m[0], m[1], m[2], m[5] * math.pi / 180,
                m[4] * math.pi / 180, m[3] * math.pi / 180]
        homo = Matrix4(dof6=dof6, axes='rzyx')
        mat = homo.get_mat4()
        mat = np.linalg.inv(mat)  # base to tool
        mats.append(mat)

    ans = mats[1] @ np.linalg.inv(mats[0])
    return ans


def calib(imgdir, imgfmt):
    global square_width, row, col

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, square_width, 0.001)

    # arrays to store object points and image points from all the images
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane
    images = glob.glob(imgdir + '*' + imgfmt)
    images.sort()

    gray = np.zeros((0, 0))
    for fname in images:
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
    _, mtx, dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    return mtx, dist


def compute_matA(imgdir, imgfmt, mtx, dist):
    """
    compute matrix B
    """
    global square_width, row, col

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, square_width, 0.001)

    # arrays to store object points and image points from all the images
    images = glob.glob(imgdir+'*'+imgfmt)
    images.sort()

    Poses = []
    for fname in images:
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        objp = np.zeros((row*col, 3), np.float32)
        objp[:, :2] = np.mgrid[0:row, 0:col].T.reshape(-1, 2)
        ret, corners = cv2.findChessboardCorners(gray, (row, col), None)

        # if the chess board corners are found, add object points and image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),criteria)
            imgpoints.append(corners2)
            objpoints = np.asarray(objpoints)[0]
            imgpoints = np.asarray(imgpoints)[0]
            _, rvec, tvec = cv2.solvePnP(objpoints, imgpoints, mtx, dist, flags=cv2.SOLVEPNP_EPNP)

            dst = cv2.Rodrigues(rvec)[0]  # converts a rotation vector to a rotation matrix
            chessboardPose = np.zeros((4, 4))
            chessboardPose[0:dst.shape[0], 0:dst.shape[1]] = dst
            chessboardPose[0:3, -1] = tvec.reshape(3,)
            chessboardPose[-1, -1] = 1
            cam2board = np.linalg.inv(chessboardPose)  # cam to board
            Poses.append(cam2board)
            cv2.destroyAllWindows()

    ans = Poses[1] @ np.linalg.inv(Poses[0])
    return ans




square_width = 15
row = 11
col = 8

mtx, dist = calib('Images/', '.bmp')

mat_B = compute_matB('CameraLog.txt')
mat_A = compute_matA("Images2/", '.bmp', mtx, dist)

print('mat_A\n', mat_A, '\n\n')
print('mat_B\n', mat_B, '\n\n')

# need to solve for AX + X(-B) = 0
q = np.zeros((4, 4))
for i in range(4):
    for j in range(4):
        q[i][j] = 1e-50

x = scipy.linalg.solve_sylvester(mat_A, -mat_B, q)
x = x/x[-1][-1]
print('mat_X\n', x, '\n\n')