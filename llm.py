import os
import sys
import ollama

CATEGORIES = ["infrastructure", "security", "database", "application"]

def classify_log_line(line):
    prompt = f"""
    Classify the following log line into one of these categories: {", ".join(CATEGORIES)}.
    Log line: {line}
    Respond with only the category name.
    """
    response = ollama.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
    return response['message']['content'].strip().lower()

def process_log_file(file_path):
    categorized_logs = {cat: [] for cat in CATEGORIES}

    with open(file_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            category = classify_log_line(line)
            if category in categorized_logs:
                categorized_logs[category].append(line.strip())

    # Save results
    for cat, lines in categorized_logs.items():
        with open(f"{cat}_logs.txt", "w") as out:
            out.write("\n".join(lines))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <log_file>")
        sys.exit(1)

    log_file = sys.argv[1]
    process_log_file(log_file)
    print("Logs categorized successfully.")
