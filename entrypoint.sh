#!/bin/sh
set -e

# Start ollama server in the background
ollama serve &

# Wait for Ollama server to be ready
echo "Waiting for Ollama server..."
for i in $(seq 1 30); do
  if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama server is up!"
    break
  fi
  echo "Waiting for Ollama server..."
  sleep 2
done

if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama server failed to start."
  exit 1
fi

# Pull llama2 model
ollama pull llama2

# Keep the server running in foreground (wait on ollama serve process)
wait
