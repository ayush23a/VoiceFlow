import socket
from recorder import start_recording, stop_recording
from transcriber import transcribe_audio
from injector import type_text
import subprocess
import time

HOST = "127.0.0.1"
PORT = 65432

is_recording = False

def show_bubble(message):
    subprocess.Popen([
        "/home/ayushaman/Documents/Ayush_Code/Projects/wispr_linux/venv/bin/python",
        "/home/ayushaman/Documents/Ayush_Code/Projects/wispr_linux/ui_client.py",
        message
    ])

def toggle_recording():
    global is_recording

    if not is_recording:
        
        show_bubble("🎤 Listening...")
        start_recording()
        is_recording = True

    else:
        audio_data = stop_recording()

        is_recording = False

        print("\nTranscribing...")

        try:
            show_bubble("🧠 Transcribing...")
            text = transcribe_audio(audio_data)

            print("\nTranscription:")
            print(text)

            text = text.strip()

            if text:
                print("\nTyping text...")

                show_bubble("⌨️ Typing...")

                time.sleep(0.2)

                show_bubble("hide")

                # time.sleep(0.1)

                type_text(text)

        except Exception as e:
            print(f"Error: {e}")

        

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
