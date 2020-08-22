"""
This program is used to further preprocess the standard images before the GUI starts.
AKA: Only the feature points SELECTED by "GUI_Extract3DCoordinates.py" will be shown
on the image saved in the folder "car_xx/std_image/".

Author: Siqi Dai
"""


import cv2
import os
from FeatureDetection import feature_detection
from PathsAndParameters import *
from PreprocessStandardImages import len_left, len_left2, len_right, len_right2
from multiprocessing.pool import ThreadPool
from FeatureMatching import show_label
import numpy as np
import glob


def extract_3d(txt_path, num_of_points):
    """
    This function reads a txt file of a specific format. It extracts the 3D coordinates
    of the feature points on the image and saves them as a txt file.
    The format of the txt file should be as follows:
    =================
    1
    Delta X: -135.45mm
    Delta Y: -106.58mm
    Delta Z: 41.44mm
    =================
    2
    Delta X: -122.66mm
    Delta Y: -106.58mm
    Delta Z: 37.47mm
    =================
    ...

    """
    file = open(txt_path)
    contents = file.readlines()

    numofFeatures = num_of_points
    coordinates = np.zeros((numofFeatures, 3))

    m = []
    idx_points_non_existed = []
    for i in range(len(contents)):
        if contents[i][0] == '=':
            ptIndex = int(contents[i+1])
            x = float(contents[i+2][9:-3]) + offset[0]
            y = float(contents[i+3][9:-3]) + offset[1]
            z = float(contents[i+4][9:-3]) + offset[2]
            coordinates[ptIndex, :] = x, y, z
            m.append(ptIndex)

    for i in range(num_of_points):
        if i not in m:
            idx_points_non_existed.append(i)
    file.close()
    return coordinates, idx_points_non_existed  # "idx_points_non_existed" are indices of the points that can be
                                            # detected by the blob detection but don't have a pre-defined 3D coordinate


def feature_matching_preprocess(car_file_path, idx_points_non_existed):
    """
    After running this method, only the points selected by the user will be remained on the image
    saved in "car_xx/std_image/".
    :param car_file_path: directory of the car images
    :param idx_points_non_existed: indices of the points that are detected but are not selected by the user.
                                   Note: The user can select whichever points he/she wants using
                                   "GUI_Extract3DCoordinates.py"
    :return:
        point2f_std_remain: 2D coords of points that are selected by the user
        idx_points_non_existed: indices of the points that are not selected by the user
        keypoints_std: keypoints that are selected by the user (this is the same as 'point2f_std_remain'
                       but is of another format)
    """
    # define the file path
    path_std = car_file_path + "std_image/"

    if os.path.exists(path_std) == 0:
        os.makedirs(path_std)
    else:
        imgs = os.listdir(path_std)
        for f in imgs:
            path = os.path.join(path_std, f)
            os.remove(path)

    img_name_std = car_file_path + fn_std  # path of the standard image
    img_std = cv2.imread(img_name_std, cv2.IMREAD_GRAYSCALE)

    # detect features
    keypoints_std = feature_detection(img_std)
    point2f_std = cv2.KeyPoint_convert(keypoints_std)

    keypoints_std_remain = [keypoints_std[i] for i in range(len(keypoints_std)) if i not in idx_points_non_existed]
    point2f_std_remain = [[point2f_std[i][0], point2f_std[i][1]] for i in range(len(point2f_std)) if i not in idx_points_non_existed]
    point2f_std_remain = np.asarray(point2f_std_remain)

    newnum = [i for i in range(len(keypoints_std))]
    newnum_remain = np.array(list(set(newnum)-set(idx_points_non_existed)))

    img_with_keypoints = cv2.drawKeypoints(img_std, keypoints_std_remain, np.array([]),(0, 0, 255))  # draw keypoints
    img_with_label = show_label(img_with_keypoints, point2f_std_remain, newnum_remain, 1)  # draw label (indices of feature points)

    basename = os.path.basename(os.path.normpath(img_name_std))
    cv2.imwrite(os.path.join(path_std, basename), img_with_label)

    return point2f_std_remain, idx_points_non_existed, keypoints_std


def get_r_t_carbase2cam(calib_file_path, std3D, removed_idx_std, point2f_std):
    """
    This function get r & t from car's base position to camera
    :param calib_file_path: directory of calibration images
    :param std3D: a list that stores the 3D coordinates of points on the image
    :param removed_idx_std: a list that stores the indices of points on standard image that are not selected
    :param point2f_std: a list that stores the 2D coordinates of the matched points on standard image
    :return: r, t
    """
    # Load intrinsic parameter
    with np.load(calib_file_path + 'dist_para/5para.npz') as X:
        mtx, dist, _, _ = [X[i] for i in ('mtx', 'dist', 'rvecs', 'tvecs')]

    objp3D = np.delete(std3D, removed_idx_std,
                       axis=0)  # delete the points that are not selected by "GUI_Extract3DCoordinates.py"

    # find an object pose from 3D-2D point correspondences using the RANSAC scheme
    ret, rvecs, tvecs, inliers = cv2.solvePnPRansac(objp3D, point2f_std, mtx, dist,
                                                    useExtrinsicGuess=0, iterationsCount=100,
                                                    reprojectionError=8.0, flags=cv2.SOLVEPNP_EPNP)
    return rvecs, tvecs


# extract 3D coordinates from txt files
coordinates_left, idx_points_non_existed_left = extract_3d(coordinates3D_std_left, len_left)
coordinates_left2, idx_points_non_existed_left2 = extract_3d(coordinates3D_std_left2, len_left2)
coordinates_right, idx_points_non_existed_right = extract_3d(coordinates3D_std_right, len_right)
coordinates_right2, idx_points_non_existed_right2 = extract_3d(coordinates3D_std_right2, len_right2)

# preprocess 4 standard images, delete the points that don't have a pre-defined 3D coordinate
pool = ThreadPool(processes=4)
async_res_left = pool.apply_async(feature_matching_preprocess,(left_car, idx_points_non_existed_left))
async_res_right = pool.apply_async(feature_matching_preprocess,(right_car, idx_points_non_existed_right))
async_res_left2 = pool.apply_async(feature_matching_preprocess,(left2_car, idx_points_non_existed_left2))
async_res_right2 = pool.apply_async(feature_matching_preprocess,(right2_car, idx_points_non_existed_right2))

val_left = async_res_left.get()
val_right = async_res_right.get()
val_left2 = async_res_left2.get()
val_right2 = async_res_right2.get()

picked_pts_std1, removed_idx_std1, keypoints_std1 = val_left[0], val_left[1], val_left[2]
picked_pts_std2, removed_idx_std2, keypoints_std2 = val_right[0], val_right[1], val_right[2]
picked_pts_std3, removed_idx_std3, keypoints_std3 = val_left2[0], val_left2[1], val_left2[2]
picked_pts_std4, removed_idx_std4, keypoints_std4 = val_right2[0], val_right2[1], val_right2[2]

# get r & t from car's base position to cam
rvecs_std1, tvecs_std1 = get_r_t_carbase2cam(left_clb, coordinates_left, removed_idx_std1, picked_pts_std1)
rvecs_std2, tvecs_std2 = get_r_t_carbase2cam(right_clb, coordinates_right, removed_idx_std2, picked_pts_std2)
rvecs_std3, tvecs_std3 = get_r_t_carbase2cam(left2_clb, coordinates_left2, removed_idx_std3, picked_pts_std3)
rvecs_std4, tvecs_std4 = get_r_t_carbase2cam(right2_clb, coordinates_right2, removed_idx_std4, picked_pts_std4)

print('Done.\n')
