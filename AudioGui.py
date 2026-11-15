"""AudioGUI

This script loads a tkinter audio player and voice conversion gui for the user to interact with.
The user is able to download audio from youtube by entering a youtube link. The audio is downloaded as a .wav audio file
Once the audio is downloaded, the user can press the convert button to run the VoiceChangingScript and change the vocals in the audio.
The user has the option to select the speakerModel and predictionMethod that will be used when converting audio by using the drop down lists.
The user is able to play, pause, and stop downloaded and converted audio using the buttons on the gui.

Author:
    Armaan Ballagan - 26.6.2023
"""

import tkinter
from tkinter import *
import yt_dlp
from yt_dlp.utils import DownloadError
import subprocess
import json
import re
import pygame
import os.path
import pytube
from pytube import YouTube
import time
from urllib.error import HTTPError



# Define the values for voice changing parameters
values = {
    "model_path": "Models\Dio\model.pth",
    "config_path": "Models\Dio\config.json",
    "speaker": "Dio",
    "cluster_model_path": "cluster_model.pt",
    "transpose": 0,
    "auto_predict_f0": False,
    "cluster_infer_ratio": 0,
    "noise_scale": 0.2,
    "f0_method": "crepe",
    "silence_threshold": -25,
    "pad_seconds": 0.5,
    "chunk_seconds": 5,
    "absolute_thresh": False,
    "max_chunk_seconds": 40,
    "use_gpu": True,
    "Image_Path": "Images\shrek.jpg",
    "song_name": "song"
}

# Keep the last downloaded song's name if the GUI is reopened without downloading again
try:
    with open("values.json", "r") as file:
        values["song_name"] = json.load(file).get("song_name", "song")
except (OSError, ValueError):
    pass


class DownloadError(Exception):
    '''Does nothing if youtube video download fails'''
    pass


def SplitVocals():
    '''
    Runs the vocalExtractor.bat file
    '''
    #Extract vocals
    batch_file_path = 'vocalExtractor.bat'

    if os.path.exists("Downloads\\audio.wav"): #Check if file exists
            splitStatus.config(text="Splitting vocals... (takes a few minutes)", fg="black")
            window.update_idletasks() #show the message before the window freezes during the split
            subprocess.run(batch_file_path, shell=True) #run vocalExtractor.bat
            if os.path.exists("separated\\stems\\vocals.wav"): #bat deletes old stems first, so this means the split worked
                splitStatus.config(text="Vocals extracted!", fg="black")
                print("vocals extracted!")
            else:
                splitStatus.config(text="Split failed - check the terminal", fg="black")
                print("vocal split failed!")
    else:
        splitStatus.config(text="Download a song first!", fg="black")
        print("Audio file not downloaded. Try downloading a youtube video!")


def changeVoice():
    '''
    Runs the VoiceChangingScript
    Updates values.json and launches the VoiceChangingScript to convert vocals if all conditions are met
    '''
    speakerModel = speakerOption.get() #get value from speaker drop down menu text
    predictionModel = predictionOption.get() #get value from prediction drop down menu text
    updateValues(speakerModel, predictionModel)

    if os.path.exists("separated\\stems\\vocals.wav"): #Check if file exists
            # Release the audio player's hold on the files, otherwise outputSong.mp3 can't be overwritten
            global playingDownloadedAudio, playingConvertedAudio
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            playingDownloadedAudio = playingConvertedAudio = False
            subprocess.run(['python', 'VoiceChangingscript.py']) #run VoiceChangingscript.py
    else:
        print("no vocals detected, rerun splitVocals!")


def updateValues(speakerModel, predictionModel):
    '''
    Configures the so-vits-svc model paths and settings
    
    Updates the values dictionary based on user input. Writes the updated valuse to values.json file
  
    Parameters:
    speakerModel (StringVar): The speakerModel inputed by the user
    predictionModel (StringVar): The predicitonModel inputed by the user
    '''

    global values
    values.update(f0_method = predictionModel, speaker= speakerModel, model_path= f'Models\\{speakerModel}\\model.pth', config_path = f'Models\\{speakerModel}\\config.json', transpose = transposeOptions[transposeOption.get()])
    file_path = "values.json" # Write the dictionary to a JSON file to change the values in other scripts
    with open(file_path, "w") as file:
        json.dump(values, file)
    


def playAudio():
    '''Plays downloaded audio'''
    global playingDownloadedAudio
    if os.path.exists("Downloads\\audio.wav"):
        if not playingDownloadedAudio:
            pygame.mixer.music.load("Downloads\\audio.wav")
            print("played")
            pygame.mixer.music.play(loops=0)
        else:
            print("resumed")
            pygame.mixer.music.unpause()
        playingDownloadedAudio = True
    else:
        print("Audio file not downloaded. Try downloading a youtube video!")

def pauseAudio():
    '''Pauses downloaded audio'''
    print("paused")
    pygame.mixer.music.pause()

def stopAudio():
    '''Stops downloaded audio'''
    print("stopped")
    global playingDownloadedAudio
    pygame.mixer.music.stop()
    playingDownloadedAudio = False


def playConvertedAudio():
    '''Plays converted audio'''
    global playingConvertedAudio
    if os.path.exists("Outputs\outputSong.mp3"):
        if not playingConvertedAudio:
            pygame.mixer.music.load("Outputs\outputSong.mp3")
            pygame.mixer.music.play(loops=0)
        else:
            pygame.mixer.music.unpause()
        playingConvertedAudio = True
    else:
        print("Download an audio file and press the convert Button!")

def pauseConvertedAudio():
    '''Pauses converted audio'''
    pygame.mixer.music.pause()


def stopConvertedAudio():
    '''Stops converted audio'''
    global playingConvertedAudio
    pygame.mixer.music.stop()
    playingConvertedAudio = False

def generateVideo():
     '''Runs the VideoCreatorGUI script'''

     subprocess.run(["python", r"VideoCreatorGUI.py"])


def download():

    url = link.get()  # assuming link is a Tkinter Entry widget
    '''
    Downloads a YouTube video as a .wav audio file.
    Saves to "Downloads/audio.wav".
    '''
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',  # ignored for .wav, but included for clarity
        }],
        'outtmpl': 'Downloads/audio.%(ext)s',
        'overwrites': True
    }
     
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Save the video title (spaces -> '_', characters Windows filenames can't contain removed) for naming the output song
    title = re.sub(r'[\\/:*?"<>|]', '', info.get('title', 'song')).strip().replace(' ', '_')
    values["song_name"] = title or "song"
    with open("values.json", "w") as file:
        json.dump(values, file)



    tkinter.Label(downloadframe, text="Audio has been downloaded", font="arial 15").pack() #display "downloaded" after download.
    window.geometry('600x630') #resize window
    print("audio downloaded!")


window = tkinter.Tk() #create new window

#Frames
downloadframe = Frame(window,pady=5)
downloadframe.pack()
donloadedAudioframe = Frame(downloadframe, padx=25)
donloadedAudioframe.pack(side = BOTTOM)

#bottom frames
bottomframe = Frame(window,pady=5)
bottomframe.pack( side = BOTTOM )

optionsframe = Frame(bottomframe, padx=25)
optionsframe.pack( side = LEFT )

splitframe = Frame(optionsframe, padx=25)
splitframe.pack()

speakerframe = Frame(optionsframe, padx=25)
speakerframe.pack( side = TOP )

predictionframe = Frame(optionsframe, padx=25)
predictionframe.pack()



convertframe = Frame(bottomframe, padx=25)
convertframe.pack( side = RIGHT)
convertedAudioframe = Frame(convertframe, padx=25)
convertedAudioframe.pack( side = BOTTOM)


window.geometry('600x600+650+150') # Size of the window
window.resizable(True, True)
window.title('Ai Voice Changer')

#Downloader frame
label1 = tkinter.Label(downloadframe, text="Ai Voice Changer", font='san-serif 30 bold', pady=10)
link = tkinter.StringVar() # Specify variable type
label2 = tkinter.Label(downloadframe, text="Paste your link here", font='san-serif 15 bold')
link_enter = tkinter.Entry(downloadframe, width=70, textvariable=link)
button1 = tkinter.Button(downloadframe, text='Download', font='san-serif 16 bold', bg='red', padx=2, pady=5, command = download)

# Downloaded Audio player
playButton = Button( donloadedAudioframe , text = "Play Downloaded Audio" , command = playAudio)
pauseButton = Button( donloadedAudioframe , text = "Pause Downloaded Audio" , command = pauseAudio)
stopButton = Button( donloadedAudioframe , text = "Stop Downloaded Audio" , command = stopAudio)
playingDownloadedAudio = False #see if audio is being played
pygame.mixer.init() #initialize mixer for playing audio

label1.pack()
label2.pack()
link_enter.pack()
button1.pack()
playButton.grid(row = 0, column=0, padx=5,pady=5)
pauseButton.grid(row = 0, column=1, padx=5,pady=5)
stopButton.grid(row = 0, column=2,padx=5,pady=5)


#optionsframe
speakers = [    # speaker menu options
    "Dio",
    "Rick Astely",
    "Soldier",
    "Hatsune Miku",
    "Link",
    "Sentry Bot",
    "Armaan",
    "Michael Rosen",
    "Stusiak"
]

prediction_method = ["crepe", #pitch prediction method
                    "crepe-tiny", 
                    "parselmouth", 
                    "dio", 
                    "harvest"]

speakerOption = StringVar() # datatype of speaker menu text
speakerOption.set("Dio") # initial menu text
predictionOption = StringVar() # datatype of prediction menu text
predictionOption.set("crepe") # initial menu text

# Create Dropdown menu
speakerLabel = tkinter.Label(speakerframe, text="Speaker:", font='san-serif 15 bold')
speakerLabel.pack(side=TOP)
speakerMenu = OptionMenu( speakerframe, speakerOption , *speakers)
speakerMenu.config(font='san-serif 10 bold', padx=10, pady=10)
speakerMenu.pack(side=TOP, pady=10)

# prediction frame
predictionLabel = tkinter.Label(predictionframe, text="f0 Prediction Method:", font='san-serif 15 bold', pady=5)
predictionLabel.pack(side=TOP)
predictionMenu = OptionMenu( predictionframe, predictionOption , *prediction_method)
predictionMenu.config(font='san-serif 10 bold', padx=10, pady=10)
predictionMenu.pack()


# split vocals frame
splitLabel = tkinter.Label(predictionframe, text="Split Vocals", font='san-serif 15 bold', pady=5)
splitLabel.pack(side=TOP)
convertButton = Button(predictionframe, text = "Split" , command = SplitVocals, font='san-serif 10 bold', padx=10, pady=10)  # run vocalExtractor.bat
convertButton.pack()
splitStatus = tkinter.Label(predictionframe, text="", font='san-serif 10 bold', pady=5) # shows split progress/result
splitStatus.pack()

#Convertframe
convertButton = Button( convertframe , text = "Convert" , command = changeVoice, font='san-serif 20 bold', padx=15, pady=10)  # run voiceChangingScript

#Converted Audio player
playConvertedAudioButton = Button( convertframe , text = "Play Converted Audio" , command = playConvertedAudio)
pauseConvertedAudioButton = Button( convertframe , text = "Pause Converted Audio" , command = pauseConvertedAudio)
stopConvertedAudioButton = Button( convertframe , text = "Stop Converted Audio" , command = stopConvertedAudio)
playingConvertedAudio = False #see if audio is being played

#Generate video
generateVideoButton = Button( convertframe , text = "Generate Video" , command = generateVideo)

# transpose dropdown (pitch shift of the vocals, 12 semitones = one octave)
transposeOptions = {"-1 Octave": -12, "Default": 0, "+1 Octave": 12}
transposeOption = StringVar()
transposeOption.set("Default") # initial menu text
transposeLabel = tkinter.Label(convertframe, text="Transpose:", font='san-serif 15 bold')
transposeLabel.pack(side=TOP)
transposeMenu = OptionMenu(convertframe, transposeOption, *transposeOptions)
transposeMenu.config(font='san-serif 10 bold', padx=10, pady=5)
transposeMenu.pack(side=TOP)

convertButton.pack(pady=10)
playConvertedAudioButton.pack(pady=4)
pauseConvertedAudioButton.pack(pady=4)
stopConvertedAudioButton.pack(pady=4)
generateVideoButton.pack(pady = 10)


window.mainloop()