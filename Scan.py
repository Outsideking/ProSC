# File: scan.py
import requests, feedparser, json, threading, queue, time
from bs4 import BeautifulSoup

# --- Atomic-level mapping ---
atomic_map = {chr(i): f"A{i}" for i in range(65,91)}
atomic_map[" "] = "__"
reverse_map = {v:k for k,v in atomic_map.items()}

def encode_atomic(text):
    return [atomic_map.get(c.upper(),"??") for c in text]

def decode_atomic(seq):
    return "".join([reverse_map.get(u,"?") for u in seq])

# --- Online Scanners ---
def scan_website(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return f"Error: {e}"

def scan_rss(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        return " ".join([entry.title + " " + entry.summary for entry in feed.entries])
    except Exception as e:
        return f"Error: {e}"

# --- Knowledge Base ---
KB_FILE = "prosc_kb.json"
def save_kb(data):
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def load_kb():
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# --- Streaming Scanner Thread ---
class StreamingScanner(threading.Thread):
    def __init__(self, sources, interval=60):
        super().__init__()
        self.sources = sources
        self.interval = interval
        self.kb = load_kb()
        self.queue = queue.Queue()
        self.running = True

    def run(self):
        while self.running:
            for src in self.sources:
                if src["type"] == "website":
                    text = scan_website(src["url"])
                elif src["type"] == "rss":
                    text = scan_rss(src["url"])
                elif src["type"] == "twitter":
                    text = f"Simulated Twitter: {src['handle']}"
                elif src["type"] == "discord":
                    text = f"Simulated Discord: {src['channel']}"
                elif src["type"] == "telegram":
                    text = f"Simulated Telegram: {src['chat']}"
                else:
                    continue
                atomic_data = encode_atomic(text)
                self.kb[src.get("url", src.get("handle", src.get("channel", src.get("chat",""))))] = atomic_data
                self.queue.put((src, atomic_data))
            save_kb(self.kb)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def fetch_latest(self):
        items = []
        while not self.queue.empty():
            items.append(self.queue.get())
        return items

# --- Multi-AI Modules Placeholder ---
def gpt_module(atomic_data): return [u+"G" for u in atomic_data]
def deebspeak_module(atomic_data): return [u+"D" for u in atomic_data]
def gbnai_module(atomic_data): return [u+"N" for u in atomic_data]

def merge_atomic(*modules):
    combined = []
    max_len = max(len(m) for m in modules)
    for i in range(max_len):
        for m in modules:
            if i < len(m):
                combined.append(m[i])
                break
    return combined

def generate_auto_link(module_name):
    return f"# Auto-link: {module_name}\nregister_module('{module_name}')\n"

# --- Example Usage ---
if __name__ == "__main__":
    sources = [
        {"type":"website", "url":"https://example.com"},
        {"type":"rss", "url":"https://news.google.com/rss"},
        {"type":"twitter", "handle":"@example"},
        {"type":"discord", "channel":"#general"},
        {"type":"telegram", "chat":"@examplechat"}
    ]

    scanner = StreamingScanner(sources, interval=300)
    scanner.start()
    print("ProSC Full Ultimate Streaming Multi-AI Repo (scan.py) running...")

    try:
        while True:
            time.sleep(10)
            latest = scanner.fetch_latest()
            for src, atomic in latest:
                merged = merge_atomic(gpt_module(atomic), deebspeak_module(atomic), gbnai_module(atomic))
                decoded_preview = decode_atomic(merged[:100])
                print(f"[Preview] {src}: {decoded_preview}...")
                link_code = generate_auto_link("MergedModule")
                print(f"Generated Auto-Link:\n{link_code}")
    except KeyboardInterrupt:
        scanner.stop()
        print("ProSC Ultimate Streaming Repo (scan.py) stopped.")
# File: prosc_full_ultimate_streaming.py

import requests, feedparser, json, threading, queue, time
from bs4 import BeautifulSoup

# --- Atomic-level mapping ---
atomic_map = {chr(i): f"A{i}" for i in range(65,91)}
atomic_map[" "] = "__"
reverse_map = {v:k for k,v in atomic_map.items()}

def encode_atomic(text):
    return [atomic_map.get(c.upper(),"??") for c in text]

def decode_atomic(seq):
    return "".join([reverse_map.get(u,"?") for u in seq])

# --- Online Scanners ---
def scan_website(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return f"Error: {e}"

def scan_rss(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        return " ".join([entry.title + " " + entry.summary for entry in feed.entries])
    except Exception as e:
        return f"Error: {e}"

# --- Knowledge Base ---
KB_FILE = "prosc_kb.json"
def save_kb(data):
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def load_kb():
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# --- Streaming Scanner Thread ---
class StreamingScanner(threading.Thread):
    def __init__(self, sources, interval=60):
        super().__init__()
        self.sources = sources
        self.interval = interval
        self.kb = load_kb()
        self.queue = queue.Queue()
        self.running = True

    def run(self):
        while self.running:
            for src in self.sources:
                if src["type"] == "website":
                    text = scan_website(src["url"])
                elif src["type"] == "rss":
                    text = scan_rss(src["url"])
                elif src["type"] == "twitter":
                    text = f"Simulated Twitter: {src['handle']}"
                elif src["type"] == "discord":
                    text = f"Simulated Discord: {src['channel']}"
                elif src["type"] == "telegram":
                    text = f"Simulated Telegram: {src['chat']}"
                else:
                    continue
                atomic_data = encode_atomic(text)
                self.kb[src.get("url", src.get("handle", src.get("channel", src.get("chat",""))))] = atomic_data
                self.queue.put((src, atomic_data))
            save_kb(self.kb)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def fetch_latest(self):
        items = []
        while not self.queue.empty():
            items.append(self.queue.get())
        return items

# --- Multi-AI Modules Placeholder ---
def gpt_module(atomic_data): return [u+"G" for u in atomic_data]
def deebspeak_module(atomic_data): return [u+"D" for u in atomic_data]
def gbnai_module(atomic_data): return [u+"N" for u in atomic_data]

def merge_atomic(*modules):
    combined = []
    max_len = max(len(m) for m in modules)
    for i in range(max_len):
        for m in modules:
            if i < len(m):
                combined.append(m[i])
                break
    return combined

def generate_auto_link(module_name):
    return f"# Auto-link: {module_name}\nregister_module('{module_name}')\n"

# --- Example Usage ---
if __name__ == "__main__":
    sources = [
        {"type":"website", "url":"https://example.com"},
        {"type":"rss", "url":"https://news.google.com/rss"},
        {"type":"twitter", "handle":"@example"},
        {"type":"discord", "channel":"#general"},
        {"type":"telegram", "chat":"@examplechat"}
    ]

    scanner = StreamingScanner(sources, interval=300)
    scanner.start()
    print("ProSC Full Ultimate Streaming Multi-AI Repo running...")

    try:
        while True:
            time.sleep(10)
            latest = scanner.fetch_latest()
            for src, atomic in latest:
                # Merge atomic with multi-AI placeholders
                merged = merge_atomic(gpt_module(atomic), deebspeak_module(atomic), gbnai_module(atomic))
                decoded_preview = decode_atomic(merged[:100])
                print(f"[Preview] {src}: {decoded_preview}...")
                link_code = generate_auto_link("MergedModule")
                print(f"Generated Auto-Link:\n{link_code}")
    except KeyboardInterrupt:
        scanner.stop()
        print("ProSC Ultimate Streaming Repo stopped.")
