import sounddevice as sd
from configs.settings import SAMPLE_RATE
import numpy as np


audio_chunks=[]
stream = None

def callback(indata, frames, time, status):
    audio_chunks.append(indata.copy())


def start_recording():
    global stream, audio_chunks

    audio_chunks = []

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=callback
    )

    stream.start()
    print("\nrecording started...")

def stop_recording():
    global stream
    
    stream.stop()
    stream.close()

    print("\nrecording done...")

    audio_data= np.concatenate(audio_chunks, axis=0)
    return audio_data.flatten()