from tkinter import *
import pygame
import os
from  subprocess import call

a = 1
def click():
    a=1
    with open('test_a.txt', 'w') as f:
        f.write(str(a))
    win.destroy()
    call(["python","進入遊戲後畫面.py"])
    

def click_two():
    a=2
    with open('test_a.txt', 'w') as f:
        f.write(str(a))
    win.destroy()
    call(["python","進入遊戲後畫面.py"])

def click_three():
    a=3
    with open('test_a.txt', 'w') as f:
        f.write(str(a))
    win.destroy()
    call(["python","進入遊戲後畫面.py"])

def click_four():
    a=4
    with open('test_a.txt', 'w') as f:
        f.write(str(a))
    win.destroy()
    call(["python","進入遊戲後畫面.py"])

win = Tk()
win.geometry("1350x700")
win.geometry("+100+50")
win.resizable(width=0, height=0)
background = PhotoImage(file="C:\\Users\\user\\Desktop\\img_space\\2img2\\background.png")
bg_label = Label(win,
                 image = background,
                 compound = 'bottom')
bg_label.pack()

photo_one = PhotoImage(file="C:\\Users\\user\\Desktop\\img_space\\2img2\\universeship.png")
button_one = Button(win,
                width=417,
                height=235,
                image=photo_one,
                command=click)
button_one.place(x=50,y=70)

photo_two = PhotoImage(file="C:\\Users\\user\\Desktop\\img_space\\2img2\\UFO.png")
button_two = Button(win,
                width=417,
                height=235,
                image=photo_two,
                command=click_two)
button_two.place(x=875,y=70)

photo_three = PhotoImage(file="C:\\Users\\user\\Desktop\\img_space\\2img2\\universeship1.png")
button_three = Button(win,
                width=417,
                height=235,
                image=photo_three,
                command=click_three)
button_three.place(x=50,y=400)

photo_four = PhotoImage(file="C:\\Users\\user\\Desktop\\img_space\\2img2\\universeship2.png")
button_four = Button(win,
                width=417,
                height=235,
                image=photo_four,
                command=click_four)
button_four.place(x=875,y=400)

win.mainloop()