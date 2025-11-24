"""
run.py - Speak Full Client + Web Dashboard
รวม STT, TTS, และ Web Dashboard ไว้ในไฟล์เดียว
"""

import threading
import time
from flask import Flask, request, jsonify, render_template_string

# -------------------------
# Speak Client
# -------------------------
try:
    import pyttsx3
    import speech_recognition as sr
except ImportError:
    print("ติดตั้ง pyttsx3, speechrecognition, pyaudio ก่อนใช้งาน")
    exit()

class SpeakClient:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

    def say(self, text):
        print(f"[Speak] {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("[Speak] Listening...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"[Speak] Heard: {text}")
                return text
            except sr.UnknownValueError:
                print("[Speak] Could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"[Speak] Recognition error: {e}")
                return ""

# -------------------------
# Web Dashboard
# -------------------------
app = Flask(__name__)
client = SpeakClient()

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Speak Dashboard</title>
</head>
<body>
<h1>Speak Client Dashboard</h1>
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
    print("[Speak] Starting Speak Client...")

    # Run web dashboard in separate thread
    threading.Thread(target=run_web, daemon=True).start()
    print("Web dashboard running at http://localhost:5000")

    # Run voice listening loop
    voice_loop()

if __name__ == "__main__":
    main()
