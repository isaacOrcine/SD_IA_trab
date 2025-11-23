"""
Agent1 - Servidor MCP com Ollama Local
Gera rascunhos de posts usando modelo Llama
"""

import httpx
from fastmcp import FastMCP
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar servidor MCP
mcp = FastMCP("Agent1-Llama-Local")

# ✅ Modelo para request
class GenerateDraftRequest(BaseModel):
    topic: str
    style: str
    tone: str = "neutro"

@mcp.tool()
async def generate_draft(topic: str, style: str, tone: str = "neutro") -> str:
    """Gera um rascunho inicial usando Ollama local."""
    prompt = f"Crie uma caption para Instagram. Tópico: {topic}, Estilo: {style}, Tom: {tone}. Retorne apenas o texto."
    
    try:
        logger.info(f"📝 Conectando ao Ollama para gerar rascunho...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://ollama:11434/api/generate",
                json={"model": "llama3.2:1b", "prompt": prompt, "stream": False}
            )
            if response.status_code != 200:
                logger.error(f"❌ Ollama retornou status {response.status_code}")
                return f"Erro: Status {response.status_code}"
            
            result = response.json().get("response", "").strip()
            if result:
                logger.info(f"✅ Rascunho gerado com sucesso")
                return result
            else:
                logger.error(f"❌ Resposta vazia do Ollama")
                return "Erro: Resposta vazia do Ollama"
    except httpx.ConnectError as e:
        logger.error(f"❌ Não conseguiu conectar ao Ollama: {e}")
        return f"Erro: Não conseguiu conectar ao Ollama - {str(e)}"
    except Exception as e:
        logger.error(f"❌ Erro ao chamar Ollama: {e}")
        return f"Erro ao conectar Ollama: {str(e)}"

# ✅ CORREÇÃO CRÍTICA: Criar aplicação FastAPI com os endpoints do FastMCP
app = FastAPI(title="Agent1 - Llama Local")

# Registrar os tools como endpoints
@app.get("/")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "Agent1-Llama-Local"}

@app.post("/api/tools/generate_draft")
async def api_generate_draft(request: GenerateDraftRequest):
    """API endpoint para gerar rascunho - aceita JSON body"""
    try:
        logger.info(f"📝 API Request: topic={request.topic}, style={request.style}, tone={request.tone}")
        result = await generate_draft(request.topic, request.style, request.tone)
        return {
            "content": [{"type": "text", "text": result}]
        }
    except Exception as e:
        logger.error(f"❌ Erro no endpoint: {e}")
        return {
            "error": str(e),
            "content": [{"type": "text", "text": f"Erro: {str(e)}"}]
        }

if __name__ == "__main__":
    print("✅ Iniciando servidor MCP Agent1 na porta 8001...")
    logger.info("🚀 Servidor MCP iniciando na porta 8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)