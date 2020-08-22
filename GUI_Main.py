"""
This program contains the GUI of the dof6 calculator. Once the 'Start' button
is pressed, a TCP server will be created. The server will keep listening for
the instructions from the client. The client program is "client.py".

Once the connection is built:
    if the client send 'light on' and the light brightness, the GUI will turn on the light;
    if the client send 'light off', the GUI will turn off the light;
    if the client sends 'compute', the GUI will compute the dof6;
    if the client sends 'save', the GUI will save the log file;
    if the client sends 'disconnect', the GUI will disconnect from the client.

Note: For simplicity, camera1 = camera left; camera2 = camera right;
      camera3 = camera left2; camera4 = camera right2

Author: Siqi Dai
"""


import socket
import logging
import glob
import os, sys
import statistics
import time
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext as st
import tkinter.filedialog as fd
import shutil
from PIL import Image, ImageTk
from FeatureMatchingPreprocess import *
from FeatureMatching import feature_matching
from Compute6DOF import compute_dof
from LightControl import *


def retrieve_img(dir, fn):
    img_set = glob.glob(dir + '*.bmp')
    for img in img_set:
        img = img.replace("\\", "/")
        if img != dir + fn_std:
            os.remove(img)
    img_set = glob.glob(dir + 'all/' + '*.bmp')
    img_set = sorted(img_set)
    for img in img_set:
        img = img.replace("\\", "/")
        if img == dir + 'all/' + fn:
            shutil.copy(img, dir+fn)
            return


def open_4_img():
    """
    This function gets the paths of the images taken by the four cameras
    """
    global address_list
    # img_test = '3.bmp'
    img_test = fn_new

    # retrieve_img(left_car, img_test)
    # retrieve_img(left2_car, img_test)
    # retrieve_img(right_car, img_test)
    # retrieve_img(right2_car, img_test)

    path1 = left_car + img_test
    path2 = right_car + img_test
    path3 = left2_car + img_test
    path4 = right2_car + img_test
    address_list = [path1, path2, path3, path4]


def show_image(path, canvas):
    """
    This function resizes the image and display the image in the specified placeholder
    :param path: image path
    :param canvas: canvas name
    """
    global width, height
    im = Image.open(path)
    resized = im.resize((width, height), Image.ANTIALIAS)
    tkimage = ImageTk.PhotoImage(resized)
    myvar = Label(root, image=tkimage, height=height, width=width)
    myvar.image = tkimage
    canvas.create_image(0, 0, image=tkimage, anchor=NW)


def select_file():
    """
    This function is used to let the user select a log file.
    The file path will be filled in the entry box automatically.
    """
    select.delete(0, END)
    fn = fd.askopenfilename(filetypes=[("Log File", '.log')])
    select.insert(0, fn)


def get_cam_ip(cam_ip_txt):
    """
    This function retrieves the ip addresses of four cameras from a txt file.
    The format of the txt file should be as follows:
        Cam L : 192.168.2.2
        Cam R : 192.168.2.3
        Cam L2: 192.168.2.4
        Cam R2: 192.168.2.5
    """
    ips = []
    file = open(cam_ip_txt)
    contents = file.readlines()
    for i in range(len(contents)):
        ips.append(contents[i][8:19])
    return ips


def get_calib_error(calib_dir):
    """
    This function retrieves the average calibration error of four cameras
    :param calib_dir: directory of calibration images
    """
    with np.load(calib_dir + "dist_para/5para.npz") as data:
        error = np.round(float(data['error']), 4)

    # if error > threshold: the calibration results may not be satisfying
    # this value can be changed according to the requirements
    fg = "red" if error >= calib_error_thresh else "green"
    return str(error), fg


def process_results(l_unfiltered, num_used_points_unfiltered, total_feature_points_unfiltered):
    """
    This function processes a set of returned results to get a final accurate output.
    Outlier deletion and weighted summation are used
    :param l_unfiltered: include four 1-DOF values returned by four cameras. e.g: [x1, x2, x3, x4], [y1, y2, y3, y4], etc.
    :param num_used_points_unfiltered: include four values, each is the number of inliers on the image
    :param total_feature_points_unfiltered: include four values, each is the total number of points on the image
    """
    # step 1: filter out obvious abnormal data
    l, num_used_points, total_feature_points = [], [], []
    for j in range(len(l_unfiltered)):
        if l_unfiltered[j] != float('inf'):  # float('inf') indicates solvePnP() doesn't have enough inputs; the value will be ignored
            # save the normal values in respective lists
            l.append(l_unfiltered[j])
            num_used_points.append(num_used_points_unfiltered[j])
            total_feature_points.append(total_feature_points_unfiltered[j])

    # step 2: calculate z-scores and delete potential outliers
    if len(l) == 0:  # if there's no normal value
        return -9999
    thresh = 1  # if z-score > thresh, the value will be recognized as an outlier and will be ignored
    avg = sum(l) / len(l)  # average
    std_dev = statistics.stdev(l)  # standard deviation
    normal, used_points, total_points = [], [], []
    for j in range(len(l)):
        z_score = np.round((l[j] - avg) / (std_dev + 1e-5), 2)  # calculate z-score
        if abs(z_score) < thresh:
            # save the normal values in respective lists
            normal.append(l[j])
            used_points.append(num_used_points[j])
            total_points.append(total_feature_points[j])

    # step 3: according to the number of points used by each camera, calculate the weighted sum as the final output
    weight = [i / j for i, j in zip(used_points, total_points)]
    weight_normalized = [i / sum(weight) for i in weight]
    ans = [i * j for i, j in zip(weight_normalized, normal)]
    return np.round(sum(ans), 3)


def process_error_msg(error1, error2, error3, error4):
    """
    This function processes and shows error messages returned by four cameras
    :param error1: a list of errors return by camera 1
    :param error2: a list of errors return by camera 2
    :param error3: a list of errors return by camera 3
    :param error4: a list of errors return by camera 4
    """
    errors = error1 + error2 + error3 + error4  # combine all the error messages and display them on the GUI
    if len(errors) == 0:
        error_msgs = "Normal"
        status_label.config(text=error_msgs, fg="green")
        l1.config(bg="green"); l2.config(bg="green"); l3.config(bg="green"); l4.config(bg="green")
    else:
        error_msgs = "*** Warnings ***\n"
        if error1:
            l1.config(bg="red")
            error_msgs += 'camera 1:\n'
            for i in error1:
                error_msgs += i + "\n"
        else:
            l1.config(bg="green")
        if error2:
            l2.config(bg="red")
            error_msgs += 'camera 2:\n'
            for i in error2:
                error_msgs += i + "\n"
        else:
            l2.config(bg="green")
        if error3:
            l3.config(bg="red")
            error_msgs += 'camera 3:\n'
            for i in error3:
                error_msgs += i + "\n"
        else:
            l3.config(bg="green")
        if error4:
            l4.config(bg="red")
            error_msgs += 'camera 4:\n'
            for i in error4:
                error_msgs += i + "\n"
        else:
            l4.config(bg="green")
        status_label.config(text=error_msgs, fg="red")
    return error_msgs


def compute_for_1cam(feature_matching_param, compute_dof_param):
    """
    This function computes the dof6 values based on the image taken by a single camera
    :param feature_matching_param: parameters needed for feature_matching(), including idx_points_non_existed, fn, keypoints_std
    :param compute_dof_param: parameters needed for compute_dof(), including clb_file, car_file, coordinates3D, rvecs_std, tvecs_std
    """
    point2f_new, removed_idx_new, error_feature_matching = feature_matching(feature_matching_param[0],
                                                                            feature_matching_param[1],
                                                                            feature_matching_param[2])
    x, y, z, alpha, beta, gamma, inliers, objp3D, error_compute_dof = compute_dof(compute_dof_param[0],
                                                                                  compute_dof_param[1], removed_idx_new,
                                                                                  point2f_new, compute_dof_param[2],
                                                                                  compute_dof_param[3], compute_dof_param[4])
    error_msgs = error_feature_matching + error_compute_dof
    return x, y, z, alpha, beta, gamma, inliers, objp3D, error_msgs


def compute_for_4cams():
    """
    This function computes dof6 based on the images taken by four cameras. The results returned by
    the method 'compute_for_1cam()' will be combined.
    """
    global address_list, num_cars
    start = time.time()
    open_4_img()
    # keep track of total number of cars
    num_cars += 1
    num_cars_label.config(text=str(num_cars))
    fn1, fn2, fn3, fn4 = address_list[0], address_list[1], address_list[2], address_list[3]
    # parameters needed for the method "feature_matching()"
    feature_matching_params = [[idx_points_non_existed_left, fn1, keypoints_std1],
                               [idx_points_non_existed_right, fn2, keypoints_std2],
                               [idx_points_non_existed_left2, fn3, keypoints_std3],
                               [idx_points_non_existed_right2, fn4, keypoints_std4]]
    # parameters needed for the method "compute_dof()"
    compute_dof_params = [[left_clb, left_car, coordinates_left, rvecs_std1, tvecs_std1],
                          [right_clb, right_car, coordinates_right, rvecs_std2, tvecs_std2],
                          [left2_clb, left2_car, coordinates_left2, rvecs_std3, tvecs_std3],
                          [right2_clb, right2_car, coordinates_right2, rvecs_std4, tvecs_std4]]

    # use multiprocessing for compute_for_single_cam() to speed up
    pool = ThreadPool(processes=3)
    async_res_left = pool.apply_async(compute_for_1cam, (feature_matching_params[0], compute_dof_params[0]))
    async_res_right = pool.apply_async(compute_for_1cam, (feature_matching_params[1], compute_dof_params[1]))
    async_res_left2 = pool.apply_async(compute_for_1cam, (feature_matching_params[2], compute_dof_params[2]))
    async_res_right2 = pool.apply_async(compute_for_1cam, (feature_matching_params[3], compute_dof_params[3]))
    val_left = async_res_left.get(); val_right = async_res_right.get(); val_left2 = async_res_left2.get(); val_right2 = async_res_right2.get()
    x1, y1, z1, alpha1, beta1, gamma1, inliers1, objp3D1, error1 = val_left[0], val_left[1], val_left[2], val_left[3], val_left[4], val_left[5], val_left[6], val_left[7], val_left[8]
    x2, y2, z2, alpha2, beta2, gamma2, inliers2, objp3D2, error2 = val_right[0], val_right[1], val_right[2], val_right[3], val_right[4], val_right[5], val_right[6], val_right[7], val_right[8]
    x3, y3, z3, alpha3, beta3, gamma3, inliers3, objp3D3, error3 = val_left2[0], val_left2[1], val_left2[2], val_left2[3], val_left2[4], val_left2[5], val_left2[6], val_left2[7], val_left2[8]
    x4, y4, z4, alpha4, beta4, gamma4, inliers4, objp3D4, error4 = val_right2[0], val_right2[1], val_right2[2], val_right2[3], val_right2[4], val_right2[5], val_right2[6], val_right2[7], val_right2[8]

    # display error messages if there's any
    error_msgs = process_error_msg(error1, error2, error3, error4)

    # store the returned results into respective lists
    x_list = [x1, x2, x3, x4]
    y_list = [y1, y2, y3, y4]
    z_list = [z1, z2, z3, z4]
    alpha_list = [alpha1, alpha2, alpha3, alpha4]
    beta_list = [beta1, beta2, beta3, beta4]
    gamma_list = [gamma1, gamma2, gamma3, gamma4]
    used_points = [inliers1, inliers2, inliers3, inliers4]  # number of inliers
    total_points = [objp3D1, objp3D2, objp3D3, objp3D4]  # total number of feature points on the image

    # process four sets of returned results and get a final 6-DOF output
    x = process_results(x_list, used_points, total_points)
    y = process_results(y_list, used_points, total_points)
    z = process_results(z_list, used_points, total_points)
    alpha = process_results(alpha_list, used_points, total_points)
    beta = process_results(beta_list, used_points, total_points)
    gamma = process_results(gamma_list, used_points, total_points)

    # display the result on the GUI
    tv.delete(*tv.get_children())
    tv.insert("", 0, "end", text="Line 1", values=(x, y, z, alpha, beta, gamma))

    # display and save four images with feature points marked
    path_l = left_car + "visual/" + os.path.basename(os.path.normpath(fn1)) if not error1 else left_car + "visual/error.bmp"
    path_r = right_car + "visual/" + os.path.basename(os.path.normpath(fn2)) if not error2 else right_car + "visual/error.bmp"
    path_l2 = left2_car + "visual/" + os.path.basename(os.path.normpath(fn3)) if not error3 else left2_car + "visual/error.bmp"
    path_r2 = right2_car + "visual/" + os.path.basename(os.path.normpath(fn4)) if not error4 else right2_car + "visual/error.bmp"

    img_l = cv2.imread(path_l); img_r = cv2.imread(path_r); img_l2 = cv2.imread(path_l2); img_r2 = cv2.imread(path_r2)

    text_l = "L: # inliers / # total points: " + str(inliers1) + "/" + str(objp3D1)
    text_r = "R: # inliers / # total points: " + str(inliers2) + "/" + str(objp3D2)
    text_l2 = "L2: # inliers / # total points: " + str(inliers3) + "/" + str(objp3D3)
    text_r2 = "R2: # inliers / # total points: " + str(inliers4) + "/" + str(objp3D4)

    img_l = cv2.putText(img_l, text_l, (25, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
    img_r = cv2.putText(img_r, text_r, (25, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 225), 3)
    img_l2 = cv2.putText(img_l2, text_l2, (25, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
    img_r2 = cv2.putText(img_r2, text_r2, (25, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    cv2.imwrite(path_l, img_l); cv2.imwrite(path_l2, img_l2); cv2.imwrite(path_r, img_r); cv2.imwrite(path_r2, img_r2)
    show_image(path_l, canvas1); show_image(path_r, canvas2); show_image(path_l2, canvas3); show_image(path_r2, canvas4)

    end = time.time()
    print('computation time:', end-start, 's\n')

    print('left:', x1, y1, z1, alpha1, beta1, gamma1)
    print('right:', x2, y2, z2, alpha2, beta2, gamma2)
    print('left2:', x3, y3, z3, alpha3, beta3, gamma3)
    print('right2:', x4, y4, z4, alpha4, beta4, gamma4)

    # display log
    write_log(x, y, z, alpha, beta, gamma, x_list, y_list, z_list, alpha_list, beta_list, gamma_list, error_msgs)
    root.update()


def server():
    """
    This function creates a TCP server by pressing the "start" button
    """
    HOST = 'localhost'  # standard loopback interface address for internal testing
    PORT = 65432  # port to listen on
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Listening for client ...')
    try:
        s.bind((HOST, PORT))
    except:
        pass
    s.listen()
    while True:
        conn, addr = s.accept()
        print('Connected with', addr)
        data = conn.recv(1024)
        if data == b'compute':
            global current_car
            car_model = conn.recv(1024)  # get the current car model
            if car_model.decode() == current_car:  # if the car model does not change, compute dof6 directly
                compute_for_4cams()
                conn.send(b'> DOF6 computation was completed.')
            else:   # if the car model changes, re-direct to another folder and re-preprocess the standard images
                save_log()
                conn.send(b'> Car model has changed. Exit. Log file was saved automatically.')
                exit()  # exit GUI
            current_car = car_model.decode()
            currCar.config(text=current_car)
            root.update()
        elif data == b'light on':
            brightness = int(conn.recv(1024).decode())  # decimal value of light brightness
            s = light_on(brightness)
            if s:
                conn.send(b'> Light was turned on.')
            else:
                conn.send(b'> RS232 connection failed.')
        elif data == b'light off':
            s = light_off()
            if s:
                conn.send(b'> Light was turned off.')
            else:
                conn.send(b'> RS232 connection failed.')
        elif data == b'save':
            save_log()
            conn.send(b'> Log file was saved.')
        elif data == b'disconnect':
            conn.send(b'> Disconnected from server. Press "Start" to re-connect.')
            break
        else:
            conn.send(b'> Not valid input. Try again.')
    print('break')
    s.close()


def write_log(x, y, z, alpha, beta, gamma, x_list, y_list, z_list, alpha_list, beta_list, gamma_list, error_msgs):
    """
    This function writes a log every time the dof6 values are computed.
    The log is displayed on the right panel of GUI
    """
    content = ""
    content += '<' + time.asctime(time.localtime(time.time())) + ': Car ' + str(num_cars) + '>\n'  # time and car number
    content += '  1) dof6-final: [' + str(x) + ', ' + str(y) + ', ' + str(z) + ', ' + str(alpha) + ', ' + str(beta) + ', ' + str(gamma) + ']\n'  # final answer
    content += '  2) dof6-cam1: [' + str(x_list[0]) + ', ' + str(y_list[0]) + ', ' + str(z_list[0]) + ', ' + str(alpha_list[0]) + ', ' + str(beta_list[0]) + ', ' + str(gamma_list[0]) + ']\n'  # answer from camera 1
    content += '  3) dof6-cam2: [' + str(x_list[1]) + ', ' + str(y_list[1]) + ', ' + str(z_list[1]) + ', ' + str(alpha_list[1]) + ', ' + str(beta_list[1]) + ', ' + str(gamma_list[1]) + ']\n'  # answer from camera 2
    content += '  4) dof6-cam3: [' + str(x_list[2]) + ', ' + str(y_list[2]) + ', ' + str(z_list[2]) + ', ' + str(alpha_list[2]) + ', ' + str(beta_list[2]) + ', ' + str(gamma_list[2]) + ']\n'  # answer from camera 3
    content += '  5) dof6-cam4: [' + str(x_list[3]) + ', ' + str(y_list[3]) + ', ' + str(z_list[3]) + ', ' + str(alpha_list[3]) + ', ' + str(beta_list[3]) + ', ' + str(gamma_list[3]) + ']\n'  # answer from camera 4
    content += '  6) car model: ' + current_car + '\n'
    content += '  7) status: ' + error_msgs + '\n==============================\n'
    logArea.insert(INSERT, content)


def save_log():
    """
    This function saves the log file. The filename is the date and time when the log is saved
    """
    fn = time.asctime(time.localtime(time.time())) + '.log'
    fn = fn.replace(":", "-")
    logging.basicConfig(filename=fn, level=logging.INFO)
    logging.info('\n' + logArea.get('1.0', END))


def delete_log(path):
    """
    This function deletes the log file. The user should enter the file path in the entry
    box and press the 'Delete Log' button
    """
    if os.path.isfile(path) == 1:
        os.remove(path)
        delete_label.config(text="The file was deleted.", fg="green")
    else:
        delete_label.config(text="The file doesn't exist.", fg="red")
    select.delete(0, END)



# ========== the design of user interface starts here ==========
"""
Note: For simplicity, camera1 = camera left; camera2 = camera right; camera3 = camera left2; camera4 = camera right2
"""
# global variables
current_car = os.path.basename(os.path.normpath(folder))  # keep track of current car model
address_list = []  # used to store paths of a maximum of 4 input images
width = 460  # width of the displayed image
height = 300  # height of the displayed image
l_r_panel_width = 300  # width of the left and right panel
ips = get_cam_ip(cam_ip_txt)  # IP addresses of four cameras (cam left, cam right, cam left2, cam right2)
num_cars = 0  # used to record the number of times  the start button is clicked
calib_error_thresh = 0.015  # if calib error >= threshold: the calibration results is not satisfying and will be marked red on the GUI


root = Tk()
root.title("DOF6 Calculator")
root.maxsize((l_r_panel_width+width)*2, int(height*3)-10)


# title frame
title_frame = Frame(root, bg="light grey")
title_frame.grid(row=0, column=1, columnspan=2, sticky="ew")
Label(title_frame, text='Camera Images', font=('Comic Sans MS', 15), bg="light grey").pack(fill=BOTH)


# left frame
left = Frame(root, width=l_r_panel_width, highlightthickness=1, highlightbackground="black")
left.grid(row=0, column=0, rowspan=4, sticky="nsew")
calib_error1, fg1 = get_calib_error(left_clb)
calib_error2, fg2 = get_calib_error(right_clb)
calib_error3, fg3 = get_calib_error(left2_clb)
calib_error4, fg4 = get_calib_error(right2_clb)
Label(left, text='Average Calibration Error (Pixels)', font=('Comic Sans MS', 15), bg="light grey").pack(fill=BOTH)
Label(left, text="Camera 1: "+calib_error1, font=('Comic Sans MS', 13), fg=fg1).pack()
Label(left, text="Camera 2: "+calib_error2, font=('Comic Sans MS', 13), fg=fg2).pack()
Label(left, text="Camera 3: "+calib_error3, font=('Comic Sans MS', 13), fg=fg3).pack()
Label(left, text="Camera 4: "+calib_error4, font=('Comic Sans MS', 13), fg=fg4).pack()
Label(left, text='Total Number of Cars', font=('Comic Sans MS', 15), bg="light grey").pack(fill=BOTH)
num_cars_label = Label(left, text="0", font=('Comic Sans MS', 13), fg='green')
num_cars_label.pack()
Label(left, text='Current Car Model', font=('Comic Sans MS', 15), bg="light grey").pack(fill=BOTH)
currCar = Label(left, text="", font=('Comic Sans MS', 13), fg='green')
currCar.pack()
Label(left, text='Program Status', font=('Comic Sans MS', 15), bg="light grey").pack(fill=BOTH)
status_label = Label(left, text="", font=('Comic Sans MS', 13), fg="green", wraplengt=250)
status_label.pack()
load = Image.open("UI_logo/ABB_logo.png")
resized = load.resize((225, 90), Image.ANTIALIAS)
tkimage = ImageTk.PhotoImage(resized)
img = Label(left, image=tkimage)
img.image = tkimage
img.place(x=0, y=670)


# middle-left frame
middleL = Frame(root, width=width)
middleL.grid(row=1, column=1, rowspan=2, sticky="w")
l1 = Label(middleL, text="Camera01 IP: "+ips[0], font=('Comic Sans MS', 11), background="green")
l1.pack(fill=BOTH)
canvas1 = Canvas(middleL, width=width, height=height, highlightthickness=1.2, highlightbackground="black", bg="light yellow")
canvas1.pack()
l3 = Label(middleL, text="Camera03 IP: "+ips[2], font=('Comic Sans MS', 11), background="green")
l3.pack(fill=BOTH)
canvas3 = Canvas(middleL, width=width, height=height, highlightthickness=1.2, highlightbackground="black", bg="light yellow")
canvas3.pack()


# middle-right frame
middleR = Frame(root, width=width)
middleR.grid(row=1, column=2, rowspan=2, sticky="w")
l2 = Label(middleR, text="Camera02 IP: "+ips[1], font=('Comic Sans MS', 11), background="green")
l2.pack(fill=BOTH)
canvas2 = Canvas(middleR, width=width, height=height, highlightthickness=1.2, highlightbackground="black", bg="light yellow")
canvas2.pack()
l4 = Label(middleR, text="Camera04 IP: "+ips[3], font=('Comic Sans MS', 11), background="green")
l4.pack(fill=BOTH)
canvas4 = Canvas(middleR, width=width, height=height, highlightthickness=1.2, highlightbackground="black", bg="light yellow")
canvas4.pack()


# right frame
right = Frame(root, width=l_r_panel_width, highlightthickness=1, highlightbackground="black")
right.grid(row=0, column=3, rowspan=4, sticky="nsew")
Label(right, text='Log', font=('Comic Sans MS', 15), bg='light grey').pack(fill=BOTH)
logArea = st.ScrolledText(master=right, wrap=WORD, width=30, height=10)
logArea.pack(padx=10, pady=10, fill=BOTH, expand=True)
Label(right, text='              Delete Log             ', font=('Comic Sans MS', 15), bg="light grey").pack(fill=BOTH)
log_name = StringVar()
Button(right, text=" Select File ", font=('Comic Sans MS', 14), command=select_file).pack()
select = Entry(right, textvariable=log_name)
select.pack(fill=BOTH)
delete_label = Label(right, text="", font=('Comic Sans MS', 13), fg='green')
delete_label.pack()
Button(right, text=" Delete ", font=('Comic Sans MS', 14), command=lambda:delete_log(log_name.get())).pack()


# bottom frame
bottom = Frame(root, bg="white")
bottom.grid(row=3, column=1, columnspan=2, sticky="nsew")
Label(bottom, text='Press the button below to start the program:', font=('Comic Sans MS', 15)).pack()
# press the button to start the TCP server
Button(bottom, text=" Start ", command=server, font=('Comic Sans MS', 14)).pack()
tv = ttk.Treeview(bottom, height=1)
tv["columns"] = ('x', 'y', 'z', 'al', 'be', 'gam')
tv.column("#0", stretch=NO, width=5, anchor='center')
tv.column("x", anchor='center', width=80)
tv.column("y", anchor='center', width=80)
tv.column("z", anchor='center', width=80)
tv.column("al", anchor='center', width=80)
tv.column("be", anchor='center', width=80)
tv.column("gam", anchor='center', width=80)
tv.heading("x", text="x (mm)")
tv.heading("y", text="y (mm)")
tv.heading("z", text="z (mm)")
tv.heading("al", text="alpha (°)")
tv.heading("be", text="beta (°)")
tv.heading("gam", text="gamma (°)")
tv.pack()
ttk.Style().configure("Treeview", font=('Comic Sans MS', 12))


root.bind("<Escape>", exit)
root.mainloop()

