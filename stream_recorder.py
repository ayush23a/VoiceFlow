import sounddevice as sd
import asyncio

SAMPLE_RATE = 16000
CHUNK_DURATION = 3.0

chunk_queue = asyncio.Queue()


async def audio_producer():

    loop = asyncio.get_running_loop()

    def callback(indata, frames, time, status):

        print("Chunk received")

        audio_chunk = indata.copy()

        asyncio.run_coroutine_threadsafe(
            chunk_queue.put(audio_chunk),
            loop
        )

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback,
        blocksize=int(SAMPLE_RATE * CHUNK_DURATION)
    ):

        print("Streaming audio...")

        while True:
            await asyncio.sleep(0.1)