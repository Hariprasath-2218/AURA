import os
import sounddevice as sd
import soundfile as sf
import numpy as np
import requests
from dotenv import load_dotenv
from faster_whisper import WhisperModel

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

SAMPLE_RATE = 16000
AUDIO_FILENAME = "input.wav"
WHISPER_MODEL_SIZE = "tiny"

print("🧠 Loading Faster-Whisper model...")
whisper_model = WhisperModel(
    WHISPER_MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)
print("✅ Faster-Whisper loaded")


def record_audio(duration=5):
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    return audio.flatten()


def offline_listen(duration=5):
    print(f"🎤 Recording {duration}s (offline)")
    audio = record_audio(duration)

    segments, _ = whisper_model.transcribe(
        audio,
        language="en",
        beam_size=1,
        vad_filter=True
    )

    return " ".join(seg.text for seg in segments).strip()


def deepgram_listen(duration=5):
    print(f"🎤 Recording {duration}s (Deepgram)")
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    sf.write(AUDIO_FILENAME, audio, SAMPLE_RATE)

    with open(AUDIO_FILENAME, "rb") as f:
        r = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            },
            data=f.read(),
            timeout=20
        )

    r.raise_for_status()
    result = r.json()

    return (
        result.get("results", {})
        .get("channels", [{}])[0]
        .get("alternatives", [{}])[0]
        .get("transcript", "")
        .strip()
    )
