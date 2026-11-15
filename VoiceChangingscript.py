"""VoiceChangingScript

This script uses the so-vits-svc voice converter, which gets passed parameters such as speakerModel and predictionModel,
to convert the lead vocals separated by vocalCleaner.py (the original backing vocals are kept unconverted).
After the conversion is finished it recombines the instrumentation with the converted vocals and exports a new audio file.

Author:
    Armaan Ballagan - 26.6.2023
"""

from so_vits_svc_fork.inference.main import infer
from pathlib import Path
from pydub import AudioSegment, effects
import json
import math
import os
from so_vits_svc_fork.utils import get_optimal_device



# Read the dictionary from the values.json file
file_path = "values.json"
with open(file_path, "r") as file:
    values = json.load(file)

# Input paths from vocalCleaner.py
lead_path = r"separated\stems\lead.wav"
backing_path = r"separated\stems\backing.wav"
vocals_path = r"separated\stems\vocals.wav"  # fallback if the lead/backing split failed
instrumental_path = r"separated\stems\instrumental.wav"

# Output paths for the converted vocals
converted_lead_path = r"Outputs\convertedVocals.wav"



def convert(input_path, output_path):
    '''Runs so-vits-svc on one vocal track with the settings from values.json'''
    print(f"converting {input_path}")
    infer(
        input_path=input_path,
        output_path=output_path,
        model_path=Path(values["model_path"]),
        config_path=Path(values["config_path"]),
        recursive=True,
        speaker= 0, #values["speaker"]
        cluster_model_path=Path(values["cluster_model_path"]) if values["cluster_model_path"] else None,
        transpose=values["transpose"],
        auto_predict_f0=values["auto_predict_f0"],
        cluster_infer_ratio=values["cluster_infer_ratio"],
        noise_scale=values["noise_scale"],
        f0_method=values["f0_method"],
        db_thresh=values["silence_threshold"],
        pad_seconds=values["pad_seconds"],
        chunk_seconds=values["chunk_seconds"],
        max_chunk_seconds=values["max_chunk_seconds"],
        absolute_thresh=values["absolute_thresh"],
        device= "cpu" if not values["use_gpu"] else get_optimal_device()
    )


def match_level(converted, original):
    '''Sets the converted track to the same loudness as the original, so lead/backing keep their balance'''
    if math.isinf(converted.dBFS) or math.isinf(original.dBFS):
        return converted
    return converted.apply_gain(original.dBFS - converted.dBFS)


# Each overlay is done 6 dB down so adding loud tracks together can't clip, then normalized back up
HEADROOM_DB = 6

if os.path.exists(lead_path) and os.path.exists(backing_path):
    # Convert only the lead - the original backing vocals are mixed back in unconverted
    convert(lead_path, converted_lead_path)
    print("done infering")

    lead = match_level(AudioSegment.from_file(converted_lead_path, format="wav"), AudioSegment.from_file(lead_path, format="wav"))
    backing = AudioSegment.from_file(backing_path, format="wav")
    if math.isinf(backing.dBFS):  # song has no backing vocals
        vocals = lead
    else:
        vocals = (lead - HEADROOM_DB).overlay(backing - HEADROOM_DB, position=0)
        print("backing vocals mixed with lead")
else:
    # Lead/backing split missing - convert the full vocal track in one pass
    convert(vocals_path, converted_lead_path)
    print("done infering")
    vocals = AudioSegment.from_file(converted_lead_path, format="wav")

#Combine Vocals + Accompaniment
instrumental = AudioSegment.from_file(instrumental_path, format="wav")

# Normalize loudness
vocals = effects.normalize(vocals)
instrumental = effects.normalize(instrumental)

# Overlay the sound files
overlay = effects.normalize((instrumental - HEADROOM_DB).overlay(vocals - HEADROOM_DB, position=0))

#export output
file_handle = overlay.export(f'Outputs\\{values["speaker"]}{values.get("song_name", "song")}.mp3', format="mp3")
file_handle = overlay.export(f'Outputs\outputSong.mp3', format="mp3") # for use with the convertedAudioPlayer in the gui

print("done exporting!")
