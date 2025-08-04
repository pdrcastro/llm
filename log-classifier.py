import os
import time
import requests
import ollama
import sys

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
os.environ["OLLAMA_HOST"] = OLLAMA_HOST
MODEL_NAME = "llama2"
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
# Classify a single log line with improved prompt and fuzzy matching
# --------------------------------------------------------------------
def classify_log_line(line, model_name):
    prompt = (
        f"Classify the following log line into exactly one of these categories: {CATEGORIES}. "
        f"Reply with only one word from this list: {', '.join(CATEGORIES)}. "
        f"Log line: {line}"
    )
    try:
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])

        # Extract response text
        if isinstance(response, dict) and "message" in response and "content" in response["message"]:
            category = response["message"]["content"].strip().lower()
        elif isinstance(response, str):
            category = response.strip().lower()
        else:
            category = str(response).strip().lower()

        # Searching matching
        if "database" in category:
            return "database"
        elif "security" in category:
            return "security"
        elif "infra" in category or "network" in category or "system" in category:
            return "infrastructure"
        elif "application" in category:
            return "application"
        else:
            print(f"⚠️ Unknown category '{category}', defaulting to 'application'")
            return "application"

    except Exception as e:
        print(f"❌ Error classifying line: {e}")
        return "application"

# --------------------------------------------------------------------
# Process a single log file
# --------------------------------------------------------------------
def process_log_file(file_path, model_name):
    categorized_logs = {cat: [] for cat in CATEGORIES}

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            category = classify_log_line(line, model_name)
            categorized_logs[category].append(line)

    for cat, lines in categorized_logs.items():
        out_file = f"{cat}_logs.txt"
        with open(out_file, "a") as f_out:
            f_out.write("\n".join(lines) + "\n")
        print(f"📄 {len(lines)} lines appended to {out_file}")

# --------------------------------------------------------------------
# Process multiple log files in a directory
# --------------------------------------------------------------------
def process_directory(log_dir, model_name):
    for filename in os.listdir(log_dir):
        if filename.endswith(".log") or filename.endswith(".txt"):
            print(f"🔍 Processing {filename}...")
            process_log_file(os.path.join(log_dir, filename), model_name)

# --------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------
if __name__ == "__main__":
    wait_for_ollama(OLLAMA_HOST)
    model_name = wait_for_model(OLLAMA_HOST, model_name_prefix=MODEL_NAME, timeout=900, interval=10)

    log_path = sys.argv[1] if len(sys.argv) > 1 else "/logs/"

    if os.path.isdir(log_path):
        process_directory(log_path, model_name)
    elif os.path.isfile(log_path):
        process_log_file(log_path, model_name)
    else:
        print(f"❌ Invalid path: {log_path}")
