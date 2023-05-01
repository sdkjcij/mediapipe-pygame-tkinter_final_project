from tkinter import *
from tkvideo import tkvideo
from subprocess import call
import pygame
import os
import cv2
#from PIL import Image, ImageT
import subprocess

###################################################################################
#相對路徑
m = os.path.join("img_tk","操作方式1.mp4")
n = os.path.join("img_tk","操作方式2.mp4")
mn = os.path.join("img_tk","background3.png")

#自定義函式
def click_one():
    pygame.mixer.music.stop()
    subprocess.Popen(["python", "game_final_project.py"])
    window.destroy()

def click_two():
    pygame.mixer.music.stop()
    subprocess.Popen(["python", "game_new_control_mode.py"])
    window.destroy()
    
###################################################################################

#起始視窗
window = Tk()
window.geometry("1350x700")
window.geometry("+100+50")
window.resizable(width=0, height=0)
background = PhotoImage(file = mn)
bg_label = Label(window,
                 image = background,
                 compound = 'bottom')
bg_label.pack()
pygame.mixer.init()

###################################################################################

#按鈕設置

button_left = Button(window,
                width = 10,
                height = 2,
                text = "開始遊玩",
                command = click_one,
                font = ('標楷體',30),
                fg = "#BA55D3",
                bg = "#FFDAB9",
                activeforeground = "#800080",
                activebackground = "#FFEBCD"
                )
button_left.place(x=180,y=550)


button_right = Button(window,
                width = 10,
                height = 2,
                text = "開始遊玩",
                command = click_two,
                font = ('標楷體',30),
                fg = "#BA55D3",
                bg = "#FFDAB9",
                activeforeground = "#800080",
                activebackground = "#FFEBCD"
                )
button_right.place(x=975,y=550)


###################################################################################

#影片設置
lblvideo_left= Label(window)
lblvideo_left.place(x=30,y=100)
player = tkvideo(m, lblvideo_left, loop = 1, size =(500,360))
player.play()

lblvideo_right= Label(window)
lblvideo_right.place(x=815,y=100)
player = tkvideo(n, lblvideo_right, loop = 1, size =(500,360))
player.play()

                 
window.mainloop()