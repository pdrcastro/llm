FROM python:3.11-slim

# Install Ollama client
RUN pip install ollama

# Copy app
WORKDIR /app
COPY llm.py .

# Ollama model
CMD ["python", "llm.py", "/logs/input.log"]
