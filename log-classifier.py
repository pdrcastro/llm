import os
import time
import requests
import ollama
import sys

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
os.environ["OLLAMA_HOST"] = OLLAMA_HOST
CATEGORIES = ["infrastructure", "security", "database", "application"]

# --------------------------------------------------------------------
# Wait for Ollama server to be ready
# --------------------------------------------------------------------
def wait_for_ollama(host, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(host)
            if resp.status_code == 200:
                print("✅ Ollama server is up!")
                return
        except Exception:
            pass
        print("⏳ Waiting for Ollama server...")
        time.sleep(2)
    raise RuntimeError("Timeout waiting for Ollama server")

# --------------------------------------------------------------------
# Wait for model to be loaded and available
# --------------------------------------------------------------------
def wait_for_model(host, model_name_prefix="llama2", timeout=600, interval=10):
    url = f"{host}/api/tags"
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("models", [])
                model_names = [m.get("name", "") for m in models]
                print(f"📦 Available models: {model_names}")
                for name in model_names:
                    if name.startswith(model_name_prefix):
                        print(f"✅ Model '{name}' is ready!")
                        return name
        except Exception as e:
            print(f"Error checking models: {e}")
        print(f"⏳ Waiting for model '{model_name_prefix}'...")
        time.sleep(interval)
    raise RuntimeError(f"Timeout waiting for model '{model_name_prefix}'")

# --------------------------------------------------------------------
# Classify a single log line
# --------------------------------------------------------------------
def classify_log_line(line, model_name):
    prompt = (
        f"Classify the following log line into one of these categories: {CATEGORIES}. "
        f"Return only the category name.\nLog line: {line}"
    )
    try:
        response = ollama.chat(model_name, prompt)
        category = response.strip().lower() if isinstance(response, str) else response.result.strip().lower()
        if category in CATEGORIES:
            return category
        else:
            print(f"Warning: Received unknown category '{category}' from model.")
            return "application"
    except Exception as e:
        print(f"Error classifying line: {e}")
        return "application"

# --------------------------------------------------------------------
# Process entire log file
# --------------------------------------------------------------------
def process_log_file(file_path, model_name):
    categorized_logs = {cat: [] for cat in CATEGORIES}

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            category = classify_log_line(line, model_name)
            if category in categorized_logs:
                categorized_logs[category].append(line)
            else:
                print(f"Warning: Unknown category '{category}' from line: {line}")

    for cat, lines in categorized_logs.items():
        out_file = f"{cat}_logs.txt"
        with open(out_file, "w") as f_out:
            f_out.write("\n".join(lines))
        print(f"Wrote {len(lines)} lines to {out_file}")

# --------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python log-classifier.py <log_file_path>")
        sys.exit(1)

    wait_for_ollama(OLLAMA_HOST)
    model_name = wait_for_model(OLLAMA_HOST, model_name_prefix="llama2", timeout=900, interval=10)

    log_file = sys.argv[1]
    if not os.path.isfile(log_file):
        print(f"Log file {log_file} does not exist!")
        sys.exit(1)

    process_log_file(log_file, model_name)
    print("✅ Log classification complete.")