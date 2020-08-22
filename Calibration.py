"""
Camera calibration program.

Intrinsic parameters of the cameras will be obtained and saved.
An executable file Calibration.exe was generated from this program.
The user can run it directly and do the calibration by following
the instructions on the user interface.

Four cameras will be calibrated at the same time.

Author: Zhongyi Zhou
Modified by: Siqi Dai
"""


from tkinter import *
from tkinter import ttk
import tkinter.filedialog as fd
import tkinter.scrolledtext as st
import numpy as np
import cv2
import glob
import os
import shutil
import time
from multiprocessing.pool import ThreadPool


def save5para(ret, mtx, dist, rvecs, tvecs, error, savedir):
    """
    This function saves 5 intrinsic parameters of the camera
    :param ret: retvalue
    :param mtx: intrinsic camera matrix
    :param dist: distortion coefficients
    :param rvecs: rotation matrix
    :param tvecs: translation matrix
    :param error: average calibration error
    :param savedir: path of the .npz file
    """
    if os.path.exists(savedir+"dist_para/") == 0:
        os.makedirs(savedir+"dist_para/")
    np.savez(savedir+"dist_para/5para.npz", ret=ret, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs, error=error)


def save_image(dirname, filename, img):
    """
    This function saves the image to a designated directory
    """
    if os.path.exists(dirname) == 0:
        os.makedirs(dirname)
    cv2.imwrite(dirname+filename+".bmp", img)


def dist_train(imgdir, imgfmt):
    """
    This function obtains the intrinsic parameters from the calibration images
    :param imgdir: directory of calibration images
    :param imgfmt: format of calibration images
    :return: camera parameters: retvalue, internal matrix, distortion coefficient array, rvecs, tvecs, average error
    """
    global square_width, row, col, content
    counter, loop_ctr = 0, 1

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, square_width, 0.001)

    # arrays to store object points and image points from all the images
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane
    images = glob.glob(imgdir+'*'+imgfmt)
    images.sort()

    gray = np.zeros((0, 0))
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        objp = np.zeros((row*col, 3), np.float32)
        objp[:, :2] = np.mgrid[0:row, 0:col].T.reshape(-1, 2)
        ret, corners = cv2.findChessboardCorners(gray, (row, col), None)

        # if chessboard corners are found, add object points and image points to respective lists (after refining them)
        ind_line = fname.rindex(os.sep)
        ind_dot = fname.rindex('.')
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (row, col), corners2, ret)
            counter += 1
            save_image(fname[0:ind_line+1] + "success/", fname[ind_line+1:ind_dot],img)
        else:
            save_image(fname[0:ind_line + 1] + "fail/", fname[ind_line + 1:ind_dot], img)
        cv2.destroyAllWindows()
        loop_ctr += 1

    if len(images) > 0:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        # get the calibration error
        error = calib_error(objpoints, imgpoints, rvecs, tvecs, mtx, dist)
        content += imgdir + ':\n     Number of qualified images = ' + str(counter) + '\n     Average calibration error = ' + str(np.round(error, 4)) + ' pixels\n'
        return ret, mtx, dist, rvecs, tvecs, error
    else:
        content += imgdir + ':\n     No images in this folder. Cannot compute camera parameters.\n'
        return 0, 0, 0, 0, 0, float('inf')


def dist_main(traindir):
    """
    This function performs the calibration and saves the intrinsic parameters into an ".npz" file
    :param traindir: directory of the images to be calibrated
    """
    if os.path.exists(traindir + "success/") == 1:
        shutil.rmtree(traindir + "success/")
    if os.path.exists(traindir + "fail/") == 1:
        shutil.rmtree(traindir + "fail/")
    [ret, mtx, dist, rvecs, tvecs, error] = dist_train(traindir, '.bmp')
    save5para(ret, mtx, dist, rvecs, tvecs, error, traindir)
    return error


def calib_error(objpoints, imgpoints, rvecs, tvecs, mtx, dist):
    """
    This function gives a good estimation of just how exact is the found parameters. The value should
    be as close to zero as possible
    :param objpoints: 3D real world points of chessboard corners     
    :param imgpoints: 2D image points of chessboard corners
    :param rvecs: rotation vector
    :param tvecs: translation vector
    :param mtx: camera matrix
    :param dist: distortion coefficient
    :return: arithmetical mean of the errors for all the calibration images
    """
    tot_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        tot_error += error
    return tot_error / len(objpoints)  # calculate the arithmetic mean of the errors for all the calibration images


def calib_four_cams():
    global content, left_clb, right_clb, left2_clb, right2_clb, content
    start = time.time()

    # use multiprocessing to speed up
    pool = ThreadPool(processes=4)
    async_res_l = pool.apply_async(dist_main, (left_clb,))
    async_res_l2 = pool.apply_async(dist_main, (left2_clb,))
    async_res_r = pool.apply_async(dist_main, (right_clb,))
    async_res_r2 = pool.apply_async(dist_main, (right2_clb,))

    val_l = async_res_l.get()
    val_l2 = async_res_l2.get()
    val_r = async_res_r.get()
    val_r2 = async_res_r2.get()

    end = time.time()
    content += 'Total calibration time: ' + str(end-start) + ' s.\n'
    content += 'Intrinsic parameters were saved as ".npz" files in the respective folders.\n\n'
    logArea.insert(INSERT, content)
    content = ""


def enter():
    global left_clb, right_clb, left2_clb, right2_clb, square_width, row, col
    left_clb, right_clb, left2_clb, right2_clb = var1.get(), var2.get(), var3.get(), var4.get()
    square_width = int(var5.get())
    row = int(var6.get())
    col = int(var7.get())


def select_folder(cam):
    cam.delete(0, END)
    clb = fd.askdirectory() + '/'
    cam.insert(0, clb)


if __name__ == "__main__":
    # define global variables
    left_clb, right_clb, left2_clb, right2_clb = None, None, None, None  # directory of calibration images
    square_width = 0  # side length of a square on the chessboard (mm)  15mm
    row, col = 0, 0  # number of rows/cols on the chessboard 棋盘格行/列角点数 （24x23/11X8）

    root = Tk()
    root.title("Calibration UI")
    root.maxsize(1000, 800)
    content = ""

    titleframe = Frame(root)
    titleframe.grid(row=0, column=0, columnspan=3, sticky="ew")
    Label(titleframe, text='Calibration', font=('Comic Sans MS', 25, 'bold'), fg="dark blue").pack(fill=BOTH)
    Label(titleframe, text='\nEnter the required information:', font=('Comic Sans MS', 17), fg="dark blue").pack()

    leftframe = Frame(root)
    leftframe.grid(row=1, column=0, sticky="en")
    Label(leftframe, text='     Directory of images taken by Cam 1 :', font=('Comic Sans MS', 15)).pack(fill=BOTH)
    Label(leftframe, text='     Directory of images taken by Cam 2 :', font=('Comic Sans MS', 15)).pack(fill=BOTH)
    Label(leftframe, text='     Directory of images taken by Cam 3 :', font=('Comic Sans MS', 15)).pack(fill=BOTH)
    Label(leftframe, text='     Directory of images taken by Cam 4 :', font=('Comic Sans MS', 15)).pack(fill=BOTH)
    Label(leftframe, text='     Checkerboard square width (mm) :', font=('Comic Sans MS', 15)).pack(fill=BOTH)
    Label(leftframe, text='     Number of rows on checkerboard  :', font=('Comic Sans MS', 15)).pack(fill=BOTH)  # 棋盘格行角点
    Label(leftframe, text='     Number of columns on checkerboard:', font=('Comic Sans MS', 15)).pack(fill=BOTH)  # 棋盘格列角点

    midframe = Frame(root)
    midframe.grid(row=1, column=1, sticky="en")

    var1 = StringVar()
    cam1 = Entry(midframe, textvariable=var1, width=35)
    cam1.pack()
    var2 = StringVar()
    cam2 = Entry(midframe, textvariable=var2, width=35)
    cam2.pack()
    var3 = StringVar()
    cam3 = Entry(midframe, textvariable=var3, width=35)
    cam3.pack()
    var4 = StringVar()
    cam4 = Entry(midframe, textvariable=var4, width=35)
    cam4.pack()
    var5 = StringVar()
    squareW = Entry(midframe, textvariable=var5, width=35)
    squareW.pack()
    var6 = StringVar()
    numR = Entry(midframe, textvariable=var6, width=35)
    numR.pack()
    var7 = StringVar()
    numC = Entry(midframe, textvariable=var7, width=35)
    numC.pack()

    rightframe = Frame(root)
    rightframe.grid(row=1, column=2, sticky="wn")
    Button(rightframe, text=" Select ... ", command=lambda: select_folder(cam1), font=('Comic Sans MS', 15)).pack()
    Button(rightframe, text=" Select ... ", command=lambda: select_folder(cam2), font=('Comic Sans MS', 15)).pack()
    Button(rightframe, text=" Select ... ", command=lambda: select_folder(cam3), font=('Comic Sans MS', 15)).pack()
    Button(rightframe, text=" Select ... ", command=lambda: select_folder(cam4), font=('Comic Sans MS', 15)).pack()

    bottomframe = Frame(root)
    bottomframe.grid(row=2, column=0, columnspan=3, sticky="ew")
    Button(bottomframe, text=" Enter ", command=enter, font=('Comic Sans MS', 18)).pack()
    Label(bottomframe, text='\nPress the button below to start calibration:', font=('Comic Sans MS', 17), fg="dark blue").pack()
    Label(bottomframe, text='This may take some time depends on the size of the image set (~ 1 min)\n', font=('Comic Sans MS', 14)).pack()
    Button(bottomframe, text=" Start ", command=calib_four_cams, font=('Comic Sans MS', 18)).pack()
    Label(bottomframe, text='\nCalibration results:', font=('Comic Sans MS', 17), fg="dark blue").pack()
    logArea = st.ScrolledText(master=bottomframe, wrap=WORD, width=100, height=12, highlightthickness=1.5, highlightbackground="black")
    logArea.pack(padx=10, pady=10, fill=BOTH, expand=True)

    root.mainloop()


