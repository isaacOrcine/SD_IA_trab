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
├── agent2-gemini/      # Agente 2 - Google Gemini (Cloud)
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   └── outputs/        # Imagens geradas
├── api/                # API principal de orquestração [TODO]
├── docker-compose.yml
└── test_gemini.py      # Script de teste para Agent 2
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
- **8002:** API FastAPI do Agent 2
- **11434:** Ollama (interno ao container)

### Volumes Persistentes
- `ollama-models`: Cache dos modelos baixados

---

## 🌐 Agent 2 - Google Gemini (Gemini 2.0 Flash + Imagen 3.0)

O segundo agente utiliza **Google Gemini API** com modelos de última geração na nuvem.

### Funcionalidades

- ✅ Servidor HTTP com FastAPI na porta 8002
- ✅ Endpoint POST `/improve` para melhorar captions
- ✅ Endpoint POST `/generate-image` para gerar imagens
- ✅ Modelo gemini-2.0-flash-exp (texto)
- ✅ Modelo imagen-3.0-generate-001 (imagens)
- ✅ Volume persistente para imagens geradas

### Configuração Inicial

**1. Obter chave da API do Gemini (gratuita):**
   - Acesse: https://makersuite.google.com/app/apikey
   - Faça login com sua conta Google
   - Clique em "Create API Key"
   - Copie a chave gerada

**2. Configurar variável de ambiente:**

```powershell
# Copiar arquivo de exemplo
Copy-Item agent2-gemini\.env.example agent2-gemini\.env

# Editar .env e adicionar sua chave
# GOOGLE_API_KEY=sua_chave_aqui
```

**3. Iniciar o agente:**

```bash
# Iniciar apenas Agent 2
docker-compose up --build agent2-gemini

# Ou iniciar todos os agentes
docker-compose up --build
```

### Endpoints do Agent 2

#### GET `/`
Retorna informações do agente

**Response:**
```json
{
  "agent": "agent2-gemini",
  "models": {
    "text": "gemini-2.0-flash-exp",
    "image": "imagen-3.0-generate-001"
  },
  "status": "online"
}
```

#### GET `/health`
Verifica se a API do Gemini está configurada

**Response:**
```json
{
  "status": "healthy",
  "gemini_api": "configured"
}
```

#### POST `/improve`
Melhora uma caption do Instagram

**Request:**
```json
{
  "draft_text": "dia incrivel na praia!! sol mar e diversao",
  "style": "casual",
  "target_audience": "jovens adultos"
}
```

**Response:**
```json
{
  "improved_text": "☀️ Dias perfeitos são feitos de sol, mar e boas energias! A praia tem esse poder de renovar a alma e recarregar as energias. Momentos assim merecem ser vividos intensamente! 🌊✨",
  "hashtags": [
    "#PraiaDia",
    "#VerãoPerfeito",
    "#SolEMar",
    "#VidaNaPraia",
    "#BeachVibes",
    "#SummerDay",
    "#GoodVibes",
    "#ViagemDePraia"
  ],
  "agent": "agent2-gemini",
  "model": "gemini-2.0-flash-exp"
}
```

#### POST `/generate-image`
Gera imagem para o post

**Request:**
```json
{
  "prompt": "beautiful sunset at the beach with palm trees",
  "style": "realistic"
}
```

**Response:**
```json
{
  "image_path": "/app/outputs/instagram_post_20251117_140530.png",
  "prompt_used": "High quality Instagram post image, realistic style, beautiful sunset...",
  "agent": "agent2-gemini",
  "model": "imagen-3.0-generate-001"
}
```

### Exemplos de Uso do Agent 2

#### Usando PowerShell

```powershell
# Melhorar caption
$body = @{
    draft_text = "Café da manhã delicioso hoje!"
    style = "casual"
    target_audience = "amantes de café"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8002/improve `
    -Method Post -Body $body -ContentType 'application/json'

# Gerar imagem
$body = @{
    prompt = "cozy coffee shop with latte art"
    style = "artistic"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8002/generate-image `
    -Method Post -Body $body -ContentType 'application/json'
```

#### Usando Python

```python
import requests

# Melhorar caption
url = "http://localhost:8002/improve"
payload = {
    "draft_text": "Treino pesado hoje! 💪",
    "style": "motivacional",
    "target_audience": "fitness enthusiasts"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Texto melhorado:\n{result['improved_text']}")
print(f"\nHashtags: {' '.join(result['hashtags'])}")

# Gerar imagem
url = "http://localhost:8002/generate-image"
payload = {
    "prompt": "gym workout motivation, person lifting weights",
    "style": "realistic"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Imagem salva em: {result['image_path']}")
```

### Script de Teste Automatizado

Execute o script de teste completo:

```powershell
# Instalar requests se necessário
pip install requests

# Executar testes
python test_gemini.py
```

O script testa todos os endpoints e mostra os resultados formatados.

### Informações Técnicas - Agent 2

**Modelos:**
- **Texto:** gemini-2.0-flash-exp (mais recente, gratuito)
- **Imagem:** imagen-3.0-generate-001

**Performance:**
- **Melhoria de caption:** 2-5 segundos
- **Geração de imagem:** 30-60 segundos
- **Requisitos:** API Key do Google

**Portas:**
- **8002:** API FastAPI do Agent 2

**Volumes:**
- `gemini-outputs`: Imagens geradas persistidas

**Limites da API Gratuita:**
- Gemini 2.0 Flash: 15 RPM (requests por minuto)
- Imagen 3.0: ~50 imagens/dia na tier gratuita
- Detalhes: https://ai.google.dev/pricing

---

## 🔄 Workflow Completo (Agent 1 + Agent 2)

```
1. Agent 1 gera rascunho inicial
   ↓
2. Agent 2 melhora o texto e adiciona hashtags
   ↓
3. Agent 2 gera imagem baseada no conteúdo
   ↓
4. Post completo pronto para publicação!
```

**Exemplo de uso combinado:**

```powershell
# 1. Gerar rascunho com Agent 1
$draft = Invoke-RestMethod -Uri http://localhost:8001/generate `
    -Method Post -ContentType 'application/json' `
    -Body '{"topic": "café da manhã", "style": "casual"}'

# 2. Melhorar com Agent 2
$improved = Invoke-RestMethod -Uri http://localhost:8002/improve `
    -Method Post -ContentType 'application/json' `
    -Body (@{
        draft_text = $draft.draft
        style = "casual"
        target_audience = "food lovers"
    } | ConvertTo-Json)

# 3. Gerar imagem
$image = Invoke-RestMethod -Uri http://localhost:8002/generate-image `
    -Method Post -ContentType 'application/json' `
    -Body '{"prompt": "delicious breakfast coffee and croissant", "style": "realistic"}'

Write-Host "Caption final: $($improved.improved_text)"
Write-Host "Hashtags: $($improved.hashtags -join ' ')"
Write-Host "Imagem: $($image.image_path)"
```

### Volumes Persistentes

## 🔜 Próximos Passos

- [x] ~~Implementar Agent 2 com Google Gemini~~
- [x] ~~Adicionar geração de imagens~~
- [ ] Criar API de orquestração para coordenar agentes
- [ ] Implementar sistema de escolha/ranking de posts
- [ ] Interface web para testar os agentes
- [ ] Sistema de cache para respostas
- [ ] Integração com API do Instagram para publicação automática

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
