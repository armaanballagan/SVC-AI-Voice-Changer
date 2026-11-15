"""VideoPlayerGUI

This script provides an interactive video player GUI using the tkinter library.
The user is able to play and pause or stop their newly generated videos.
Tkinters video module does not play audio with the video and the module was pretty finicky so a static image is displayed instead of a video.
Displaying the static image with audio has the result as playing the video since, in this instance, the video is just a static image with audio.

Author:
    Armaan Ballagan - 26.6.2023
"""

from tkinter import *
from PIL import ImageTk, Image
import pygame
import json


# Read the dictionary from the file
file_path = "values.json"
with open(file_path, "r") as file:
    values = json.load(file)
image_path = values["Image_Path"]


def playAudio():
    '''Plays video audio'''
    global playingAudio
    if not playingAudio:
        pygame.mixer.music.play(loops=0)
    else:
        pygame.mixer.music.unpause()
    playingAudio = True


def pauseAudio():
    '''pauses video audio'''
    pygame.mixer.music.pause()


def stopAudio():
    '''stops video audio'''
    global playingAudio
    pygame.mixer.music.stop()
    playingAudio = False

# Create tkinter window
root = Tk()
root.geometry("600x400+650+200")

#frames
frame = Frame(root, width=600, height=400)
frame.pack()
audioframe = Frame(root, pady= 10)
audioframe.pack()

#convert image to be compatible with tkinter
img = ImageTk.PhotoImage(Image.open(image_path))

#display image
label = Label(frame, image = img)
label.pack()

playButton = Button( audioframe , text = "Play Video" , command = playAudio)
pauseButton = Button( audioframe , text = "Pause Video" , command = pauseAudio)
stopButton = Button( audioframe , text = "Stop Video" , command = stopAudio)
playingAudio = False #see if audio is being played
pygame.mixer.init()
pygame.mixer.music.load("Outputs\outputSong.mp3")

playButton.grid(row = 0, column=0, padx=5,pady=5)
pauseButton.grid(row = 0, column=1, padx=5,pady=5)
stopButton.grid(row = 0, column=2,padx=5,pady=5)

root.mainloop()