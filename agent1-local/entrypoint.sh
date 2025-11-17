#!/bin/bash

# Iniciar Ollama em background
ollama serve &

# Aguardar o Ollama iniciar
echo "Aguardando Ollama iniciar..."
sleep 5

# Baixar o modelo llama3.2:1b
echo "Baixando modelo llama3.2:1b..."
ollama pull llama3.2:1b

# Iniciar a aplicação FastAPI
echo "Iniciando servidor FastAPI..."
uvicorn app:app --host 0.0.0.0 --port 8001
