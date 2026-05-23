from faster_whisper import WhisperModel

model = None


def get_model():
    global model

    if model is None:
        print("Loading voice model...")

        model = WhisperModel(
            "small",
            compute_type="int8"
        )

    return model


def transcribe_audio(audio_data):
    whisper_model = get_model()

    segments, info = whisper_model.transcribe(
        audio_data,
        language="en",
        task="transcribe",
        beam_size=1,
        best_of=1,
        temperature=0,
        vad_filter=True,
        condition_on_previous_text=False,
    )

    print(f"Detected language: {info.language}")

    transcription = ""

    for segment in segments:
        transcription += segment.text + " "

    return transcription.strip()