import socket
import time
from configs.settings import VOICEFLOW_PORT, BUBBLE_PORT
from core.audio.recorder import start_recording, stop_recording
from core.stt.transcriber import transcribe_audio
from core.llm.cleaner import clean_transcript
from core.injection.injector import type_text

HOST = "127.0.0.1"
is_recording = False


def show_bubble(message: str):
    """Sends a message to the PyQt overlay UI bubble over TCP socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(0.2)
            client.connect((HOST, BUBBLE_PORT))
            client.send(message.encode())
    except (ConnectionRefusedError, socket.timeout, OSError):
        # UI bubble is optional/not running; do not block typing workflow
        pass


def toggle_recording():
    global is_recording

    if not is_recording:
        show_bubble("🎤 Listening...")
        start_recording()
        is_recording = True
    else:
        audio_data = stop_recording()
        is_recording = False

        print("\n[VoiceFlow] Transcribing audio...")
        show_bubble("🧠 Transcribing...")

        try:
            raw_text = transcribe_audio(audio_data)
            raw_text = raw_text.strip()

            print(f"\n[Whisper Raw]: {raw_text}")

            if raw_text:
                show_bubble("✨ Polishing...")
                final_text = clean_transcript(raw_text)
                print(f"[Final Output]: {final_text}")

                show_bubble("⌨️ Typing...")
                time.sleep(0.1)
                show_bubble("hide")

                type_text(final_text)
            else:
                show_bubble("hide")

        except Exception as e:
            show_bubble("hide")
            print(f"[Error in pipeline]: {e}")


def main():
    print(f"VoiceFlow started on port {VOICEFLOW_PORT}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, VOICEFLOW_PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            with conn:
                toggle_recording()


if __name__ == "__main__":
    main()
