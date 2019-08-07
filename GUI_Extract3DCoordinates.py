"""
This program is an auxiliary tool to determine the 3D coordinates of the feature points on the car.
A standard image with labeld feature points is needed. The 3D coordinates will be saved into a txt file
in the folder "std_images_txt".

Note: 1. The user can select whichever points he/she wants using this program.
      2. Only the points selected by the user will eventually be used to compute dof-6.
      3. The user can click on the points on the image to retrieve its index without manually entering it.

Author: Siqi Dai
ABB
"""


from tkinter import *
from tkinter import ttk
import tkinter.filedialog as fd
from PIL import Image, ImageTk
from PreprocessStandardImages import point2f_std_left, point2f_std_left2, point2f_std_right, point2f_std_right2
from PathsAndParameters import num_points_model_bottom, num_points_model_left, num_points_model_right, cam_height, cam_width
import numpy as np
from PIL import Image


def select_img(r, c):
    """
    This function lets the user to select the image
    :param r: row
    :param c: column
    """
    global camera, car_side, canvas_width, canvas_height, car_cad_img_width, car_cad_img_height
    path = fd.askopenfilename(filetypes=[("Image File", '.bmp')])
    im = Image.open(path)
    resized = im.resize((canvas_width, canvas_height), Image.ANTIALIAS)
    if c == 0:
        e.delete(0, END)
        root.tkimage1 = ImageTk.PhotoImage(resized)
        img1 = canvas1.create_image((canvas_width/2, canvas_height/2), anchor='center', image=root.tkimage1)
        canvas1.bind("<Button 1>", get_idx_of_feature_point_left)
        if "left2" in path:
            camera = 1
            e.insert(0, str(len(point2f_std_left2)))
        elif "left" in path:
            camera = 0
            e.insert(0, str(len(point2f_std_left)))
        elif "right2" in path:
            camera = 3
            e.insert(0, str(len(point2f_std_right2)))
        else:  # "right" in path
            camera = 2
            e.insert(0, str(len(point2f_std_right)))

    elif c == 1:
        car_cad_img_width, car_cad_img_height = im.size
        root.tkimage2 = ImageTk.PhotoImage(resized)
        img2 = canvas2.create_image((canvas_width/2, canvas_height/2),anchor='center', image=root.tkimage2)
        canvas2.bind("<Button 1>", get_idx_of_feature_point_right)

        if '0.bmp' in path:
            car_side = 0  # bottom
        elif '1.bmp' in path:
            car_side = 1   # left
        else:
            car_side = 2  # right

    x = tv.get_children()
    for item in x:
        t = tv.item(item, "values")
        tv.delete(item)


def input_int():
    """
    This function lets the user input the total number of feature points on the graph
    """
    global camera
    if camera == 0:
        num = len(point2f_std_left)
    elif camera == 1:
        num = len(point2f_std_left2)
    elif camera == 2:
        num = len(point2f_std_right)
    elif camera == 3:
        num = len(point2f_std_right2)
    else:
        num = var.get()
    insert_into_treeview(num)


def insert_into_treeview(num):
    """
    This function initializes a treeview
    :param num: number of the feature points on the image
    """
    x = tv.get_children()
    for item in x:
        tv.delete(item)

    for i in range(int(num)):
        if (i % 2) == 0:
            tv.insert("", "end", values=(str(i)),tags=('oddrow',))
        else:
            tv.insert("", "end", values=(str(i)),tags=('evenrow',))
        tv.tag_configure('oddrow', background='white')
        tv.tag_configure('evenrow', background='lavender')


def insert_into_treeview_entry2(std, new):
    """
    This function inputs a pair of indices into the tree view
    :param std: index on the standard image
    :param new: index on the new image
    """
    x = tv.get_children()
    for item in x:
        t = tv.item(item, "values")
        if int(t[0]) == int(std):
            tv.item(item, values=(std, new))
            break


def input_int_2entries():
    """
    This function lets the user to input a pair of corresponding indices
    """
    idx_std = var2.get()
    idx_new = var3.get()
    insert_into_treeview_entry2(idx_std, idx_new)
    x1.delete(0, END)
    x2.delete(0, END)


def generate_txt():
    """
    This function generates a txt file of a specific format
    """
    idx_new_list, idx_std_list = [], []
    x = tv.get_children()
    for item in x:
        t = tv.item(item, "values")
        if len(t) == 2 and t[1] != "":
            idx_std_list.append(int(t[1]))
            idx_new_list.append(int(t[0]))

    path1 = "std_images_txt/generated_bottom.txt"
    path2 = "std_images_txt/generated_left.txt"
    path3 = "std_images_txt/generated_right.txt"

    if int(v_radiobutton.get()) == 0:  # bottom
        writetxt(path1, idx_std_list, idx_new_list, 0, num_points_model_bottom)
    elif int(v_radiobutton.get()) == 1:  # left side
        writetxt(path2, idx_std_list, idx_new_list, 1, num_points_model_left)
    else:  # right side
        writetxt(path3, idx_std_list, idx_new_list, 2, num_points_model_right)


def get_idx_of_feature_point_left(event):
    """
    This function provides the user with the index of the point being clicked on the left image
    """
    global camera, canvas_width, canvas_height
    if camera == 0:  # left
        point_list = point2f_std_left
    elif camera == 1:  # left2
        point_list = point2f_std_left2
    elif camera == 2:  # right
        point_list = point2f_std_right
    else:  # right2
        point_list = point2f_std_right2
    x = event.x * (cam_width/canvas_width)
    y = event.y * (cam_height/canvas_height)
    for i in range(len(point_list)):
        x_std = point_list[i][0][0]
        y_std = point_list[i][0][1]
        if (x-15) <= x_std <= (x+15) and (y-15) <= y_std <= (y+15):
            x1.delete(0, END)
            x1.insert(0, str(i))

            tv_child = tv.get_children()
            for item in tv_child:
                t = tv.item(item, "values")
                if int(t[0]) == i:
                    x2.delete(0, END)
                    x2.insert(0, t[1])


def get_idx_of_feature_point_right(event):
    """
    This function provides the user with the index of the point being clicked on the right image
    """
    global car_side, car_cad_img_width, car_cad_img_height, canvas_width, canvas_height

    if car_side == 0:
        numofFeatures = num_points_model_bottom
        file = open('std_images_txt/0_2D_points.txt', 'r')
    elif car_side == 1:
        numofFeatures = num_points_model_left
        file = open('std_images_txt/1_2D_points.txt', 'r')
    else:
        numofFeatures = num_points_model_right
        file = open('std_images_txt/2_2D_points.txt', 'r')

    contents = file.readlines()

    coordinates = np.zeros((numofFeatures+1, 2))
    m = []
    for i in range(len(contents)):
        if contents[i][0] == '=':
            ptIndex = int(contents[i+1])
            x1 = int(contents[i+2][3:])
            y1 = int(contents[i+3][3:])
            coordinates[ptIndex, :] = x1, y1
            m.append(ptIndex)
    file.close()

    x = event.x * (car_cad_img_width/canvas_width)
    y = event.y * (car_cad_img_height/canvas_height)
    for i in range(len(coordinates)):
        x_std = coordinates[i][0]
        y_std = coordinates[i][1]
        if (x - 15) <= x_std <= (x + 15) and (y - 15) <= y_std <= (y + 15):
            x2.delete(0, END)
            x2.insert(0, str(i))


def clear_new_idx():
    """
    This function lets the user to delete a pair of indices
    """
    num = var4.get()
    x3.delete(0, END)
    x = tv.get_children()
    for item in x:
        t = tv.item(item, "values")
        if int(t[0]) == int(num):
            tv.item(item, values=(int(num), ""))
            break


def writetxt(fn, a, newa, num, total_num_points):
    """
    This function is used to generate a txt file with the 3D coordinates of the feature points on the image
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

    :param: fn - name of the txt file to be generated
    :param: a - list of indices of points on the std image
    :param: newa - list of indices of points on the image to be tested (note: the order of the indices must match the order of the indices in the list "a")
    :param: num - there are three choices for this parameter: 0, 1, and 2.
            if num is 0, the image of the bottom of the car model will be used as the standard image;
            if num is 1, the image of the left side of the car model will be used as the standard image;
            if num is 2, the image of the right side of the car model will be used as the standard image
    :param: total_num_points: total number of points recorded in the txt file
    """
    if num == 0:
        file = open('std_images_txt/0.txt', 'r')
    elif num == 1:
        file = open('std_images_txt/1.txt', 'r')
    else:
        file = open('std_images_txt/2.txt', 'r')
    contents = file.readlines()

    coordinates = np.zeros((total_num_points+1, 3))
    m = []
    for i in range(len(contents)):
        if contents[i][0] == '=':
            ptIndex = int(contents[i+1])
            x1 = float(contents[i+2][9:-3])
            y1 = float(contents[i+3][9:-3])
            z1 = float(contents[i+4][9:-3])
            coordinates[ptIndex, :] = x1, y1, z1
            m.append(ptIndex)
    file.close()

    with open(fn, "w") as f_w:
        l = []
        for i in range(len(a)):
            if a[i] in m:
                num = ("%d" % newa[i])
                x = ("%.2f" % coordinates[a[i]][0])
                y = ("%.2f" % coordinates[a[i]][1])
                z = ("%.2f" % coordinates[a[i]][2])
                l += ['=================\n', str(num), '\nDelta X: ', str(x), 'mm\nDelta Y: ', str(y), 'mm\nDelta Z: ', str(z), 'mm\n']
        f_w.writelines(l)


# ========== main body starts here ==========
camera = None  # 0-left, 1-left2, 2-right, 3-right2
car_side = None  # 0-bottom side of car, 1-left side of car, 2-right side of car
car_cad_img_width, car_cad_img_height = None, None  # width and height of car's CAD image
canvas_width, canvas_height = 700, 500  # 930, 650 / 500, 400 width and height of canvas

root = Tk()
root.title("Extract 3D Coordinates")
root.minsize(1400, 700)  # 1860, 1000
titleLabel = Label(root,text='Extract 3D Coordinates',fg='steel blue',font=('Comic Sans MS', 15, 'bold'))
titleLabel.grid(row=0,column=0,columnspan=4)

new = Button(root,text=" Select Image to be Analyzed ... ",font=('Comic Sans MS', 12),command=lambda:select_img(1, 0))
new.grid(row=1,column=0,columnspan=2,sticky=W)
std = Button(root,text=" Select Standard Image ... ",font=('Comic Sans MS', 12),command=lambda:select_img(1, 1))
std.grid(row=1,column=1,sticky=W)

canvas1 = Canvas(width=canvas_width, height=canvas_height, bg='azure2', highlightthickness=1, highlightbackground="black")
canvas1.grid(row=2,column=0,sticky=W)
canvas2 = Canvas(width=canvas_width, height=canvas_height, bg='azure2', highlightthickness=1, highlightbackground="black")
canvas2.grid(row=2,column=1,sticky=W,columnspan=3)

Label(root, text="Total number of points detected on the image to be analyzed:",font=('Comic Sans MS', 12)).grid(row=3,column=0,sticky=E)
var = StringVar()
e = Entry(root,textvariable = var)
e.grid(row = 3, column = 1,sticky=W)
b = Button(root,text=" Enter ",font=('Comic Sans MS', 11),command=input_int)
b.grid(row=3,column=2,sticky=W)

tvframe = Frame(root)
tvframe.grid(row=4,rowspan=10,sticky=E)
tv = ttk.Treeview(tvframe, height=10)
tv["columns"] = ('Index (Car Image)','Index (CAD Image)')
tv.column("#0", stretch=NO, width=5, anchor='center')
tv.column("Index (Car Image)", anchor='center', width=350)
tv.column("Index (CAD Image)", anchor='center', width=350)
tv.heading( "Index (Car Image)", text="Index (Car Image)")
tv.heading( "Index (CAD Image)", text="Index (CAD Image)")
tv.grid(row=4, column=1)
ttk.Style().configure("Treeview",font=('Comic Sans MS',12))

scr = ttk.Scrollbar(root,orient='vertical',command=tv.yview)
tv.configure(yscrollcommand=scr.set)

Label(root,text="Idx (car):",font=('Comic Sans MS', 12)).grid(row=4,column=1,sticky=E)
Label(root,text="Idx (CAD):",font=('Comic Sans MS', 12)).grid(row=5,column=1,sticky=E)
var2, var3, var4 = StringVar(), StringVar(), StringVar()
x1 = Entry(root,textvariable = var2)
x1.grid(row=4, column=2,sticky=W)
x2 = Entry(root,textvariable = var3)
x2.grid(row=5, column=2,sticky=W)
b = Button(root, text=" Enter ",font=('Comic Sans MS', 11),command=input_int_2entries)
b.grid(row=6, column=2,sticky=W)
Label(root,text="Clear matching relationship for Idx (car):",font=('Comic Sans MS', 12)).grid(row=7, column=1, sticky=E)
x3 = Entry(root,textvariable = var4)
x3.grid(row=7, column=2, sticky=W)
delete = Button(root,text=" Clear ",font=('Comic Sans MS', 11),command=clear_new_idx)
delete.grid(row=8, column=2, sticky=W)

v_radiobutton = StringVar()
v_radiobutton.set(0)
Radiobutton(root,text="Bottom",variable=v_radiobutton,value=0,font=('Comic Sans MS', 12)).grid(row=9, column=1, sticky=E)
Radiobutton(root,text="Left Side",variable=v_radiobutton,value=1,font=('Comic Sans MS', 12)).grid(row=9, column=2)
Radiobutton(root,text="Right Side",variable=v_radiobutton,value=2,font=('Comic Sans MS', 12)).grid(row=9, column=3, sticky=W)

txt = Button(root,text=" Generate txt ",font=('Comic Sans MS', 11),command=generate_txt)
txt.grid(row=10, column=2, sticky=W)

root.mainloop()
