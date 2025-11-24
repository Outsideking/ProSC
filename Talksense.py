"""
run.py - TalkSense Full Client + Web Dashboard + Auto-Update
รวม STT, TTS, Web Dashboard, Auto-Update ในไฟล์เดียว
"""

import threading
import time
import subprocess
import sys
import os
from flask import Flask, request, jsonify, render_template_string

# -------------------------
# Speak / TalkSense Client
# -------------------------
try:
    import pyttsx3
    import speech_recognition as sr
except ImportError:
    print("ติดตั้ง pyttsx3, speechrecognition, pyaudio ก่อนใช้งาน")
    sys.exit()

class TalkSenseClient:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

    def say(self, text):
        print(f"[TalkSense] {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("[TalkSense] Listening...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"[TalkSense] Heard: {text}")
                return text
            except sr.UnknownValueError:
                print("[TalkSense] Could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"[TalkSense] Recognition error: {e}")
                return ""

# -------------------------
# Web Dashboard
# -------------------------
app = Flask(__name__)
client = TalkSenseClient()

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>TalkSense Dashboard</title>
</head>
<body>
<h1>TalkSense Dashboard</h1>
<form action="/say" method="get">
    Text to speak: <input type="text" name="text">
    <input type="submit" value="Speak">
</form>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/say")
def say_text():
    text = request.args.get("text", "")
    if text:
        client.say(text)
        return jsonify({"success": True, "text": text})
    return jsonify({"success": False, "error": "No text provided"})

def run_web():
    app.run(host="0.0.0.0", port=5000)

# -------------------------
# Auto-update Function
# -------------------------
def auto_update(repo_path="."):
    while True:
        try:
            print("[AutoUpdate] Checking for updates...")
            result = subprocess.run(["git", "pull"], cwd=repo_path, capture_output=True, text=True)
            print(f"[AutoUpdate] {result.stdout}")
            if "Already up to date." not in result.stdout:
                print("[AutoUpdate] Updates found, restarting...")
                os.execv(sys.executable, ["python"] + sys.argv)
        except Exception as e:
            print(f"[AutoUpdate] Error: {e}")
        time.sleep(60)  # check every 60 seconds

# -------------------------
# Main Loop (Voice Listen)
# -------------------------
def voice_loop():
    while True:
        command = client.listen()
        if command:
            client.say(f"You said: {command}")
        time.sleep(1)

# -------------------------
# Main
# -------------------------
def main():
    print("[TalkSense] Starting TalkSense Client...")

    # Run web dashboard
    threading.Thread(target=run_web, daemon=True).start()
    print("Web dashboard running at http://localhost:5000")

    # Run auto-update
    threading.Thread(target=auto_update, daemon=True).start()

    # Run voice listening loop
    voice_loop()

if __name__ == "__main__":
    main()
