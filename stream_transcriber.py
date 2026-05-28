from faster_whisper import WhisperModel
import asyncio
import numpy as np


model=WhisperModel(
    "small",
    compute_type="int8"
)

async def transcriber_worker(queue):
    while True:
        # print("Waiting for chunk...")
        audio_chunk = await queue.get()
        # print("Chunk processing...")

        audio_np = np.squeeze(audio_chunk).astype("float32")

        # print(audio_np.shape)
        # print(audio_np.dtype)

        segments, info = model.transcribe(
            audio_np,
            language="en",
            beam_size=1,
            vad_filter=False,
            condition_on_previous_text=True
        )

        text = " ".join([
            segment.text for segment in segments
        ])
        if text.strip():
            print("Partial:", text)