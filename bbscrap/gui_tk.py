from tkinter import *
from tkinter import filedialog

root = Tk()
root.withdraw()
root.update()
file_path = filedialog.askdirectory()
root.destroy()