"""

"""
import cv2
import numpy as np
from Matrix4D import Matrix4
import math
import os, glob
import scipy.io



def gripper2base():
    """
    compute matrix A
    """
    M = np.zeros((10, 4, 4))
    mat = scipy.io.loadmat('armMat.mat')

    data1 = [[row.flat[0] for row in line] for line in mat['armMat'][0]]
    data2 = [[row.flat[0] for row in line] for line in mat['armMat'][1]]
    data3 = [[row.flat[0] for row in line] for line in mat['armMat'][2]]
    data4 = [[row.flat[0] for row in line] for line in mat['armMat'][3]]

    for i in range(4):
        for j in range(10):
            M[j][0][i] = data1[i][j]

    for i in range(4):
        for j in range(10):
            M[j][1][i] = data2[i][j]

    for i in range(4):
        for j in range(10):
            M[j][2][i] = data3[i][j]

    for i in range(4):
        for j in range(10):
            M[j][3][i] = data4[i][j]

    N = np.zeros((7, 4, 4))
    j = 0
    for i in range(10):
        if i in [0, 2, 3, 4, 5, 6, 9]:
            N[j] = M[i]
            j += 1

    R_gripper2base, t_gripper2base = [], []
    for i in N:
        i = np.linalg.inv(i)
        r = np.zeros((3, 3))
        r = i[0:r.shape[0], 0:r.shape[1]]
        t = i[0:3, -1]
        R_gripper2base.append(r)
        t_gripper2base.append(t)

    return R_gripper2base, t_gripper2base


def save_image(dirname, filename, img):
    """
    This function saves the image to a specified place
    """
    if os.path.exists(dirname) == 0:
        os.makedirs(dirname)
    cv2.imwrite(dirname+filename+".bmp", img)


def target2cam(imgdir, imgfmt):
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
        ind_line = fname.rindex(os.sep)
        ind_dot = fname.rindex('.')
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        objp = np.zeros((row * col, 3), np.float32)
        objp[:, :2] = np.mgrid[0:row, 0:col].T.reshape(-1, 2)
        ret, corners = cv2.findChessboardCorners(gray, (row, col), flags=cv2.CALIB_CB_ADAPTIVE_THRESH)

        # if the chess board corners are found, add object points and image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
            imgpoints.append(corners2)

            img = cv2.drawChessboardCorners(img, (row, col), corners2, ret)
            save_image(fname[0:ind_line+1] + "success/", fname[ind_line+1:ind_dot],img)

    _, mtx, dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    R_target2cam, t_target2cam = [], []
    for fname in images:
        objectpoints = []  # 3d point in real world space
        imagepoints = []  # 2d points in image plane
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        objp = np.zeros((row*col, 3), np.float32)
        objp[:, :2] = np.mgrid[0:row, 0:col].T.reshape(-1, 2)
        ret, corners = cv2.findChessboardCorners(gray, (row, col), flags=cv2.CALIB_CB_ADAPTIVE_THRESH)
        
        # if the chess board corners are found, add object points and image points (after refining them)
        if ret == True:
            objectpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imagepoints.append(corners2)
            objectpoints = np.asarray(objectpoints)[0]
            imagepoints = np.asarray(imagepoints)[0]

            _, rvec, tvec = cv2.solvePnP(objectpoints, imagepoints, mtx, dist, flags=cv2.SOLVEPNP_EPNP)

            R = cv2.Rodrigues(rvec)[0]  # converts a rotation vector to a rotation matrix
            R_target2cam.append(R)
            t_target2cam.append(tvec)

    return R_target2cam, t_target2cam



square_width = 14
row = 9
col = 6
R_gripper2base, t_gripper2base = gripper2base()
R_target2cam, t_target2cam = target2cam('Images2/', '.jpg')
R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, method=cv2.CALIB_HAND_EYE_TSAI)
print(R_cam2gripper, '\n\n', t_cam2gripper, '\n\n')

homo = np.zeros((4, 4))
homo[0:R_cam2gripper.shape[0], 0:R_cam2gripper.shape[1]] = R_cam2gripper
homo[0:3, -1] = t_cam2gripper.reshape(3,)
homo[-1][-1] = 1

ans = Matrix4(np_mat=homo)
dof6 = ans.get_dof6(axes='rzyx')
print(dof6)
