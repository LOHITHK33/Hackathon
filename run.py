import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import webbrowser

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.environ.get("NEXUS_MODEL", "qwen2.5:7b")
HOST = os.environ.get("NEXUS_HOST", "127.0.0.1")
PORT = int(os.environ.get("NEXUS_PORT", "8000"))

_ollama_proc = None


def say(msg):
    print(f"  nexus  {msg}", flush=True)


def ollama_running():
    try:
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def model_present():
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as r:
            data = json.load(r)
        names = [m.get("name", "") for m in data.get("models", [])]
        want = MODEL.split(":")[0]
        return any(n == MODEL or n.split(":")[0] == want for n in names)
    except Exception:
        return False


def ensure_ollama_installed():
    if shutil.which("ollama") is None:
        say("Ollama is not installed.")
        say("Install it from https://ollama.com/download, then run this again.")
        sys.exit(1)


def start_ollama():
    global _ollama_proc
    if ollama_running():
        say("Ollama server already running.")
        return
    say("Starting Ollama server...")
    env = dict(os.environ)
    env.setdefault("OLLAMA_NUM_PARALLEL", "4")
    _ollama_proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    for _ in range(40):
        if ollama_running():
            say("Ollama server is up.")
            return
        time.sleep(0.5)
    say("Ollama server did not start in time.")
    sys.exit(1)


def ensure_model():
    if model_present():
        say(f"Model '{MODEL}' is ready.")
        return
    say(f"Pulling model '{MODEL}' (first run only)...")
    result = subprocess.run(["ollama", "pull", MODEL])
    if result.returncode != 0:
        say(f"Failed to pull '{MODEL}'. Try a smaller model, e.g. NEXUS_MODEL=qwen2.5:3b")
        sys.exit(1)
    say(f"Model '{MODEL}' downloaded.")


def start_app():
    say(f"Starting Nexus at http://{HOST}:{PORT}")
    try:
        webbrowser.open(f"http://{HOST}:{PORT}")
    except Exception:
        pass
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False, log_level="info")


def cleanup():
    if _ollama_proc is not None:
        say("Shutting down Ollama server...")
        _ollama_proc.terminate()


def main():
    print()
    say("Booting the agent swarm stack...")
    ensure_ollama_installed()
    start_ollama()
    ensure_model()
    try:
        start_app()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()