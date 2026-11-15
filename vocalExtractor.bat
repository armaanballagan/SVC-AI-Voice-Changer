call conda activate demucs-cuda
REM Remove the previous song's stems so a failed run can't leave old files behind
if exist "separated\stems" rmdir /s /q "separated\stems"
REM BS-Roformer (vocals/instrumental) -> karaoke (lead/backing)
python vocalCleaner.py
call conda activate so-vits-svc-fork2

REM Old Demucs separation (replaced by BS-Roformer in vocalCleaner.py):
REM demucs -d cuda -n htdemucs_ft --two-stems=vocals --segment=7 --shifts=5 --overlap=0.5 --int24 --clip-mode=rescale "Downloads\audio.wav"
REM Older settings: --mp3-preset=2 --segment=7 --shifts=3 --overlap=0.25

REM call conda activate uvr5
REM python "..\ultimatevocalremovergui-master\ultimatevocalremovergui-master\UVR.py" -m "models/MDX_NET_Main" -i "Downloads\audio.wav" -o
REM call conda activate so-vits-svc-fork2
