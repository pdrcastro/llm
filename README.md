# LLM
LLM for Monitoring Solution

## Run Container
### Build the image
docker build -t log-classifier .

### Run with mounted log file
docker run --rm -v $(pwd)/logs:/logs log-classifier

### Tools 

- Ollama: https://ollama.com/ 