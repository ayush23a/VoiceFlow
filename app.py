from recorder import start_recording, stop_recording
from transcriber import transcribe_audio
from injector import type_text


def main():
    
    print(
        "\nPress:\n"
        "'r' -> start recording\n"
        "'s' -> stop recording\n"
        "'q' -> quit\n\n"
        )
    
    while True:

        command = input()

        if command=='r':
            start_recording()
        
        elif command =='s':

            audio_data = stop_recording()

            print("\nTranscribing...")
            text = transcribe_audio(audio_data)
            
            print("\nTranscription")
            print(text)

            text = text.strip()
            
            if text:
                print("\n Typing text")
                type_text(text)
            
        elif command=='q':
            break


if __name__ == "__main__":
    main()
