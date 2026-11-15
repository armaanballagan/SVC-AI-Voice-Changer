"""vocalCleaner

Runs from vocalExtractor.bat (inside the demucs-cuda conda env).
Splits the downloaded song into lead vocals, backing vocals and instrumental:

    1. BS-Roformer:   audio.wav -> vocals + instrumental
    2. Karaoke model: vocals    -> lead vocal + backing vocals

Lead and backing are converted separately by VoiceChangingscript.py so they don't clash.

Outputs (in separated\\stems\\):
    lead.wav         -> converted by VoiceChangingscript.py
    backing.wav      -> converted by VoiceChangingscript.py
    instrumental.wav -> mixed back in by VoiceChangingscript.py
    vocals.wav       -> in-between step (used as a fallback if step 2 fails)
"""

import os
from audio_separator.separator import Separator

INPUT_PATH = os.path.join("Downloads", "audio.wav")
OUTPUT_DIR = os.path.join("separated", "stems")
MODEL_DIR = os.path.join("pretrained_models", "audio-separator")  # models download here on first run

VOCAL_MODEL = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"
KARAOKE_MODEL = "mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt"

if not os.path.exists(INPUT_PATH):
    raise SystemExit(f"{INPUT_PATH} not found - download a song first.")

os.makedirs(OUTPUT_DIR, exist_ok=True)
separator = Separator(output_dir=OUTPUT_DIR, model_file_dir=MODEL_DIR, output_format="WAV")

# Step 1: split vocals from instrumental
separator.load_model(model_filename=VOCAL_MODEL)
separator.separate(INPUT_PATH, custom_output_names={"Vocals": "vocals", "Instrumental": "instrumental"})
print("vocals and instrumental separated!")

# Step 2: split lead vocal from backing vocals
separator.load_model(model_filename=KARAOKE_MODEL)
separator.separate(os.path.join(OUTPUT_DIR, "vocals.wav"),
                   custom_output_names={"Vocals": "lead", "Instrumental": "backing"})
print("lead and backing vocals separated!")
