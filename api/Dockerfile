FROM python:3.11-slim

WORKDIR /app

# Instala o cliente MCP e sse-client
RUN pip install mcp==1.0.0 httpx==0.27.2 sse-starlette

COPY . .

CMD ["python", "orchestrator.py"]