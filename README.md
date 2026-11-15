# SVC-AI Voice Changer

CS final project by Armaan Ballagan. A Tkinter app that:

1. Downloads a song from a YouTube link as a `.wav`
2. Splits it into lead vocals, backing vocals and instrumental (BS-Roformer + karaoke model via `audio-separator`)
3. Converts the lead vocals into another voice with [so-vits-svc-fork](https://github.com/voicepaw/so-vits-svc-fork)
4. Mixes everything back together, and can turn the result into a video with an image (optionally generated with [min-dalle](https://github.com/kuprel/min-dalle))

## Files

| File | What it does |
|---|---|
| `AudioGui.py` | Main GUI: download, split, convert, play |
| `vocalExtractor.bat` | Runs `vocalCleaner.py` in the `demucs-cuda` env |
| `vocalCleaner.py` | Separates vocals / backing / instrumental |
| `VoiceChangingscript.py` | Voice conversion and remixing |
| `ImageGenerator.py` | Text-to-image with min-dalle |
| `VideoCreatorGUI.py` / `VideoPlayerGUI.py` | Make and play a video of the converted song |
| `values.json` | Settings shared between the scripts |

## Setup (Windows, NVIDIA GPU)

1. Clone with the min-dalle submodule:
   ```
   git clone --recurse-submodules https://github.com/armaanballagan/SVC-AI-Voice-Changer.git
   ```
2. Create the two conda environments (the batch file expects these exact names):
   ```
   conda env create -f environments/so-vits-svc-fork2.yml
   conda env create -f environments/demucs-cuda.yml
   ```
3. Install [ffmpeg](https://ffmpeg.org/) and make sure it's on your PATH.
4. Download the voice models from the [v1.0 release](https://github.com/armaanballagan/SVC-AI-Voice-Changer/releases/tag/v1.0) and unzip them into `Models/` (see `Models/README.md`).
5. Run the app:
   ```
   conda activate so-vits-svc-fork2
   python AudioGui.py
   ```

The separation models and DALL·E mini weights download automatically on first use.
