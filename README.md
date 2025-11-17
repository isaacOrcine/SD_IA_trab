# Sistema Distribuído de IA para Geração de Posts do Instagram

Sistema distribuído com múltiplos agentes de IA para geração inteligente de conteúdo para Instagram.

## 📋 Arquitetura

```
Trab_SD/
├── agent1-local/       # Agente 1 - Ollama + Llama3.2:1b (Local)
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── entrypoint.sh
├── agent2-gemini/      # Agente 2 - Gemini (Cloud) [TODO]
├── api/                # API principal de orquestração [TODO]
└── docker-compose.yml
```

## 🚀 Agent 1 - Modelo Local (Ollama + Llama3.2:1b)

O primeiro agente utiliza **Ollama** rodando localmente com o modelo **llama3.2:1b** (modelo leve e rápido).

### Funcionalidades

- ✅ Servidor HTTP com FastAPI na porta 8001
- ✅ Endpoint POST `/generate` para geração de posts
- ✅ Modelo Llama3.2:1b rodando localmente
- ✅ Volume persistente para cache de modelos
- ✅ Health check automático

## 🛠️ Como Rodar

### Pré-requisitos

- Docker e Docker Compose instalados
- Mínimo 4GB de RAM disponível
- ~1.3GB de espaço em disco para o modelo

### Iniciar o Sistema

```bash
# Na raiz do projeto
docker-compose up --build
```

**Importante:** O primeiro start levará alguns minutos para:
1. Instalar o Ollama
2. Baixar o modelo llama3.2:1b (~1.3GB)
3. Iniciar o servidor

Aguarde a mensagem: `"Iniciando servidor FastAPI..."`

### Verificar Status

```bash
# Verificar se o agente está online
curl http://localhost:8001/

# Verificar saúde do serviço
curl http://localhost:8001/health
```

## 📡 API - Endpoints

### GET `/`
Retorna informações do agente

**Response:**
```json
{
  "agent": "agent1-local",
  "model": "llama3.2:1b",
  "status": "online"
}
```

### GET `/health`
Verifica saúde do serviço Ollama

**Response:**
```json
{
  "status": "healthy",
  "ollama": "online"
}
```

### POST `/generate`
Gera rascunho de post para Instagram

**Request:**
```json
{
  "topic": "Serviços de computação",
  "style": "casual"
}
```

**Response:**
```json
{
  "draft": "Você tem o potencial de conquistar sua melhor versão! Não é só sobre o treino, mas também sobre criar um hábito que se torne uma parte natural da sua vida. Cada passo você desafia, cada exercício você supera... Qual é o seu objetivo maior?\n\n#TreinamentoMotivacional #AcademiaDesafia #CriaçãoDeHábitos",
  "agent": "agent1-local",
  "model": "llama3.2:1b"
}
```

## 🧪 Exemplos de Teste

### Usando cURL (PowerShell)

```powershell
# Teste básico
curl http://localhost:8001/


# Gerar post profissional sobre tecnologia
curl -X POST http://localhost:8001/generate `
  -H "Content-Type: application/json" `
  -d '{\"topic\": \"inteligência artificial\", \"style\": \"profissional\"}'

# Gerar post divertido sobre pets
curl -X POST http://localhost:8001/generate `
  -H "Content-Type: application/json" `
  -d '{\"topic\": \"meu cachorro\", \"style\": \"divertido\"}'
```

### Usando Python

```python
import requests

url = "http://localhost:8001/generate"
payload = {
    "topic": "treino na academia",
    "style": "motivacional"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Post gerado por: {result['agent']}")
print(f"Modelo: {result['model']}")
print(f"\n{result['draft']}")
```

### Usando Postman

1. **Method:** POST
2. **URL:** `http://localhost:8001/generate`
3. **Headers:** `Content-Type: application/json`
4. **Body (raw JSON):**
```json
{
  "topic": "sunset na montanha",
  "style": "inspiracional"
}
```

## 🔧 Gerenciamento

### Ver logs em tempo real
```bash
docker-compose logs -f agent1-local
```

### Parar o sistema
```bash
docker-compose down
```

### Parar e remover volumes (limpar cache de modelos)
```bash
docker-compose down -v
```

### Rebuild completo
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 📊 Informações Técnicas

### Modelo
- **Nome:** llama3.2:1b
- **Tamanho:** ~1.3GB
- **Fornecedor:** Meta (via Ollama)
- **Contexto:** 128k tokens
- **Ideal para:** Geração rápida de texto curto

### Performance Esperada
- **Primeira execução:** 30-60 segundos (download do modelo)
- **Execuções seguintes:** 5-15 segundos por geração
- **RAM necessária:** ~2GB durante geração

### Portas Utilizadas
- **8001:** API FastAPI do Agent 1
- **11434:** Ollama (interno ao container)

### Volumes Persistentes
- `ollama-models`: Cache dos modelos baixados

## 🔜 Próximos Passos

- [ ] Implementar Agent 2 com Google Gemini
- [ ] Criar API de orquestração para coordenar agentes
- [ ] Implementar sistema de escolha/ranking de posts
- [ ] Adicionar geração de imagens
- [ ] Interface web para testar os agentes

## 📝 Notas

- O modelo roda completamente **offline** após o download inicial
- Resultados podem variar em criatividade e qualidade
- Para melhor qualidade, considere modelos maiores (llama3.2:3b, llama3:8b)
- O primeiro start pode demorar devido ao download do modelo

## ⚠️ Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker-compose logs agent1-local

# Verificar se a porta está disponível
netstat -an | findstr "8001"
```

### Modelo não baixa
- Verifique conexão com internet
- Confirme espaço em disco disponível
- Reinicie o container: `docker-compose restart agent1-local`

### Timeout ao gerar
- Aguarde mais tempo na primeira geração (modelo carrega na primeira vez)
- Verifique recursos disponíveis (RAM/CPU)

---

**Desenvolvido para Trabalho de Sistemas Distribuídos**
