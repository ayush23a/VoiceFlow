import subprocess

def type_text(text):
    subprocess.run([
        "ydotool",
        "type",
        "--key-delay",
        "5",
        text
    ])

    