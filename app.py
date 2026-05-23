import socket
from recorder import start_recording, stop_recording
from transcriber import transcribe_audio
from injector import type_text

HOST = "127.0.0.1"
PORT = 65432

is_recording = False
def toggle_recording():
    global is_recording

    if not is_recording:
        start_recording()
        is_recording = True

    else:
        audio_data = stop_recording()

        is_recording = False

        print("\nTranscribing...")

        text = transcribe_audio(audio_data)

        print("\nTranscription:")
        print(text)

        text = text.strip()

        if text:
            print("\nTyping text...")
            type_text(text)


def main():
    print("VoiceFlow started.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))

        server.listen()

        while True:
            conn, addr = server.accept()

            with conn:
                toggle_recording()


if __name__ == "__main__":
    main()
