"""VideoCreatorGUI

This script loads a tkinter video creator gui for the user to interact with.
The user is able to either upload thier own image or generate a new image.
If the user decides to generate an image the ImageGenerator.py script is run and the user is presented with an image generation GUI.
The selected image is then combined with their audio and exported as a .mp4 file.
After the video is created the VideoPlayerGUI.py script is run so the user can view thier video

Author:
    Armaan Ballagan - 26.6.2023
"""



from moviepy.editor import AudioFileClip, ImageClip
from tkinter import *
from PIL import ImageTk, Image
from tkinter import Tk, Button
from PIL import Image, ImageTk
from tkinter import filedialog
import subprocess
import json
import os
from tkinter import Tk, Button, filedialog, Label
from PIL import Image, ImageTk


# Read the dictionary from the file
file_path = "values.json"
with open(file_path, "r") as file:
    values = json.load(file)


def add_static_image_to_audio(image_path, audio_path, output_path):
    '''
    Creates and outputs a video after combining a static image with an audio file
    '''
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path)
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    # set the FPS to 1
    video_clip.fps = 1
    # export video clip
    video_clip.write_videofile(output_path)



def createNewFrame(image_path):
    '''
    Creates a new frame that displays the correct image for the button
    
    Parameters:
    image_path (String): The image path refers to the path of the selected image. It is used to display the correct image on the button in the GUI.
    '''

    root = Tk()
    root.geometry('600x450+650+200')  # Size of the window
    root.resizable(True, True)
    root.title('Video Creator')

    titleLabel = Label(root, text="Select an Image", font='san-serif 30 bold', pady=10)
    titleLabel.pack()

    chooseimageframe = Frame(root,pady=5)
    chooseimageframe.pack()
    createvideoframe = Frame(root,pady=10)
    createvideoframe.pack()

    desired_width = 200
    new_image = scaleImage(image_path, desired_width)

    selectimage = Button(chooseimageframe, image=new_image, compound='top', text='Upload Image', font='san-serif 20 bold', padx=15, pady=10, command=lambda: loadImage(root))
    selectimage.pack(side="left",padx=10)

    generateimage = Button(chooseimageframe, text='Generate Image', font='san-serif 20 bold', padx=15, pady=10, command=lambda: generateImage(root))
    generateimage.pack(side="right", padx=10)

    CreateVideoButton = Button(root, text='Create Video', font='san-serif 20 bold', padx=15, pady=10, command=lambda: createVideo(root, image_path, ))
    CreateVideoButton.pack(pady= 10)

    root.mainloop()


def generateImage(root):
    '''
    Opens the Image Generator GUI. After the ImageGenerator GUi is closed the frame is deleted and reloaded with a different button image
  
    Parameters:
    root (Frame): The root is the window that pops up. It is used to referece which window to destroy.
    '''

    subprocess.run(['python', 'ImageGenerator.py'])
    root.destroy()
    createNewFrame(r"Images\generated Image.png")

def loadImage(root):
    '''
    Reloads the frame and displays a different button image
    
    Parameters:
    image_path (String): The image path refers to the path of the selected image. It is used to display the correct image on the button in the GUI.
    '''
    
    image_path = filedialog.askopenfilename(initialdir=os.path.abspath("Images"), title="Select A File", filetypes=(("all files", "*.*"), ("jpg files", "*.jpg"), ("png files", "*.png")))
    root.destroy()
    createNewFrame(image_path)


def createVideo(root, image_path):
    '''
    Destroys the frame and combines audio with image to output a video. It then opens the video in the VideoPlayerGUI
  
    Parameters:
    root (Frame): The root is the window that pops up. It is used to referece which window to destroy
    image_path (String): The image path refers to the path of the selected image. The image path gets written to the values.json file so that it can be read from other scripts
    '''

    root.destroy()
    audio_path = r"Outputs\outputSong.mp3"
    output_path = r"Outputs\outputVideo.mp4"
    add_static_image_to_audio(image_path, audio_path, output_path)
    values.update(Image_Path = image_path)
    file_path = "values.json" # Write the dictionary to a JSON file to change the values in the other script
    with open(file_path, "w") as file:
        json.dump(values, file)
    subprocess.run(['python', 'VideoPlayerGUI.py']) 



def scaleImage(image_path, desired_width):
    '''
    Scales image to desired width while mantaining aspect ratio
    
    Parameters:
    image_path (String): image_path (String): The image path refers to the path of the selected image. It is the image that gets scaled
    desired_width (int): desired_width is the width you want the image to be while still maintaining the aspect ratio 
    '''

    image = Image.open(image_path)
    # Resize the image while maintaining its aspect ratio
    width, height = image.size
    aspect_ratio = desired_width / width
    desired_height = int(height * aspect_ratio)
    resized_image = image.resize((desired_width, desired_height), Image.ANTIALIAS)
    new_image = ImageTk.PhotoImage(resized_image)
    return new_image


initial_image_path = r'Images\Default_Image.jpg'
createNewFrame(initial_image_path)

