from tkinter import *
from subprocess import call
from tkvideo import tkvideo
import pygame
import os
import tkinter as tk
import cv2
from tkinter import colorchooser
import sys
import threading

#######檔案路徑##########
m = os.path.join('sound_tk','music.mp3')
n = os.path.join('img_tk','space_star.png')
nm = os.path.join('img_tk','space.mp4')

#######自定義函式##########
scale_music = None
def submit():
    b = int(scale_music.get())
    a = b/100
    pygame.mixer.music.set_volume(a)

def scale_one():
    global scale_music
    win_volume = Tk()
    scale_music = Scale(win_volume, 
                    from_ = 100,
                    to = 0)
    scale_music.place(x=5,y=5)
    button_scale = Button(win_volume,
                          text = "確認",
                          command = submit)
    button_scale.place(x=100,y=150)

def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load(m)
    pygame.mixer.music.play(loops=-1)

def color_choose():
    a = colorchooser.askcolor()
    color = a[1]
    button_setting.config(bg=color)
    button_start.config(bg=color)

def color_choose_2():
    b = colorchooser.askcolor()
    color = b[1]
    button_setting.config(fg=color)
    button_start.config(fg=color)

def click_setting():
    win_setting = Tk()
    win_setting.geometry("200x150")
    win_setting.geometry("+100+50")
    win_setting.config(bg="#FFDAB9")
    win_setting.resizable(width=0, height=0)
    button_color = Button(win_setting, 
                            width = 20,
                            text = "按鈕顏色調整",
                            height = 1,
                            command = color_choose).pack(padx=20,pady=5)
    button_color_word = Button(win_setting, 
                            width = 20,
                            text = "字體顏色調整",
                            height = 1,
                            command = color_choose_2).pack(padx=20,pady=5)
    button_volume = Button(win_setting,
                            text = "音量調整", 
                            width = 20,
                            height = 1,
                            command = scale_one).pack(padx=20,pady=5)
    win_setting.mainloop()

def click_start():
    win_start.destroy()
    call(["python", "testtest.py"])

############起始畫面############
win_start = Tk()
win_start.geometry("1350x700")
win_start.geometry("+100+50")
win_start.resizable(width=0, height=0)
background = PhotoImage(file = n)
bg_label = Label(win_start,
                 image = background,
                 compound = 'bottom')
bg_label.pack()

button_start = Button(win_start,
                      width = 20,
                      height = 1,
                      text = "進入遊戲",
                      command = click_start,
                      font = ('標楷體',30),
                      fg = "#BA55D3",
                      bg = "#FFDAB9",
                      activeforeground = "#800080",
                      activebackground = "#FFEBCD")
button_start.place(x=450,y=475)

button_setting = Button(win_start,
                      width = 20,
                      height = 1,
                      text = "設置",
                      command = click_setting,
                      font = ('標楷體',30),
                      fg = "#BA55D3",
                      bg = "#FFDAB9",
                      activeforeground = "#800080",
                      activebackground = "#FFEBCD")
button_setting.place(x=450,y=600)
play_music()

############影片設置############
lblvideo_left= Label(win_start)
lblvideo_left.place(x=350,y=40)
player = tkvideo(nm, lblvideo_left, loop = 1, size =(600,400))
player.play()

win_start.mainloop()