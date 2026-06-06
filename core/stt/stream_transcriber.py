from faster_whisper import WhisperModel
from collections import deque
from core.stt.transcript_accumulator import TranscriptAccumulator
from configs.settings import WHISPER_MODEL, LANGUAGE, BEAM_SIZE, VAD_FILTER, COMPUTE_TYPE

import numpy as np
import time


model = WhisperModel(
    WHISPER_MODEL,
    compute_type=COMPUTE_TYPE
)

rolling_buffer = deque(maxlen=3)

accumulator = TranscriptAccumulator()

counter = 0


async def transcriber_worker(queue):

    global counter

    while True:

        audio_chunk = await queue.get()

        rolling_buffer.append(audio_chunk)

        print(
            f"Queue: {queue.qsize()} | Buffer: {len(rolling_buffer)}"
        )

        if len(rolling_buffer) < rolling_buffer.maxlen:
            continue

        counter += 1

        # Run Whisper every 2 seconds
        if counter % 2 != 0:
            continue

        audio_np = np.concatenate(
            list(rolling_buffer),
            axis=0
        ).squeeze().astype(np.float32)

        start = time.perf_counter()

        segments, info = model.transcribe(
            audio_np,
            language=LANGUAGE,
            beam_size=BEAM_SIZE,
            vad_filter=VAD_FILTER,
            condition_on_previous_text=False
        )

        text = " ".join(
            segment.text
            for segment in segments
        ).strip()

        latency = (
            time.perf_counter()
            - start
        )

        if not text:
            continue

        transcript = accumulator.update(
            text
        )

        print("\n" + "=" * 60)
        print(
            f"Latency: {latency:.2f}s"
        )
        print(
            f"Current: {text}"
        )
        print()
        print(
            "TRANSCRIPT:"
        )
        print(transcript)