from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import json
from typing import Optional

app = FastAPI(title="Agent 1 - Ollama Local")


class GenerateRequest(BaseModel):
    topic: str
    style: str


class GenerateResponse(BaseModel):
    draft: str
    agent: str
    model: str


@app.get("/")
async def root():
    return {
        "agent": "agent1-local",
        "model": "llama3.2:1b",
        "status": "online"
    }


@app.get("/health")
async def health():
    """Verifica se o Ollama está disponível"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                return {"status": "healthy", "ollama": "online"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama indisponível: {str(e)}")


@app.post("/generate", response_model=GenerateResponse)
async def generate_post(request: GenerateRequest):
    """
    Gera um rascunho de post do Instagram usando Ollama local
    
    Args:
        topic: Tópico do post (ex: "Serviços de computação")
        style: Estilo do post (ex: "casual", "profissional", "divertido")
    
    Returns:
        draft: Rascunho do post gerado
        agent: Nome do agente (agent1-local)
        model: Modelo usado (llama3.2:1b)
    """
    
    # Criar prompt para o modelo
    prompt = f"""Você é um criador de conteúdo para Instagram. 
Crie uma caption criativa e envolvente para um post sobre: {request.topic}
Estilo desejado: {request.style}

A caption deve:
- Ter entre 2-4 linhas
- Ser atrativa e engajadora
- Usar emojis apropriados
- Incluir 3-5 hashtags relevantes no final

Caption:"""
    
    # Chamar Ollama via API
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao chamar Ollama: {response.text}"
                )
            
            result = response.json()
            draft = result.get("response", "").strip()
            
            if not draft:
                raise HTTPException(
                    status_code=500,
                    detail="Modelo não retornou resposta"
                )
            
            return GenerateResponse(
                draft=draft,
                agent="agent1-local",
                model="llama3.2:1b"
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout ao gerar conteúdo - modelo pode estar processando"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro de conexão com Ollama: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
