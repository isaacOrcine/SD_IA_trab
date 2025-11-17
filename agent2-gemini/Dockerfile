FROM python:3.11-slim

# Criar diretório de trabalho
WORKDIR /app

# Criar diretório para imagens geradas
RUN mkdir -p /app/outputs

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8002

# Iniciar aplicação
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
