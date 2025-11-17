from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Optional
import base64
from pathlib import Path
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env")

genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(title="Agent 2 - Google Gemini")

# Diretório para salvar imagens
OUTPUTS_DIR = Path("/app/outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)


# ============= MODELOS =============

class ImproveCaptionRequest(BaseModel):
    draft_text: str
    style: Optional[str] = "casual"  # "casual", "profissional", "engraçado"
    target_audience: Optional[str] = "público geral"


class ImproveCaptionResponse(BaseModel):
    improved_text: str
    hashtags: List[str]
    agent: str
    model: str


class GenerateImageRequest(BaseModel):
    prompt: str
    style: Optional[str] = "realistic"


class GenerateImageResponse(BaseModel):
    image_path: str
    prompt_used: str
    agent: str
    model: str


# ============= ENDPOINTS =============

@app.get("/")
async def root():
    return {
        "agent": "agent2-gemini",
        "models": {
            "text": "models/gemini-2.5-flash",
            "image_description": "models/gemini-2.5-flash"
        },
        "status": "online"
    }


@app.get("/health")
async def health():
    """Verifica se a API do Gemini está configurada"""
    try:
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_api_key_here":
            raise HTTPException(
                status_code=503,
                detail="GOOGLE_API_KEY não configurada corretamente"
            )
        return {
            "status": "healthy",
            "gemini_api": "configured"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro na configuração: {str(e)}"
        )


@app.post("/improve", response_model=ImproveCaptionResponse)
async def improve_caption(request: ImproveCaptionRequest):
    """
    Melhora uma caption de Instagram usando Gemini
    
    Args:
        draft_text: Texto do rascunho para melhorar
        style: Estilo desejado (casual, profissional, divertido, etc)
        target_audience: Público-alvo (opcional)
    
    Returns:
        improved_text: Texto melhorado
        hashtags: Lista de 5-10 hashtags relevantes
        agent: Nome do agente
        model: Modelo usado
    """
    try:
        # Criar prompt para melhorar caption
        prompt = f"""Você é um especialista em marketing digital e criação de conteúdo para Instagram.

TAREFA: Melhore a caption abaixo para torná-la mais profissional, envolvente e otimizada para o Instagram.

CAPTION ORIGINAL:
{request.draft_text}

DIRETRIZES:
- Estilo: {request.style}
- Público-alvo: {request.target_audience}
- Corrija erros gramaticais e ortográficos
- Torne o texto mais envolvente e com gatilhos emocionais
- Mantenha entre 2-5 linhas (não muito longo)
- Use emojis estrategicamente (não exagere)
- Adicione call-to-action sutil se apropriado
- NÃO inclua hashtags no texto melhorado

FORMATO DA RESPOSTA:
Retorne APENAS o texto melhorado, sem hashtags.

TEXTO MELHORADO:"""

        # Chamar Gemini para texto
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="Gemini não retornou resposta"
            )
        
        improved_text = response.text.strip()
        
        # Gerar hashtags relevantes
        hashtags_prompt = f"""Com base nesta caption do Instagram, sugira 5-10 hashtags relevantes e populares.

CAPTION:
{improved_text}

REGRAS:
- Misture hashtags populares e nichos
- Inclua hashtags em português e inglês quando relevante
- Foque em engajamento e alcance
- NÃO use # na frente, apenas as palavras

FORMATO: Retorne apenas as hashtags separadas por vírgula, sem numeração ou marcadores.

HASHTAGS:"""

        hashtags_response = model.generate_content(hashtags_prompt)
        hashtags_text = hashtags_response.text.strip()
        
        # Processar hashtags
        hashtags = [
            f"#{tag.strip().replace('#', '')}" 
            for tag in hashtags_text.split(',')
            if tag.strip()
        ][:10]  # Limitar a 10 hashtags
        
        return ImproveCaptionResponse(
            improved_text=improved_text,
            hashtags=hashtags,
            agent="agent2-gemini",
            model="models/gemini-2.5-flash"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao melhorar caption: {str(e)}"
        )


@app.post("/generate-image", response_model=GenerateImageResponse)
async def generate_image_description(request: GenerateImageRequest):
    """
    Gera uma DESCRIÇÃO DETALHADA de imagem usando Gemini
    
    Args:
        prompt: Descrição da imagem desejada
        style: Estilo visual (realistic, artistic, minimalist, etc)
    
    Returns:
        image_path: Caminho onde a descrição foi salva
        prompt_used: Prompt final usado
        agent: Nome do agente
        model: Modelo usado
    """
    try:
        # Melhorar o prompt para gerar uma descrição de imagem
        enhanced_prompt = f"""Você é um diretor de arte especialista em criar prompts para geradores de imagem de IA (como Midjourney ou DALL-E).
Sua tarefa é expandir a ideia do usuário em um prompt rico e detalhado.

IDÉIA ORIGINAL:
- Prompt: {request.prompt}
- Estilo: {request.style}

INSTRUÇÕES:
- Crie um parágrafo único e detalhado.
- Descreva a cena, a iluminação, as cores, a composição, a atmosfera e os detalhes finos.
- Use palavras-chave que maximizem a qualidade da imagem gerada.
- O resultado deve ser um prompt pronto para ser copiado e colado em uma ferramenta de IA.

PROMPT DETALHADO:"""
        
        # Usar gemini-pro para DESCREVER a imagem
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        response = model.generate_content(enhanced_prompt)

        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="Gemini não retornou uma descrição para a imagem."
            )

        # Salvar a descrição em um arquivo .txt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_prompt_{timestamp}.txt"
        image_path = OUTPUTS_DIR / filename
        
        with open(image_path, "w", encoding="utf-8") as f:
            f.write(f"Prompt detalhado para gerar imagem:\n\n{response.text}")
        
        return GenerateImageResponse(
            image_path=f"Descrição de imagem salva em: {str(image_path)}",
            prompt_used=enhanced_prompt,
            agent="agent2-gemini",
            model="models/gemini-2.5-flash"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar descrição de imagem: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
