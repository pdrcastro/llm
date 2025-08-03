# LLM
LLM for Monitoring Solution

## Purpose
log-classifier.py is a log classification tool that uses the Ollama LLaMA2 model to categorize each log line into one of four categories:

- infrastructure
- security
- database
- application

# Log Classifier with Ollama (LLaMA2)

This project is a **log classification tool** that uses the [Ollama](https://ollama.ai) **LLaMA2** model to categorize log lines into specific categories.

## 📌 Features
- Connects to an **Ollama server**.
- Uses the **LLaMA2** model to classify logs.
- Supports the following categories:
  - `infrastructure`
  - `security`
  - `database`
  - `application`
- Writes categorized logs to separate files.

---

## 🚀 How It Works
1. **Waits for the Ollama server** to start.
2. **Checks the model** (`llama2`) is available.
3. **Reads each log line** from the given file.
4. Sends each line to the LLaMA2 model for classification.
5. Groups logs into categories.
6. Saves results in separate text files.

---

## 📂 Output
The tool generates:



## Run Container
### Build the image
docker build -t log-classifier .
docker build -f Dockerfile-ollama -t custom-ollama .


### Run with mounted log file
docker compose build
docker compose up

### Tools 

- Ollama: https://ollama.com/ 