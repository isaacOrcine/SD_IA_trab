"""
FastAPI Web Interface para Orchestrator
Fornece uma interface web interativa para gerar posts Instagram
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs dos agentes
AGENT1_URL = os.getenv("AGENT1_URL", "http://agent1-local:8001")
AGENT2_URL = os.getenv("AGENT2_URL", "http://agent2-gemini:8002")

# Criar app FastAPI
app = FastAPI(
    title="Instagram AI Post Generator",
    description="Interface para gerar posts Instagram com IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretório para histórico
HISTORY_DIR = Path("/app/history")
HISTORY_DIR.mkdir(exist_ok=True)

# ============= MODELOS =============

class WorkflowRequest(BaseModel):
    topic: str
    style: str
    tone: str = "criativo"
    target_audience: str = "público geral"

class WorkflowResponse(BaseModel):
    draft: str
    final_post: str
    image_prompt: str
    timestamp: str

# ============= ENDPOINTS =============

@app.get("/")
async def root():
    """Retorna a página HTML principal"""
    return FileResponse("/app/index.html", media_type="text/html")

@app.post("/api/generate-post")
async def generate_post(request: WorkflowRequest):
    """Executa o workflow e retorna o resultado"""
    try:
        logger.info(f"📝 Gerando post para: {request.topic}")
        
        # Etapa 1: Gerar rascunho
        logger.info("ETAPA 1: Gerando rascunho...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response1 = await client.post(
                f"{AGENT1_URL}/api/tools/generate_draft",
                json={
                    "topic": request.topic,
                    "style": request.style,
                    "tone": request.tone
                }
            )
            if response1.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Agent1 error: {response1.text}"
                )
            
            result1 = response1.json()
            draft = result1.get("content", [{}])[0].get("text", "") if isinstance(result1.get("content"), list) else result1.get("content", {}).get("text", "")
        
        logger.info("ETAPA 2: Refinando com Gemini...")
        # Etapa 2: Refinar
        async with httpx.AsyncClient(timeout=120.0) as client:
            response2 = await client.post(
                f"{AGENT2_URL}/improve",
                json={
                    "draft_text": draft,
                    "target_audience": request.target_audience
                }
            )
            if response2.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Agent2 error: {response2.text}"
                )
            
            result2 = response2.json()
            final_post = result2.get("improved_text", "")
        
        logger.info("ETAPA 3: Gerando prompt de imagem...")
        # Etapa 3: Gerar prompt de imagem
        async with httpx.AsyncClient(timeout=120.0) as client:
            response3 = await client.post(
                f"{AGENT2_URL}/generate-image",
                json={
                    "prompt": final_post,
                    "style": "realistic"
                }
            )
            if response3.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Agent2 image error: {response3.text}"
                )
            
            result3 = response3.json()
            image_prompt = result3.get("image_path", "")
        
        # Salvar no histórico
        workflow_result = {
            "draft": draft,
            "final_post": final_post,
            "image_prompt": image_prompt,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "topic": request.topic,
                "style": request.style,
                "tone": request.tone,
                "target_audience": request.target_audience
            }
        }
        
        # Salvar arquivo
        filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = HISTORY_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(workflow_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Post gerado com sucesso! Salvo em {filename}")
        
        return WorkflowResponse(**workflow_result)
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Agents timeout - took too long")
    except httpx.ConnectError as e:
        raise HTTPException(status_code=503, detail=f"Cannot connect to agents: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    """Retorna histórico de posts gerados"""
    try:
        files = sorted(HISTORY_DIR.glob("post_*.json"), reverse=True)[:10]
        history = []
        
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                history.append({
                    "filename": file.name,
                    "timestamp": data.get("timestamp"),
                    "topic": data.get("metadata", {}).get("topic"),
                    "final_post": data.get("final_post")
                })
        
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{filename}")
async def get_history_item(filename: str):
    """Retorna um item específico do histórico"""
    try:
        filepath = HISTORY_DIR / filename
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download um JSON do histórico"""
    try:
        filepath = HISTORY_DIR / filename
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(filepath, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "Web Interface"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)