"""
Orquestrador MCP - Coordena fluxo entre Agent1 (Ollama) e Agent2 (Gemini)
Utiliza chamadas HTTP REST para comunicação com os agentes
"""

import httpx
import asyncio
import os
import json
from typing import Dict
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URLs dos agentes
AGENT1_URL = os.getenv("AGENT1_URL", "http://agent1-local:8001")
AGENT2_URL = os.getenv("AGENT2_URL", "http://agent2-gemini:8002")

HTTP_TIMEOUT = 120.0

logger.info(f"Conectando a Agent1: {AGENT1_URL}")
logger.info(f"Conectando a Agent2: {AGENT2_URL}")


class OrchestratorError(Exception):
    """Exceção customizada para erros do orquestrador"""
    pass


class Agent1Client:
    """Cliente para Agent1 (Ollama Local)"""
    
    def __init__(self, base_url: str = AGENT1_URL, timeout: float = HTTP_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                is_healthy = response.status_code == 200
                if is_healthy:
                    logger.info(f"✅ Agent1 está respondendo")
                return is_healthy
        except Exception as e:
            logger.debug(f"Agent1 ainda não pronto: {e}")
            return False
    
    async def generate_draft(self, topic: str, style: str, tone: str = "criativo") -> str:
        try:
            logger.info(f"📝 Agent1: Gerando rascunho - Tópico: {topic}, Estilo: {style}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {"topic": topic, "style": style, "tone": tone}
                
                response = await client.post(
                    f"{self.base_url}/api/tools/generate_draft",
                    json=payload
                )
                
                if response.status_code != 200:
                    raise OrchestratorError(
                        f"Agent1 retornou status {response.status_code}: {response.text}"
                    )
                
                result = response.json()
                
                if isinstance(result, dict) and "content" in result:
                    content = result["content"]
                    if isinstance(content, list) and len(content) > 0:
                        draft_text = content[0].get("text", "")
                    else:
                        draft_text = content.get("text", "") if isinstance(content, dict) else str(content)
                else:
                    draft_text = str(result)
                
                if not draft_text or len(draft_text) < 10:
                    raise OrchestratorError("Agent1 retornou rascunho vazio")
                
                logger.info(f"✅ Rascunho gerado com sucesso ({len(draft_text)} caracteres)")
                return draft_text.strip()
        
        except httpx.TimeoutException:
            raise OrchestratorError(f"Agent1 timeout após {self.timeout}s")
        except httpx.ConnectError as e:
            raise OrchestratorError(f"Não conseguiu conectar a Agent1: {e}")
        except Exception as e:
            raise OrchestratorError(f"Erro ao chamar Agent1: {str(e)}")


class Agent2Client:
    """Cliente para Agent2 (Gemini Cloud)"""
    
    def __init__(self, base_url: str = AGENT2_URL, timeout: float = HTTP_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                is_healthy = response.status_code == 200
                if is_healthy:
                    logger.info(f"✅ Agent2 está respondendo")
                return is_healthy
        except Exception as e:
            logger.debug(f"Agent2 ainda não pronto: {e}")
            return False
    
    async def improve_content(self, draft_text: str, target_audience: str = "público geral") -> str:
        """Chama o endpoint /improve do Agent2"""
        try:
            logger.info(f"✨ Agent2: Refinando conteúdo para {target_audience}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # ✅ IMPORTANTE: Usar /improve em vez de /api/tools/improve_content
                payload = {
                    "draft_text": draft_text,
                    "target_audience": target_audience
                }
                
                response = await client.post(
                    f"{self.base_url}/improve",  # ✅ ENDPOINT CORRETO
                    json=payload
                )
                
                if response.status_code != 200:
                    raise OrchestratorError(
                        f"Agent2 retornou status {response.status_code}: {response.text}"
                    )
                
                result = response.json()
                
                # Agent2 retorna improved_text diretamente
                improved_text = result.get("improved_text", "")
                
                if not improved_text or len(improved_text) < 10:
                    raise OrchestratorError("Agent2 retornou conteúdo vazio")
                
                logger.info(f"✅ Conteúdo refinado com sucesso ({len(improved_text)} caracteres)")
                return improved_text.strip()
        
        except httpx.TimeoutException:
            raise OrchestratorError(f"Agent2 timeout após {self.timeout}s")
        except httpx.ConnectError as e:
            raise OrchestratorError(f"Não conseguiu conectar a Agent2: {e}")
        except Exception as e:
            raise OrchestratorError(f"Erro ao chamar Agent2 improve_content: {str(e)}")
    
    async def generate_image_prompt(self, post_text: str) -> str:
        """Chama o endpoint /generate-image do Agent2"""
        try:
            logger.info("🎨 Agent2: Gerando prompt de imagem")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # ✅ IMPORTANTE: Usar /generate-image em vez de /api/tools/generate_image_prompt
                payload = {
                    "prompt": post_text,
                    "style": "realistic"
                }
                
                response = await client.post(
                    f"{self.base_url}/generate-image",  # ✅ ENDPOINT CORRETO
                    json=payload
                )
                
                if response.status_code != 200:
                    raise OrchestratorError(
                        f"Agent2 retornou status {response.status_code}: {response.text}"
                    )
                
                result = response.json()
                
                # Agent2 retorna image_path com descrição
                image_prompt = result.get("image_path", "")
                
                if not image_prompt or len(image_prompt) < 5:
                    raise OrchestratorError("Agent2 retornou prompt vazio")
                
                logger.info(f"✅ Prompt de imagem gerado com sucesso")
                return image_prompt.strip()
        
        except httpx.TimeoutException:
            raise OrchestratorError(f"Agent2 timeout ao gerar prompt")
        except httpx.ConnectError as e:
            raise OrchestratorError(f"Não conseguiu conectar a Agent2: {e}")
        except Exception as e:
            raise OrchestratorError(f"Erro ao chamar Agent2: {str(e)}")


class Orchestrator:
    """Orquestrador principal"""
    
    def __init__(self, agent1_url: str = AGENT1_URL, agent2_url: str = AGENT2_URL):
        self.agent1 = Agent1Client(agent1_url)
        self.agent2 = Agent2Client(agent2_url)
    
    async def verify_agents_health(self, retries: int = 30, delay: int = 2) -> bool:
        logger.info(f"🔍 Verificando saúde dos agentes (máximo {retries} tentativas)...")
        
        for attempt in range(1, retries + 1):
            agent1_ok = await self.agent1.health_check()
            agent2_ok = await self.agent2.health_check()
            
            if agent1_ok and agent2_ok:
                logger.info(f"✅ Ambos agentes estão saudáveis após {attempt} tentativa(s)")
                return True
            
            if attempt < retries:
                logger.info(f"⏳ Tentativa {attempt}/{retries} - Agentes iniciando...")
                await asyncio.sleep(delay)
        
        logger.error(f"❌ Agentes não responderam após {retries} tentativas")
        return False
    
    async def run_instagram_workflow(
        self,
        topic: str,
        style: str,
        tone: str = "criativo",
        target_audience: str = "público geral"
    ) -> Dict:
        try:
            timestamp = datetime.now().isoformat()
            logger.info(f"\n{'='*70}")
            logger.info(f"🚀 INICIANDO WORKFLOW INSTAGRAM")
            logger.info(f"   Tópico: {topic}")
            logger.info(f"   Estilo: {style}")
            logger.info(f"   Tom: {tone}")
            logger.info(f"   Público: {target_audience}")
            logger.info(f"{'='*70}\n")
            
            # ETAPA 1: Gerar rascunho com Agent1
            logger.info("ETAPA 1/3: Gerando rascunho inicial...")
            draft = await self.agent1.generate_draft(topic=topic, style=style, tone=tone)
            logger.info(f"\n📝 RASCUNHO:\n{'-'*70}\n{draft}\n{'-'*70}\n")
            
            # ETAPA 2: Melhorar conteúdo com Agent2
            logger.info("ETAPA 2/3: Refinando conteúdo com Gemini...")
            final_post = await self.agent2.improve_content(
                draft_text=draft,
                target_audience=target_audience
            )
            logger.info(f"\n✨ POST FINAL:\n{'-'*70}\n{final_post}\n{'-'*70}\n")
            
            # ETAPA 3: Gerar prompt de imagem
            logger.info("ETAPA 3/3: Gerando prompt de imagem...")
            image_prompt = await self.agent2.generate_image_prompt(post_text=final_post)
            logger.info(f"\n🎨 PROMPT DE IMAGEM:\n{'-'*70}\n{image_prompt}\n{'-'*70}\n")
            
            result = {
                "draft": draft,
                "final_post": final_post,
                "image_prompt": image_prompt,
                "timestamp": timestamp,
                "metadata": {
                    "topic": topic,
                    "style": style,
                    "tone": tone,
                    "target_audience": target_audience
                }
            }
            
            logger.info(f"{'='*70}")
            logger.info("✅ WORKFLOW CONCLUÍDO COM SUCESSO!")
            logger.info(f"{'='*70}\n")
            
            return result
        
        except OrchestratorError as e:
            logger.error(f"\n❌ ERRO NO WORKFLOW: {str(e)}\n")
            raise
        except Exception as e:
            logger.error(f"\n❌ ERRO INESPERADO: {str(e)}\n")
            raise OrchestratorError(f"Erro inesperado: {str(e)}")


async def main():
    orchestrator = Orchestrator(agent1_url=AGENT1_URL, agent2_url=AGENT2_URL)
    
    agents_healthy = await orchestrator.verify_agents_health(retries=60, delay=1)
    if not agents_healthy:
        logger.error("❌ Agentes não estão saudáveis")
        return 1
    
    try:
        result = await orchestrator.run_instagram_workflow(
            topic="Inteligência Artificial e Automação",
            style="Tecnológico",
            tone="criativo",
            target_audience="desenvolvedores e tech enthusiasts"
        )
        
        with open("workflow_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ Resultado salvo em workflow_result.json")
    
    except OrchestratorError as e:
        logger.error(f"Erro: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)