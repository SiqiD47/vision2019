"""
SolvePNP algorithm for dof6 measurement

Author: Zhongyi Zhou
Modified by: Siqi Dai
"""


import cv2
import numpy as np
import glob
import os
import math
from transforms3d.axangles import mat2axangle
from transforms3d.euler import axangle2euler


def homogene(rvecs, tvecs):
    """
    This function is used to generate a homogeneous matrix
    :param rvecs: rotation vectors
    :param tvecs: translation vectors
    """
    # generate homogeneous transformation matrix
    if rvecs.shape == (3, 3):
        R = rvecs
    elif rvecs.shape == (3, 1):
        R = cv2.Rodrigues(rvecs)[0]
    else:
        print("rvecs shape error!")
        return None
    T = tvecs
    homo = np.zeros((R.shape[0]+1, R.shape[1]+1))
    homo[-1, -1] = 1
    homo[0:R.shape[0], 0:R.shape[1]] = R
    homo[0:homo.shape[1] - 1, -1] = T.reshape(3,)
    return homo


def save_blank_img(visual_dir, fn):
    blank_img = 255 * np.ones(shape=[972, 1296, 3], dtype=np.uint8)  # white blank image
    basename = os.path.basename(os.path.normpath(fn))
    cv2.imwrite(os.path.join(visual_dir, basename), blank_img)


def compute_dof(calib_file_path, car_file_path, removed_idx_new, point2f_new, std3D, rvecs_std, tvecs_std):
    """
    This function computes 6-DOF. Note that there should only be 2 images in the car_file_path folder, which are
    the standard image and the image to be analyzed
    :param calib_file_path: directory of calibration images
    :param car_file_path: directory of car images
    :param removed_idx_new: a list that stores the indices of points on the new image that are detected but not
                            selected by 'GUI_Extract3DCoordinates.py'
    :param point2f_new: a list that stores the 2D coordinates of the points on the new image
    :param std3D: a list that stores the 3D coordinates of points on the standard image
    :param rvecs_std: r from the car's base position to camera
    :param tvecs_std: t from the car's base position to camera
    :return: x, y, z, alpha, beta, gamma, number of inliers, total number of feature points, a list of error messages
    """
    error_msg = []  # a list used to store error messages

    # Load intrinsic parameter
    with np.load(calib_file_path + 'dist_para/5para.npz') as X:
        mtx, dist, _, _ = [X[i] for i in ('mtx', 'dist', 'rvecs', 'tvecs')]

    img_set = glob.glob(car_file_path + '*.bmp')
    img_set = sorted(img_set)

    # create a folder for visualization purposes
    visual_dir = car_file_path + 'visual/'
    if os.path.exists(visual_dir) == 0:
        os.makedirs(visual_dir)
    else:
        images = os.listdir(visual_dir)
        for f in images:
            os.remove(os.path.join(visual_dir, f))

    if len(img_set) < 2:
        save_blank_img(visual_dir, "error.bmp")
        return float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0, 0, error_msg

    img = cv2.imread(img_set[1], cv2.IMREAD_GRAYSCALE)

    # start getting rvecs and tvecs for the car at its new position
    objp3D = np.delete(std3D, removed_idx_new, axis=0)  # delete the points that are not selected by "GUI_Extract3DCoordinates.py"
    imgpts = point2f_new  # detected feature points (marked red)
    keypoints = cv2.KeyPoint_convert(imgpts)
    img = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255))  # red

    if len(objp3D) >= 4:  # number of objp3D must be >= 4 for solvePnPRansac()
        # find an object pose from 3D-2D point correspondences using the RANSAC scheme
        ret, rvecs_new, tvecs_new, inliers = cv2.solvePnPRansac(objp3D, point2f_new, mtx, dist,
                                                        useExtrinsicGuess=0, iterationsCount=100,
                                                        reprojectionError=8.0, flags=cv2.SOLVEPNP_EPNP)

        imgpts2, jac = cv2.projectPoints(std3D, rvecs_new, tvecs_new, mtx, dist)  # points re-projected to the image using calculated r and t (marked blue)
        keypoints2 = cv2.KeyPoint_convert(imgpts2)
        img = cv2.drawKeypoints(img, keypoints2, np.array([]), (255, 0, 0))  # blue

        if inliers is not None:
            inliers_points = np.array([point2f_new[m] for m in inliers])
            inliers_points = inliers_points[:, 0]  # points that were not filtered out by "solvePnPRansac()" (marked green)
            keypoints3 = cv2.KeyPoint_convert(inliers_points)
            img = cv2.drawKeypoints(img, keypoints3, np.array([]), (0, 255, 0))  # green
            basename = os.path.basename(os.path.normpath(img_set[1]))
            cv2.imwrite(os.path.join(visual_dir, basename), img)
        else:
            save_blank_img(visual_dir, "error.bmp")
            e = img_set[1] + ": # inliers is 0."
            error_msg.append(e)
            return float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0, len(objp3D), error_msg

    else:
        save_blank_img(visual_dir, "error.bmp")
        e = img_set[1] + ": total # detected points < 4."
        error_msg.append(e)
        return float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0, len(objp3D), error_msg

    # start several homogeneous transformation
    cam2std = np.linalg.inv(homogene(rvecs_std, tvecs_std))  # from camera to car's base position 相机到物体基准位置
    new2cam = homogene(rvecs_new, tvecs_new)  # from car's new position to camera 物体偏移位置到相机
    final_homo = cam2std @ new2cam

    axis_base = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]  # identity
    axis_base2 = final_homo @ np.array(axis_base)
    bias_trans = axis_base2[:3, -1].T
    axis, angle = mat2axangle(final_homo[0:3, 0:3])
    rot_angle = axangle2euler(axis, angle, axes='sxyz')
    bias_rot = np.array(rot_angle) / math.pi * 180

    # get the values of x, y, z, alpha, beta, gamma
    x = np.round(bias_trans[0], 2)
    y = np.round(bias_trans[1], 2)
    z = np.round(bias_trans[2], 2)
    alpha = np.round(bias_rot[0], 2)
    beta = np.round(bias_rot[1], 2)
    gamma = np.round(bias_rot[2], 2)

    return x, y, z, alpha, beta, gamma, len(inliers), len(objp3D), error_msg
