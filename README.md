# VoiceFlow 🎙️✨

**VoiceFlow** is a lightning-fast, privacy-first voice dictation system for Linux. Inspired by modern voice-first tools like Wispr Flow and Superwhisper, VoiceFlow turns your spoken words into polished, punctuated text and automatically types it into whatever application is currently focused—whether it's a code editor, browser, terminal, or chat client.

It runs locally with **Faster Whisper** (CTranslate2 INT8) for low-latency automatic speech recognition, optionally cleans up stutters and homophones via **Groq LLM** with an ultra-low timeout fail-safe, displays a sleek non-intrusive **PyQt6 floating status pill**, and injects keystrokes system-wide via **ydotool** on both **Wayland** and **X11**.

---

## ✨ Key Features

- ⚡ **Near-Instant Local Transcription**: Powered by `faster-whisper` (`small` model with `int8` quantization) using VAD (Voice Activity Detection) filtering to eliminate silence and noise.
- 🧠 **AI Polish & Punctuation**: Context-aware speech refinement using fast LLMs on Groq (`qwen/qwen3.8-27b`, `llama-3.3-70b-versatile`, etc.) to automatically fix hesitations, grammatical slips, and homophones while preserving technical terminology and code.
- 🛡️ **Zero-Lag Fail-Safe**: Fast-fail design with zero retries and configurable timeout (`GROQ_TIMEOUT=2.5s`). If offline, slow, or disabled, VoiceFlow instantly falls back to raw Whisper output without stalling.
- ⌨️ **System-Wide Text Injection**: Injects text into the currently focused window using `ydotool` through Linux `/dev/uinput`, supporting modern Wayland compositors (Hyprland, Sway, GNOME, KDE) as well as X11.
- 🫧 **Floating Status Pill**: Non-activating, stay-on-top, frameless PyQt6 overlay bubble in the corner of your screen showing live operational status (`Listening...`, `Transcribing...`, `Polishing...`, `Typing...`) without stealing window focus.
- 🔄 **One-Touch Hotkey Toggle**: Simple socket-driven trigger designed to be bound to a single keyboard shortcut (e.g., `Super+D` or `Caps Lock`).
- 🛠️ **Daemon-Ready**: Includes a native systemd user service (`voiceflow.service`) to run quietly in the background upon login.
- 🔬 **Continuous Streaming Prototype**: Experimental modular audio producer and consumer with n-gram sliding-window deduplication (`TranscriptAccumulator`) for real-time streaming dictation research.

---

## 🏗️ Architecture & Process Flow

```text
               ┌────────────────────────────────────────────────────────┐
               │                  User Press Hotkey                     │
               │           (e.g., Super + D in Hyprland / GNOME)        │
               └──────────────────────────┬─────────────────────────────┘
                                          │ executes
                                          ▼
                                    toggle.py
                                          │ TCP connect (127.0.0.1:65432)
                                          ▼
                                     ┌─────────┐
                                     │ app.py  │
                                     └────┬────┘
                                          │
            ┌─────────────────────────────┴─────────────────────────────┐
            │                                                           │
   [If NOT recording]                                           [If ALREADY recording]
            │                                                           │
            ├─► Sends "🎤 Listening..." to ui.py (port 65433)           ├─► audio_data = stop_recording()
            ├─► Starts sounddevice InputStream                          ├─► Sends "🧠 Transcribing..." to ui.py
            └─► Sets is_recording = True                                ├─► raw_text = transcribe_audio(audio_data)
                                                                        │
                                                                        ├─► If raw_text is valid:
                                                                        │     ├── Sends "✨ Polishing..." to ui.py
                                                                        │     ├── final_text = clean_transcript(raw_text)
                                                                        │     │     ├── Groq API cleans & punctuates
                                                                        │     │     └── Fallback to raw_text on timeout/error
                                                                        │     ├── Sends "⌨️ Typing..." to ui.py
                                                                        │     ├── Sends "hide" to ui.py
                                                                        │     └── type_text(final_text) via ydotool
                                                                        │
                                                                        └─► Else:
                                                                              └── Sends "hide" to ui.py
```

### Detailed Component Roles

| Component | Path | Responsibility |
| :--- | :--- | :--- |
| **Server & Orchestrator** | `app.py` | Runs TCP server (port `65432`), tracks recording state, coordinates STT, LLM cleaning, UI notifications, and text typing. |
| **Toggle Trigger** | `toggle.py` | Minimal socket client connecting to `app.py` to toggle recording start/stop. |
| **Audio Recorder** | `core/audio/recorder.py` | Captures 16 kHz mono audio via `sounddevice` into buffered float32 NumPy arrays. |
| **Stream Recorder** | `core/audio/stream_recorder.py` | Async streaming producer collecting 1-second chunks into an `asyncio.Queue`. |
| **Whisper STT** | `core/stt/transcriber.py` | Loads and runs `faster-whisper` (`small`, `int8`, VAD-filtered) in memory. |
| **Streaming Transcriber** | `core/stt/stream_transcriber.py` | Rolling-buffer transcriber worker for live streaming inference. |
| **Transcript Accumulator** | `core/stt/transcript_accumulator.py` | Suffix/prefix n-gram overlap matching algorithm to deduplicate streaming speech segments. |
| **LLM Cleaner** | `core/llm/cleaner.py` | Fast-fail Groq client cleaning stutters, formatting text, and adding punctuation. |
| **Input Injector** | `core/injection/injector.py` | Invokes `ydotool type --key-delay 5` to type text into the active window. |
| **Overlay UI** | `core/ui/ui.py` | Frameless, translucent PyQt6 bubble listening on port `65433`. |
| **UI Client** | `core/ui/ui_client.py` | CLI socket helper to send custom messages to the overlay bubble. |
| **Configuration** | `configs/settings.py` | Central settings loader reading defaults and `.env` variables. |
| **Systemd Service** | `services/voiceflow.service` | Systemd user service unit for background daemon execution. |

---

## 📂 Repository Structure

```text
VoiceFlow/
├── app.py                         # Main server daemon & pipeline orchestrator
├── toggle.py                      # Global hotkey trigger script
├── start_voiceflow.sh             # Shell script to activate venv and run app.py
├── requirements.txt               # Python package dependencies
├── .env.example                   # Template environment variables
├── .env                           # Local environment configuration (API keys, ports)
├── configs/
│   └── settings.py                # Global configuration & environment loader
├── core/
│   ├── audio/
│   │   ├── recorder.py            # Push-to-talk audio capture (sounddevice)
│   │   └── stream_recorder.py     # Continuous asyncio audio chunk streamer
│   ├── injection/
│   │   └── injector.py            # Virtual keyboard input via ydotool
│   ├── llm/
│   │   ├── __init__.py
│   │   └── cleaner.py             # Groq LLM post-processing & fallback logic
│   ├── stt/
│   │   ├── transcriber.py         # Faster-Whisper batch transcription
│   │   ├── stream_transcriber.py  # Streaming inference worker with rolling buffer
│   │   └── transcript_accumulator.py # Overlap deduplication algorithm
│   └── ui/
│       ├── ui.py                  # PyQt6 floating status pill (overlay)
│       └── ui_client.py           # Socket client for testing UI states
├── services/
│   └── voiceflow.service          # Systemd user unit definition
└── tests/
    └── test_stream.py             # Async streaming audio/STT pipeline test
```

---

## 📋 Prerequisites & System Dependencies

### 1. Linux Environment
VoiceFlow is designed for Linux systems supporting `/dev/uinput` (Wayland or X11).

### 2. Audio Library & PortAudio
Ensure PortAudio is installed so `sounddevice` can access your microphone:
- **Arch Linux / Manjaro**:
  ```bash
  sudo pacman -S portaudio
  ```
- **Ubuntu / Debian**:
  ```bash
  sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev
  ```
- **Fedora**:
  ```bash
  sudo dnf install portaudio portaudio-devel
  ```

### 3. `ydotool` (Virtual Keyboard Typing)
`ydotool` communicates with the Linux `/dev/uinput` device to type characters regardless of whether you are running GNOME, KDE, Hyprland, Sway, or X11.

- **Install `ydotool`**:
  - Arch Linux: `sudo pacman -S ydotool`
  - Ubuntu / Debian: `sudo apt install ydotool`
  - Fedora: `sudo dnf install ydotool`

- **Ensure `ydotoold` is running & permissions are set**:
  The user running VoiceFlow must have permission to access `/dev/uinput`.
  ```bash
  # Option A: Start user service (recommended on modern distros)
  systemctl --user enable --now ydotool

  # Option B: Run daemon manually in background with root/uinput group
  sudo ydotoold &
  ```
  > **Tip**: If `ydotool` complains about permissions, ensure your user is in the `input` group (`sudo usermod -aG input $USER`) and that `/dev/uinput` has appropriate udev rules.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ayush23a/VoiceFlow.git
cd VoiceFlow
```

### 2. Set Up Virtual Environment

You can use standard Python `venv` or `uv`:

```bash
python3 -m venv venv
source venv/bin/activate
```

*(Or using `uv`)*:
```bash
uv venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example `.env` file and customize your settings:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
# Groq API Configuration (Optional but recommended for smart punctuation & cleanup)
GROQ_API_KEY=your_groq_api_key_here

# Groq Model (e.g. qwen/qwen3.8-27b, llama-3.3-70b-versatile, etc.)
GROQ_MODEL=qwen/qwen3.8-27b

# Timeout in seconds before falling back to raw Whisper output
GROQ_TIMEOUT=2.5

# Temperature (0.0 for deterministic cleanup)
GROQ_TEMPERATURE=0.0

# Enable/Disable Groq post-processing
GROQ_ENABLED=true

# Custom TCP Ports (Optional)
VOICEFLOW_PORT=65432
BUBBLE_PORT=65433
```

> **Note**: If `GROQ_API_KEY` is omitted or `GROQ_ENABLED=false`, VoiceFlow automatically skips LLM cleanup and directly injects raw Whisper transcription.

---

## 🎮 How to Run VoiceFlow

### Step 1: Start the Floating Status Pill (Optional)
In a terminal (or your background startup script), launch the PyQt6 status bubble:
```bash
source venv/bin/activate
python core/ui/ui.py
```
*(The status pill will remain hidden in the background until voice events occur).*

### Step 2: Start the VoiceFlow Daemon
In another terminal (or background service):
```bash
source venv/bin/activate
python app.py
```
Output:
```text
VoiceFlow started on port 65432...
```

### Step 3: Trigger Dictation
Run `toggle.py` to start and stop recording:

```bash
# First execution: Starts listening
python toggle.py

# Speak into your microphone...

# Second execution: Stops recording, transcribes, refines, and types!
python toggle.py
```

---

## ⌨️ Setting Up a Global Hotkey

To achieve a seamless "push-to-talk" or "toggle-to-talk" experience, map `toggle.py` to a global keyboard shortcut in your desktop environment or window manager.

### Hyprland (`~/.config/hypr/hyprland.conf`)
```ini
# Toggle voice dictation with Super + D
bind = $mainMod, D, exec, /home/ayushaman/Documents/Ayush_Code/Projects/wispr_linux/venv/bin/python /home/ayushaman/Documents/Ayush_Code/Projects/wispr_linux/toggle.py
```

### Sway / i3 (`~/.config/sway/config` or `~/.config/i3/config`)
```ini
# Toggle voice dictation with Mod4 + d
bindsym $mod+d exec /home/ayushaman/Documents/Ayush_Code/Projects/wispr_linux/venv/bin/python /home/ayushaman/Documents/Ayush_Code/Projects/wispr_linux/toggle.py
```

### GNOME
1. Open **Settings** → **Keyboard** → **View and Customize Shortcuts** → **Custom Shortcuts**.
2. Click **+** to add a new shortcut:
   - **Name**: `VoiceFlow Toggle`
   - **Command**: `/path/to/VoiceFlow/venv/bin/python /path/to/VoiceFlow/toggle.py`
   - **Shortcut**: `Super + D` (or any shortcut of choice).

### KDE Plasma
1. Open **System Settings** → **Shortcuts** → **Custom Shortcuts**.
2. Add **New Global Shortcut** → **Command/URL**.
3. Set the trigger key and set the action to `/path/to/VoiceFlow/venv/bin/python /path/to/VoiceFlow/toggle.py`.

---

## 🔄 Running as a Background Systemd Service

VoiceFlow includes a systemd user unit in `services/voiceflow.service`. To run VoiceFlow automatically upon login:

1. Update the paths in `services/voiceflow.service` to match your user and virtual environment:
   ```ini
   [Unit]
   Description=VoiceFlow Daemon
   After=graphical-session.target

   [Service]
   Type=simple
   WorkingDirectory=/home/YOUR_USER/path/to/VoiceFlow
   ExecStart=/home/YOUR_USER/path/to/VoiceFlow/venv/bin/python app.py
   Restart=always
   RestartSec=2

   [Install]
   WantedBy=default.target
   ```

2. Copy the unit file to your systemd user directory:
   ```bash
   mkdir -p ~/.config/systemd/user
   cp services/voiceflow.service ~/.config/systemd/user/
   ```

3. Reload and enable the service:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now voiceflow.service
   ```

4. Check the service status and logs:
   ```bash
   systemctl --user status voiceflow.service
   journalctl --user -u voiceflow.service -f
   ```

---

## ⚙️ Configuration Reference

All settings can be configured via environment variables in `.env` or adjusted in `configs/settings.py`:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `SAMPLE_RATE` | `16000` | Audio sampling rate in Hz (standard for Whisper models). |
| `CHANNELS` | `1` | Audio channels (mono). |
| `CHUNK_DURATION` | `1` | Duration (seconds) of audio chunks for streaming. |
| `ROLLING_BUFFER_SIZE` | `3` | Number of chunks in the rolling streaming buffer. |
| `QUEUE_MAXSIZE` | `5` | Maximum queue size for async streaming. |
| `WHISPER_MODEL` | `"small"` | Whisper model size (`tiny`, `base`, `small`, `medium`, `large-v3`). |
| `COMPUTE_TYPE` | `"int8"` | CTranslate2 quantization type (`int8`, `float16`, `float32`). |
| `BEAM_SIZE` | `1` | Whisper beam search size (1 = greedy decoding, lowest latency). |
| `LANGUAGE` | `"en"` | Language code for transcription. |
| `VAD_FILTER` | `True` | Silero VAD filtering to strip silence before transcription. |
| `VOICEFLOW_PORT` | `65432` | TCP port for the VoiceFlow server daemon. |
| `BUBBLE_PORT` | `65433` | TCP port for the PyQt6 status overlay bubble. |
| `GROQ_API_KEY` | `""` | API key for Groq Cloud. |
| `GROQ_MODEL` | `"qwen/qwen3.8-27b"` | Groq LLM model name for post-processing. |
| `GROQ_TIMEOUT` | `2.5` | Timeout (seconds) before falling back to raw Whisper output. |
| `GROQ_TEMPERATURE` | `0.0` | Sampling temperature for deterministic cleanup. |
| `GROQ_ENABLED` | `true` | Boolean flag to enable or disable Groq post-processing. |

---

## 🧪 Experimental Streaming Pipeline

The repository includes an experimental real-time streaming pipeline located in `core/audio/stream_recorder.py`, `core/stt/stream_transcriber.py`, and `core/stt/transcript_accumulator.py`.

### How it works:
1. `audio_producer()` captures continuous 1-second chunks and feeds an `asyncio.Queue`.
2. `transcriber_worker()` maintains a 3-second sliding window buffer (`deque(maxlen=3)`).
3. Every 2 seconds, audio is concatenated and transcribed by Faster Whisper.
4. `TranscriptAccumulator` performs n-gram suffix/prefix overlap matching across consecutive windows to seamlessly append newly uttered words without duplicating previously recognized phrases.

To test this experimental streaming pipeline in your terminal:
```bash
python tests/test_stream.py
```

---

## 🔧 Troubleshooting

### 1. `ydotool: /dev/uinput: Permission denied`
- Ensure your user belongs to the `input` group:
  ```bash
  sudo usermod -aG input $USER
  ```
- Alternatively, run `ydotoold` as root or set up a udev rule:
  ```bash
  echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/80-uinput.rules
  sudo udevadm control --reload-rules && sudo udevadm trigger
  ```

### 2. Nothing is typed after transcription
- Check if `ydotoold` is active:
  ```bash
  pgrep -l ydotoold || systemctl --user status ydotool
  ```
- Make sure the target text field or window is focused before the transcription completes.

### 3. Microphone not recording / PortAudio error
- Verify that your microphone is recognized by ALSA / PulseAudio / PipeWire:
  ```bash
  python -c "import sounddevice as sd; print(sd.query_devices())"
  ```
- Ensure microphone permissions are granted and not muted in `pavucontrol` or `wpctl`.

### 4. Floating Overlay UI does not show up
- Ensure you have launched `python core/ui/ui.py`.
- If Wayland blocks window positioning, PyQt6 defaults to primary screen coordinates. `ui.py` uses `WA_ShowWithoutActivating` and `WindowDoesNotAcceptFocus` to prevent stealing input focus.

### 5. Groq Fallback Warnings in Logs
- If you see `[LLM Cleaner Fallback] Reverting to raw Whisper transcript`:
  - Verify that `GROQ_API_KEY` is properly set in your `.env`.
  - Check your internet connectivity.
  - If your network latency to Groq is high, consider increasing `GROQ_TIMEOUT` in `.env` (e.g., to `3.5`).

---

## 📄 License

This project is open-source under the [MIT License](LICENSE) (or applicable project license).
