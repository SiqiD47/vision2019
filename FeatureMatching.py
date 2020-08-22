"""
This script finds the correspondences of a series of images. "1.bmp" is used as the standard image.
The key method Coherent Point Registration (cpd-register) used here is implemented in Myronenko A,
Song X. Point set registration: coherent point drift[J]. IEEE Transactions on Pattern Analysis &
Machine Intelligence, 2010, 32(12):2262-2275.

Modification: The cpd-register algorithm is improved by further filtering the matched points by
using the method matchfilter2().

Author: Xu Yang
Modified by: Hanhui Li
"""


from __future__ import (absolute_import, division, print_function, unicode_literals)
import os
import math
import numpy as np
import cv2
import numpy.matlib
from builtins import *
from FeatureDetection import feature_detection


def show_label(image, point2f, index, i):
    """
    This function labels the points in different colors on a given image
    :param image: image to be labeled on
    :param point2f: a list of 2D coordinates of the points
    :param index: a list of indices of the points
    :param i: indicate the color, 1 - blue; 2 - green; 3 - red
    """
    for idx in range(len(point2f)):
        point = point2f[idx]
        if i == 1:
            image = cv2.putText(image, str(index[idx]), tuple(point), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)  # blue
        elif i == 2:
            image = cv2.putText(image, str(index[idx]), tuple(point), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)  # green
        else:
            image = cv2.putText(image, str(index[idx]), tuple(point), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)  # red
    return image


"""
The following three functions re-implements the CPD algorithm using Python. They are modified 
based on the codes at GitHUb: https://github.com/Hennrik/Coherent-Point-Drift-Python.git.
"""

def cpd_p(x, y, sigma2, w, m, n, d):
    # using numpy broadcasting to build a new matrix.
    g = x[:, np.newaxis, :]-y
    g = g*g
    g = np.sum(g, 2)
    g = np.exp(-1.0/(2*sigma2)*g)
    # g1 is the top part of the expression calculating p
    # temp2 is the bottom part of expression calculating p
    g1 = np.sum(g, 1)
    temp2 = (g1 + (2*np.pi*sigma2)**(d/2)*w/(1-w)*(float(m)/n)).reshape([n, 1])
    p = (g/temp2).T
    p1 = (np.sum(p, 1)).reshape([m, 1])
    px = np.dot(p, x)
    pt1 = (np.sum(np.transpose(p), 1)).reshape([n, 1])
    return p1, pt1, px


def register_rigid(x, y, w, max_it=150):
    # get dataset lengths and dimensions
    [n, d] = x.shape
    [m, d] = y.shape

    # t is the updated moving shape, we initialize it with y first.
    t = y

    # initialize sigma^2
    sigma2 = (m*np.trace(np.dot(np.transpose(x), x))+n*np.trace(np.dot(np.transpose(y), y)) -
               2*np.dot(sum(x), np.transpose(sum(y))))/(m*n*d)
    iter = 0
    while iter < max_it and sigma2 > 10.e-8:
         [p1, pt1, px] = cpd_p(x, t, sigma2, w, m, n, d)

         # precompute
         Np = np.sum(pt1)
         mu_x = np.dot(np.transpose(x), pt1)/Np
         mu_y = np.dot(np.transpose(y), p1)/Np

         # solve for rotation, scaling, translation and sigma^2
         a = np.dot(np.transpose(px), y)-Np*(np.dot(mu_x, np.transpose(mu_y)))
         [u, s, v] = np.linalg.svd(a)
         s = np.diag(s)
         c = np.eye(d)
         c[-1, -1] = np.linalg.det(np.dot(u, v))
         r = np.dot(u, np.dot(c, v))
         scale = np.trace(np.dot(s, c))/(sum(sum(y*y*np.matlib.repmat(p1, 1, d)))-Np *
                                         np.dot(np.transpose(mu_y), mu_y))
         sigma22 = np.abs(sum(sum(x*x*np.matlib.repmat(pt1, 1, d)))-Np *
                          np.dot(np.transpose(mu_x), mu_x)-scale*np.trace(np.dot(s, c)))/(Np*d)
         sigma2 = sigma22[0][0]

         # ts is translation
         ts = mu_x-np.dot(scale*r, mu_y)
         t = np.dot(scale*y, np.transpose(r))+np.matlib.repmat(np.transpose(ts), m, 1)
         iter = iter+1
    return t


def compute_new2std_idx(x, y):
    xx, yy = [], []
    for i in range(len(x)):  # new image
        xx.append(x[i][0])  # x
        xx.append(x[i][1])  # y
    for i in range(len(y)):  # std image
        yy.append(y[i][0])  # x
        yy.append(y[i][1])  # y

    x = np.reshape(xx, (len(x), 2))  # new
    y = np.reshape(yy, (len(y), 2))  # std
    y_new = register_rigid(x, y, 0.0)  # std affined
    correspond_list = []
    for i in range(len(y_new)):
        distance_min = math.sqrt((y_new[i][0]-x[0][0])*(y_new[i][0]-x[0][0]) + (y_new[i][1]-x[0][1])*(y_new[i][1]-x[0][1]))
        idx_min = 0
        for j in range(len(x)):
            distance = math.sqrt((y_new[i][0]-x[j][0])*(y_new[i][0]-x[j][0]) + (y_new[i][1]-x[j][1])*(y_new[i][1]-x[j][1]))
            if distance <= distance_min:
                distance_min = distance
                idx_min = j
        correspond_list.append(idx_min)

    correspond_list = np.array(correspond_list)
    return correspond_list


def dist(a):
    """
    This function computes the Euclidean distance for every pair of points
    """
    dists = []
    for i in range(a.shape[0]):
        dist1 = 10000  # the nearest point
        dist2 = 9999  # the second nearest point
        index1 = 0  # index of the nearest point
        index2 = 0  # index of the second nearest point
        for j in range(a.shape[0]):
            if i != j:
                dist = np.linalg.norm(a[i] - a[j])
                if dist < dist1:
                    dist2 = dist1
                    dist1 = dist
                    index2 = index1
                    index1 = j

                elif dist1 <= dist < dist2:
                    dist2 = dist
                    index2 = j
        dists.append([index1, index2])
    return dists


def matchfilter2(point2f_std, point2f_new_as_std, PARM=1):
    """
    This function improves the cpd feature matching algorithm. It filters the matching points given by
    the cpd algorithm and deleted the points that may not be correctly matched
    :param point2f_std: feature points on the standard image
    :param point2f_new_as_std: feature points on the new image corresponding to those on the standard image
    """
    temp = point2f_new_as_std.copy()
    error_label = []
    numnew = np.array(range(temp.shape[0]))
    for i in range(temp.shape[0]):
        if np.where(temp == temp[i])[0].shape[0] != 2:
            temp[i] = (0, 0)
            error_label.append(i)

    dist_std = dist(point2f_std)
    dist_new = dist(point2f_new_as_std)

    if PARM == 1:  # compare the closest point
        for i in range(temp.shape[0]):
            if dist_std[i][0] != dist_new[i][0]:
                temp[i] = (0, 0)
                error_label.append(i)
    elif PARM == 2:  # compare both the closest and the second closest points
        for i in range(temp.shape[0]):
            if dist_std[i] != dist_new[i]:
                temp[i] = (0, 0)
                error_label.append(i)

    numnew = np.array(numnew)
    point2f_new_as_std = np.delete(point2f_new_as_std, error_label, 0)
    # "newnum" is an array of # indices of points that are correctly matched in the new image
    numnew = np.delete(numnew, error_label, 0)

    return point2f_new_as_std, numnew


def feature_matching(idx_points_non_existed, fname, keypoints_std):
    """
    This function applies the above methods and performs feature matching
    :param idx_points_non_existed: index of points on the standard image that cannot be matched with those on the new image
    :param fname: filename of the new image
    :param keypoints_std: keypoints on the standard image
    """
    error_msg = []  # a list used to store error messages
    fname = fname.replace("\\", "/")

    # read images
    if os.path.exists(fname):
        img_new = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
    else:
        e = "'" + fname + "' cannot be read."
        error_msg.append(e)
        return None, None, None, error_msg

    # detect features
    keypoints_new = feature_detection(img_new)

    point2f_std = cv2.KeyPoint_convert(keypoints_std)
    point2f_new = cv2.KeyPoint_convert(keypoints_new)

    # perform feature matching
    x = point2f_new.tolist()
    y = point2f_std.tolist()

    # compute new_points and std_points
    new2std_index = compute_new2std_idx(x, y)
    point2f_new_as_std = point2f_new[new2std_index, :]
    point2f_new_as_std_cp, newnum = matchfilter2(point2f_std,point2f_new_as_std, PARM=1)
    point2f_new_as_std = [[x.tolist()] for x in point2f_new_as_std]
    point2f_new_as_std = np.array(point2f_new_as_std)

    idx_all_points = [i for i in range(len(point2f_new_as_std))]  # indices of all points
    idx_to_pick = list(set(newnum.tolist()) - set(idx_points_non_existed))  # indices of points selected by "GUI_Extract3DCoordinates.py"
    idx_to_remove = list(set(idx_all_points) - set(idx_to_pick))  # indices of points not selected by "GUI_Extract3DCoordinates.py"
    point2f_new_as_std_final = np.delete(point2f_new_as_std, idx_to_remove, axis=0)  # 2D coords of points selected by "GUI_Extract3DCoordinates.py"

    return point2f_new_as_std_final, idx_to_remove, error_msg
