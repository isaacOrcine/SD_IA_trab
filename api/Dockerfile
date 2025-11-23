FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    httpx==0.27.2 \
    pydantic==2.5.0 \
    python-multipart==0.0.6

COPY . .

EXPOSE 8000

CMD ["python", "web_app.py"]