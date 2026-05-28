# VoiceFlow

VoiceFlow is a lightweight local voice-to-text dictation tool for Linux. It records audio from your microphone, transcribes it with Faster Whisper, and types the resulting text into the currently focused application using `ydotool`.

## What it does

- Starts a local TCP server on `127.0.0.1:65432`
- Toggles microphone recording on each client connection
- Captures mono audio at `16 kHz`
- Transcribes speech with a cached Whisper model
- Types the final transcript into the active window

## How it works

The project is split into four small parts:

- `app.py` starts the server and handles the recording/transcription lifecycle.
- `recorder.py` opens a `sounddevice.InputStream`, stores microphone chunks, and returns the recorded audio as a NumPy array.
- `transcriber.py` loads `faster_whisper.WhisperModel("small", compute_type="int8")` once and reuses it for transcription.
- `injector.py` sends the transcript to `ydotool type`.

The toggle flow is simple:

1. Run `app.py`.
2. Run `toggle.py` once to start recording.
3. Run `toggle.py` again to stop recording.
4. The audio is transcribed and typed automatically.

## Repository structure

```text
VoiceFlow/
├── app.py
├── injector.py
├── recorder.py
├── toggle.py
├── transcriber.py
├── requirements.txt
└── .gitignore
```

## Requirements

### Python packages

The current `requirements.txt` lists:

- `faster-whisper`
- `sounddevice`
- `numpy`
- `pynput`
- `scipy`
- `socket`

### System dependencies

You also need:

- A working microphone input device
- `ydotool` and its daemon/service
- Audio backend support for `sounddevice` / PortAudio
- Linux, since `ydotool` is the typing backend used by the project

> `ydotool` writes input through the Linux input/uinput stack and relies on a persistent background daemon. Make sure it is installed and working before using VoiceFlow.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ayush23a/VoiceFlow.git
cd VoiceFlow
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and configure `ydotool`

Install `ydotool` using your distribution’s package manager or from source, then ensure its daemon is running and has permission to access `/dev/uinput`.

## Usage

### Terminal 1: start the VoiceFlow server

```bash
python app.py
```

You should see:

```text
VoiceFlow started.
```

### Terminal 2: trigger recording

Run:

```bash
python toggle.py
```

This opens a local socket connection to the server and starts recording.

### Terminal 2 again: stop recording and transcribe

Run the same command again:

```bash
python toggle.py
```

This time the recording stops, the model transcribes the audio, and the text is typed into the focused application.

## Transcription settings

VoiceFlow currently uses these transcription parameters:

- Model: `small`
- Compute type: `int8`
- Language: `en`
- Task: `transcribe`
- Beam size: `1`
- Best of: `1`
- Temperature: `0`
- VAD filtering: enabled
- Previous text conditioning: disabled

These defaults favor low overhead and a simple live dictation workflow.

## Notes and limitations

- The project types into whatever window is currently focused.
- The current implementation is single-user and local-only.
- `toggle.py` does not send a command payload; it only opens a socket connection to flip the recording state.
- The server is currently hardcoded to `127.0.0.1:65432`.
- The project is optimized for English speech.

## Troubleshooting

### Nothing is typed after transcription

Check that:

- `ydotool` is installed
- `ydotoold` is running
- The daemon can access `/dev/uinput`
- The target window is focused

### No microphone input

Check your input device permissions and verify that your system can access the microphone from Python.

### Transcription is slow

The model is loaded on first use and then reused. The first transcription may take longer because the model has to initialize.

### Text appears in the wrong place

VoiceFlow types into the active window. Make sure the correct input field is focused before you stop recording.

## Extending the project

Possible next improvements:

- Add a real keyboard shortcut instead of a separate toggle script
- Support richer commands or punctuation post-processing
- Add configurable model size and language options
- Add a simple status UI
- Add error handling around audio, socket, and typing failures

## License

No license file is currently included in the repository. Add one before publishing or distributing the project.

---

If you want, I can also turn this into a more polished README with badges, screenshots, and a command-line quick start section.
