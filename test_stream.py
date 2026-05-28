import asyncio

from stream_recorder import (
    audio_producer,
    chunk_queue
)

from stream_transcriber import (
    transcriber_worker
)


async def main():

    producer_task = asyncio.create_task(
        audio_producer()
    )

    worker_task = asyncio.create_task(
        transcriber_worker(chunk_queue)
    )

    await asyncio.gather(
        producer_task,
        worker_task
    )


asyncio.run(main())