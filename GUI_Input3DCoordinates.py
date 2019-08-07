"""
This program is an auxiliary tool to input the 3D coordinates of the points on a given image.
It should only be used when we change the car model. The 3D coordinates will be saved into a txt
file in the folder "std_images_txt".

The 2D coordinates of all the points will also be saved in another txt file. This file will be
used by "GUI_Extract3DCoordinates.py" so that the index of a point can be obtained once the
user clicks on it.

Author: Siqi Dai
ABB
"""


from tkinter import *
import tkinter.filedialog as fd
from PIL import Image, ImageTk


def select_img():
    """
    This function lets the user to select the image
    :param r: row
    :param c: column
    """
    path = fd.askopenfilename(filetypes=[("Image File", '.bmp')])
    im = Image.open(path)
    resized = im.resize((950, 500), Image.ANTIALIAS)
    root.tkimage = ImageTk.PhotoImage(resized)
    img1 = canvas1.create_image((475, 254), anchor='center',image=root.tkimage)
    canvas1.bind("<Button 1>", print_coords)


def input_int_3entries():
    """
    This function lets the user to input the 3D coordinates of a point
    """
    x = var2.get()
    y = var3.get()
    z = var4.get()
    coord = [idx-1,x,y,z]
    coord_list.append(coord)
    idx_label = Label(root, text = "Index "+str(idx-1)+" saved!").grid(row=6, column=1, sticky=W)
    x1.delete(0, END)
    y1.delete(0, END)
    z1.delete(0, END)


def print_coords(event):
    """
    This function prints the 2D coordinate of a point on the image
    """
    global idx, coord_list_2d
    id = ""
    for i in range(int(idx)):
        id = id+"a"
    canvas1.create_text((event.x, event.y), text=idx, font=("Comic Sans MS", 14, "bold"), fill='red', tag=id)
    idx_label = Label(root, text=str(idx)+"                          ").grid(row=6, column=1, sticky=W)
    coord_list_2d[idx] = (event.x, event.y)
    idx = idx + 1


def create_txt():
    """
    This function saves the 3D coordinates to a txt file of a specific format
    """
    global idx, x, y, z, coord_list, coord_list_2d
    filename = var5.get()
    with open(filename+".txt", "w") as f_w:  # store the 3D coordinates of the points
        l = []
        for i in range(len(coord_list)):
            coord = coord_list[i]
            num = ("%d" % int(coord[0]))
            x = ("%.2f" % float(coord[1]))
            y = ("%.2f" % float(coord[2]))
            z = ("%.2f" % float(coord[3]))
            l += ['=================\n', str(num), '\nDelta X: ', str(x), 'mm\nDelta Y: ', str(y), 'mm\nDelta Z: ',
                  str(z), 'mm\n']
        f_w.writelines(l)
        f_w.close()

    with open(filename+'_2D_points.txt', "w") as f_w:  # store the 2D coordinates of the points on the image
        l = []
        for num in coord_list_2d.keys():
            x = coord_list_2d[num][0]
            y = coord_list_2d[num][1]
            l += ['=================\n', str(num), '\nX: ', str(x), '\nY: ', str(y), '\n']
        f_w.writelines(l)
        f_w.close()

    print(filename, 'successfully saved!')

    idx = 1
    coord_list = []


def clear_index():
    """
    This function lets the user delete the 3D coordinates of a point
    """
    global coord_list, coord_list_2d, idx
    index = var6.get()

    if coord_list_2d.get(int(index)): del coord_list_2d[int(index)]

    if int(index) < idx:
        tag = ""
        for i in range(int(index)):
            tag += "a"
        canvas1.delete(tag)

    flag = 0
    if len(coord_list) >= 1:
        for coord in coord_list:
            if int(index) == int(coord[0]):
                flag = 1
                coord_to_be_removed = coord
                break
        if flag == 1:
            coord_list.remove(coord_to_be_removed)
    idx_clear.delete(0, END)


# ========== main body starts here ==========
idx = 1
coord_list = []  # list to store 3D coordinates
coord_list_2d = {}  # dictionary to store point indices and their corresponding 2D coordinates

root = Tk()
root.title("Input 3D Coordinates")
root.minsize(960, 800)
titleLabel = Label(root, text='Input 3D Coordinates',fg='steel blue',font=('Comic Sans MS', 15, 'bold'))
titleLabel.grid(row=0, column=0, columnspan=2)

img = Button(root,text=" Select Image ... ",font=('Comic Sans MS', 12), command=lambda :select_img())
img.grid(row=1,column=0, sticky=W)

canvas1 = Canvas(width=960, height=500, bg='azure2', highlightthickness=1, highlightbackground="black")
canvas1.grid(row=2,column=0, columnspan=2)

Label(root, text="Index:", font=('Comic Sans MS', 12)).grid(row=6, column=0, sticky=E)
Label(root, text="X:", font=('Comic Sans MS', 12)).grid(row=7, column=0, sticky=E)
Label(root, text="Y:", font=('Comic Sans MS', 12)).grid(row=8, column=0, sticky=E)
Label(root, text="Z:", font=('Comic Sans MS', 12)).grid(row=9, column=0, sticky=E)
Label(root, text="File Name:", font=('Comic Sans MS', 12)).grid(row=13, column=0, sticky=E)
Label(root, text="Clear Index:", font=('Comic Sans MS', 12)).grid(row=11, column=0, sticky=E)
idx_label=Label(root, text=" ").grid(row=6, column=1, sticky=W)
var2 = StringVar()
x1=Entry(root,textvariable=var2)
x1.grid(row=7, column=1, sticky=W)
var3 = StringVar()
y1=Entry(root,textvariable=var3)
y1.grid(row=8, column=1, sticky=W)
var4 = StringVar()
z1=Entry(root,textvariable=var4)
z1.grid(row=9, column=1, sticky=W)
var5 = StringVar()
Entry(root,textvariable=var5).grid(row=13, column=1, sticky=W)
var6 = StringVar()
idx_clear = Entry(root, textvariable=var6)
idx_clear.grid(row=11, column=1, sticky=W)

b = Button(root, text=" Enter ", font=('Comic Sans MS', 11), command=input_int_3entries)
b.grid(row=10, column=1, sticky=W)
b = Button(root,text=" Enter ", font=('Comic Sans MS', 11), command=clear_index)
b.grid(row=12, column=1, sticky=W)
b = Button(root,text=" Save txt ", font=('Comic Sans MS', 11), command=create_txt)
b.grid(row=14, column=1, sticky=W)

root.mainloop()