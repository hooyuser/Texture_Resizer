import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from pathlib import Path
import numpy as np
import re
import cv2

window = tk.Tk()
window.title("Texture Processor")
window.geometry("1024x768")
window.resizable(True, True)
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)
window.rowconfigure(4, weight=50)
window.rowconfigure(5, weight=1)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=5)
window.columnconfigure(2, weight=1)

frame = tk.Frame(master=window, width=150, height=150)

l1 = tk.Label(master=window, text="Batch Resize", font=("Arial", 12), )
l1.grid(row=0, column=0)

l2 = tk.Label(master=window, text="File Directory", font=("Arial", 12), )
l2.grid(row=1, column=0)


class ImgFiles:
    def __init__(self):
        self.dir_path = ''
        self.file_list = []
        self.display_list = []


imgs = ImgFiles()


def open_dir():
    if imgs.dir_path == "":
        imgs.dir_path = filedialog.askdirectory()
    else:
        imgs.dir_path = filedialog.askdirectory(initialdir=imgs.dir_path)
    e_path_text.set(imgs.dir_path)


RES_ID = {'512': 1, '1024': 2, '2048': 3, '4096': 4, '8192': 5}


def get_img_info(img_file):
    im = cv2.imread(str(img_file))
    w, h = im.shape[1], im.shape[0]
    res_id = 6
    if w == h:
        res_id = RES_ID.get(str(w), 6)
    return {'np_data': im, 'res_id': res_id, 'res': f'{w} * {h}'}


def get_size(img_file):
    size = img_file.stat().st_size
    return f'{size >> 10} KB' if size < 1048576 else f'{size / 1048576.0:.2f} MB'


def display_img_list(*args):
    if lv_dirs:
        for item in lv_dirs.get_children():
            lv_dirs.delete(item)
        imgs.display_list = []
        if var_filter.get() == 0:
            for f in imgs.file_list:
                lv_dirs.insert('', 'end', values=(f['path'].name, f['img']['res'], get_size(f['path'])))
            imgs.display_list = list(range(len(imgs.file_list)))
        else:
            for i, f in enumerate(imgs.file_list):
                if f['img']['res_id'] == var_filter.get():
                    lv_dirs.insert('', 'end', values=(f['path'].name, f['img']['res'], get_size(f['path'])))
                    imgs.display_list.append(i)

    return True


EXTS = [".png", ".exr", ".jpg", ".tif", ".tiff"]


def search_imgs():
    name = e_name.get()
    if name == '':
        imgs.file_list = [{'path': f, 'img': get_img_info(f)} for f in Path(imgs.dir_path).iterdir() if
                          f.is_file() and f.suffix in EXTS]
    else:
        rule = re.compile(name)
        imgs.file_list = [{'path': f, 'img': get_img_info(f)} for f in Path(imgs.dir_path).iterdir() if
                          f.is_file() and f.suffix in EXTS and re.search(rule, f.name)]

    display_img_list()


def resize_img():
    for idx in imgs.display_list:
        resized = cv2.resize(imgs.file_list[idx]['img']['np_data'], None, fx=0.5, fy=0.5,
                             interpolation=cv2.INTER_CUBIC)  # cv2.INTER_AREA


e_path_text = tk.StringVar()
e_path = tk.Entry(window, textvariable=e_path_text)
e_path.grid(row=1, column=1, sticky=tk.EW)

b_select_path = tk.Button(
    window,
    text="Select Path",
    command=open_dir,
    font=("Arial", 12),
)
b_select_path.grid(row=1, column=2, padx=10, )

l_name = tk.Label(master=window, text="Name", font=("Arial", 12), )
l_name.grid(row=2, column=0)

e_name = tk.Entry(window, )
e_name.grid(row=2, column=1, sticky=tk.EW)

b_search_imgs = tk.Button(
    window,
    text="Search Files",
    command=search_imgs,
    font=("Arial", 12),
)
b_search_imgs.grid(row=2, column=2, padx=10, )

l_filter = tk.Label(master=window, text="Filter", font=("Arial", 12), )
l_filter.grid(row=3, column=0)

frame_filters = tk.Frame(window, background="#99ceff", height=70)
frame_filters.grid(row=3, column=1, columnspan=2, sticky=tk.W)

FILTERS = [
    ('None', 0),
    ('512×512', 1),
    ('1K', 2),
    ('2K', 3),
    ('4K', 4),
    ('8K', 5),
    ('Others', 6)]
var_filter = tk.IntVar()
var_filter.set(0)
var_filter.trace_add("write", display_img_list)

for resolution, idx in FILTERS:
    b = tk.Radiobutton(frame_filters, text=resolution, variable=var_filter, value=idx, font=("Arial", 12), )
    b.grid(row=0, column=idx)

columns = ("name", "resolution", "size")
headers = ("Name", "Resolution", "File Size")
widths = (350, 120, 120)
lv_dirs = ttk.Treeview(window, show="headings", columns=columns)

for (column, header, width) in zip(columns, headers, widths):
    lv_dirs.column(column, width=width, anchor="w")
    lv_dirs.heading(column, text=header, anchor="w")

lv_dirs.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW, padx=10, pady=15)
scrollbar = tk.Scrollbar(lv_dirs, orient="vertical")
scrollbar.config(command=lv_dirs.yview)
scrollbar.pack(side="right", fill="y")
lv_dirs.config(yscrollcommand=scrollbar.set)

l_resize = tk.Label(master=window, text="Resizing Ratio", font=("Arial", 12), )
l_resize.grid(row=5, column=0, pady=8, sticky=tk.N)

frame_ratios = tk.Frame(window, background="#99ceff", height=70)
frame_ratios.grid(row=5, column=1, columnspan=2, pady=8, sticky=tk.NW)

RATIOS = [
    ('1/2', 0),
    ('1/4', 1),
    ('1/8', 2),
    ('Custom', 3),
]
var_ratio = tk.IntVar()
var_ratio.set(0)

for ratio, idx in RATIOS:
    b = tk.Radiobutton(frame_ratios, text=ratio, variable=var_ratio, value=idx, font=("Arial", 12), )
    b.grid(row=0, column=idx)

b_search_imgs = tk.Button(
    window,
    text="Resize All",
    font=("Arial", 12),
)
b_search_imgs.grid(row=5, column=2, padx=10, pady=8, sticky=tk.N)

window.mainloop()
