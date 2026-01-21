import os
import subprocess
import sounddevice as sd
import soundfile as sf

PIPER_EXE = "piper/piper.exe"
MODEL = "piper/en_US-hfc_male-medium.onnx"
CONFIG = "piper/en_US-hfc_male-medium.onnx.json"
OUTPUT = "reply.wav"


def speak(text):
    if not text:
        return

    clean_text = text.replace("*", "").replace("#", "")

    subprocess.run(
        [
            PIPER_EXE,
            "--model", MODEL,
            "--config", CONFIG,
            "--sentence_silence", "0.05",
            "--output_file", OUTPUT
        ],
        input=clean_text.encode("utf-8"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if os.path.exists(OUTPUT):
        audio, sr = sf.read(OUTPUT, dtype="float32")
        sd.play(audio, sr)
        sd.wait()
