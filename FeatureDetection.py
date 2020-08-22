"""
This file contains a function that performs blob detection

Author: Xu Yang
Modified by: Siqi Dai
"""


import cv2
from multiprocessing.pool import ThreadPool
from PathsAndParameters import min_area, max_area


def feature_detection(image):
    """
    This function detects the circular features on a car model
    :param image: image to be analyzed
    :return: keypoints detected on the image
    """
    Param_dark = cv2.SimpleBlobDetector_Params()

    # parameter settings
    Param_dark.blobColor = 0
    detector_dark = cv2.SimpleBlobDetector_create(Param_dark)
    keypoints_dark = detector_dark.detect(image)

    return keypoints_dark
