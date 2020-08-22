"""
This program is used to preprocess the standard images before the GUI starts.
AKA: detects feature points and labels them.

All the detected feature points will be shown on the image saved in the folder
"car_xx/std_image/". This program will be called by "GUI_Extract3DCoordinates.py"
to let the user select feature points of interest.

Author: Siqi Dai
"""


import cv2
import os
from FeatureDetection import feature_detection
from PathsAndParameters import folder, fn_std, left_car, left2_car, right_car, right2_car
from multiprocessing.pool import ThreadPool
from FeatureMatching import show_label
import numpy as np


def preprocess(car_file_path):
    """
    This function detects feature points on the standard images and labels the feature points
    :param car_file_path: directory that stores the image of the car at its base position
    """
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

    newnum = [i for i in range(len(keypoints_std))]
    newnum = np.asarray(newnum)

    img_with_keypoints = cv2.drawKeypoints(img_std, keypoints_std, np.array([]), (0, 0, 255))  # draw keypoints
    img_with_label = show_label(img_with_keypoints, point2f_std, newnum, 1)  # draw label (indices of feature points)

    basename = os.path.basename(os.path.normpath(img_name_std))
    cv2.imwrite(os.path.join(path_std, basename), img_with_label)
    point2f_std = [[[i[0], i[1]]] for i in point2f_std]
    point2f_std = np.asarray(point2f_std)
    return point2f_std, len(point2f_std)


print('Preprocessing the standard images ...\n')
# use multiprocessing to speed up
pool = ThreadPool(processes=4)
async_res_left = pool.apply_async(preprocess, (left_car,))
async_res_right = pool.apply_async(preprocess, (right_car,))
async_res_left2 = pool.apply_async(preprocess, (left2_car,))
async_res_right2 = pool.apply_async(preprocess, (right2_car,))

val_left = async_res_left.get()
val_right = async_res_right.get()
val_left2 = async_res_left2.get()
val_right2 = async_res_right2.get()

point2f_std_left, len_left = val_left[0], val_left[1]
point2f_std_right, len_right = val_right[0], val_right[1]
point2f_std_left2, len_left2 = val_left2[0], val_left2[1]
point2f_std_right2, len_right2 = val_right2[0], val_right2[1]



