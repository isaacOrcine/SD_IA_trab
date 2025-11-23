#!/bin/bash
set -e

echo "✅ Iniciando Agent1 - Ollama Local Client"

# Verificar se pode conectar ao Ollama
max_attempts=30
attempt=0

echo "⏳ Aguardando Ollama iniciar..."
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://ollama:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama está pronto!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Tentativa $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Ollama não respondeu após $max_attempts tentativas"
    exit 1
fi

# Verificar se modelo existe
echo "🤖 Verificando modelo llama3.2:1b..."
if ! curl -s http://ollama:11434/api/tags | grep -q "llama3.2:1b"; then
    echo "📥 Modelo não encontrado, puxando..."
    curl -X POST http://ollama:11434/api/pull -d '{"name":"llama3.2:1b"}'
    echo "✅ Modelo baixado!"
else
    echo "✅ Modelo já existe"
fi

echo "🚀 Iniciando aplicação FastMCP..."
exec python app.py