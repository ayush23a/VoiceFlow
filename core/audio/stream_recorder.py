import sounddevice as sd
import asyncio
from configs.settings import SAMPLE_RATE, CHUNK_DURATION


chunk_queue = asyncio.Queue(maxsize=5)


async def audio_producer():

    loop = asyncio.get_running_loop()

    def callback(indata, frames, time_info, status):

        audio_chunk = indata.copy()

        if chunk_queue.full():
            return

        asyncio.run_coroutine_threadsafe(
            chunk_queue.put(audio_chunk),
            loop
        )

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback,
        blocksize=int(
            SAMPLE_RATE * CHUNK_DURATION
        )
    ):

        print("Streaming audio...")

        while True:
            await asyncio.sleep(0.1)