import time
import requests
import os
import ollama
from ollama._types import ResponseError

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
MODEL_NAME = "llama2"

def wait_for_ollama(timeout=60):
    url = f"{OLLAMA_HOST}/api/status"
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                print("Ollama server is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        print("Waiting for Ollama server...")
        time.sleep(2)
    raise RuntimeError("Timeout waiting for Ollama server")

def model_exists(client, model_name):
    try:
        # Try a lightweight request to check if model exists
        client.chat(model=model_name, messages=[{"role":"user","content":"hello"}])
        return True
    except ResponseError as e:
        if "not found" in str(e).lower():
            return False
        raise

def pull_model(client, model_name):
    print(f"Pulling model '{model_name}' ...")
    client.pull(model_name)
    print(f"Model '{model_name}' pulled successfully")

def ensure_model(host=OLLAMA_HOST, model_name=MODEL_NAME):
    wait_for_ollama()
    client = ollama.Client(host=host)
    if not model_exists(client, model_name):
        pull_model(client, model_name)
    else:
        print(f"Model '{model_name}' already available")
