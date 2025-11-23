# Sistema Distribuído de IA para Geração de Posts do Instagram

Sistema distribuído com múltiplos agentes de IA para geração inteligente de conteúdo para Instagram. O sistema orquestra uma IA local e uma IA em nuvem para criar legendas otimizadas e prompts detalhados para imagens.

## 📋 Arquitetura

```

Trab\_SD/
├── agent1-local/       \# Agente 1 - Ollama + Llama3.2:1b (Local)
│   ├── Dockerfile
│   ├── app.py          \# API FastAPI
│   └── entrypoint.sh
├── agent2-gemini/      \# Agente 2 - Google Gemini (Cloud)
│   ├── Dockerfile
│   ├── app.py          \# API FastAPI
│   └── outputs/        \# Prompts de imagem gerados
├── api/                \# Orquestrador e Interface Web
│   ├── Dockerfile
│   ├── web\_app.py      \# Servidor Principal
│   └── index.html      \# Frontend
├── docker-compose.yml
└── test\_full\_flow.ps1  \# Script de teste do fluxo completo

````

## 🚀 Funcionalidades Principais

1.  **Geração Híbrida:** Combina velocidade/privacidade local com inteligência de nuvem.
2.  **Interface Web:** Dashboard interativo para gerar e visualizar posts.
3.  **Histórico:** Salva todos os posts gerados localmente em JSON.
4.  **Agentes Especializados:**
    * **Agent 1 (Local):** Gera o rascunho inicial bruto.
    * **Agent 2 (Cloud):** Refina o texto (SEO/Copywriting) e cria direção de arte para imagens.

---

## 🛠️ Como Rodar

### Pré-requisitos
* Docker e Docker Compose instalados.
* Mínimo 4GB de RAM disponível.
* Chave de API do Google Gemini.

### Configuração

1.  **Configure a API Key do Gemini:**
    ```bash
    # Copie o exemplo
    cp agent2-gemini/.env.example agent2-gemini/.env
    
    # Edite e insira sua chave (GOOGLE_API_KEY)
    # Acesse: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
    ```

2.  **Inicie o Sistema:**
    ```bash
    docker-compose up --build
    ```
    *Aguarde o download do modelo Llama (pode demorar alguns minutos na primeira vez).*

3.  **Acesse a Interface:**
    Abra seu navegador em: **`http://localhost:8000`**

---

## 🧩 Detalhes dos Serviços

### 1. Web API (Orquestrador)
O cérebro do sistema. Recebe o pedido do usuário, coordena os agentes e apresenta o resultado.

* **URL:** `http://localhost:8000`
* **Endpoints Principais:**
    * `GET /`: Interface Web
    * `POST /api/generate-post`: Dispara o workflow completo
    * `GET /api/history`: Lista posts anteriores

### 2. Agent 1 - Rascunhador (Local)
Serviço local utilizando **Ollama** com modelo **Llama 3.2**. Focado em gerar a base do conteúdo sem custo.

* **URL:** `http://localhost:8001`
* **Modelo:** `llama3.2:1b`
* **Endpoint:**
    * `POST /api/tools/generate_draft`
    * Body: `{"topic": "...", "style": "...", "tone": "..."}`

### 3. Agent 2 - Especialista (Cloud)
Serviço em nuvem utilizando **Google Gemini**. Focado em refinamento de texto e direção de arte.

* **URL:** `http://localhost:8002`
* **Modelo Utilizado:** `gemini-2.5-flash`
* **Endpoints:**
    * `POST /improve`: Melhora a legenda e adiciona hashtags.
    * `POST /generate-image`: Gera um **prompt descritivo detalhado** para criação de imagens (salvo em `.txt`).

---

## 🔄 Workflow do Sistema

Quando você solicita um post na interface web:

1.  **Web API** envia o tema para o **Agent 1**.
2.  **Agent 1** (Llama) escreve um rascunho simples.
3.  **Web API** pega o rascunho e envia para o **Agent 2**.
4.  **Agent 2** (Gemini) reescreve o texto com tom profissional e gera hashtags.
5.  **Agent 2** analisa o texto final e cria um **Prompt de Imagem** detalhado (descrição de iluminação, cenário, estilo).
6.  **Web API** exibe o Texto Final e o Prompt de Imagem para o usuário.

---

## 🧪 Testando via Terminal

Você pode testar os agentes individualmente se desejar:

**Testar Agent 1 (Gerar Rascunho):**
```bash
curl -X POST http://localhost:8001/api/tools/generate_draft \
  -H "Content-Type: application/json" \
  -d '{"topic": "Inteligência Artificial", "style": "Técnico", "tone": "Informativo"}'
````

**Testar Agent 2 (Melhorar Texto):**

```bash
curl -X POST http://localhost:8002/improve \
  -H "Content-Type: application/json" \
  -d '{"draft_text": "IA é legal", "style": "Profissional", "target_audience": "Devs"}'
```

-----

## 📝 Notas Importantes

  * **Geração de Imagem:** Atualmente, o Agent 2 gera um **arquivo de texto** com a descrição detalhada (prompt) para a imagem, e não o arquivo de imagem (.jpg/.png) em si. Isso permite que você copie o prompt e use em geradores de sua preferência (Midjourney, DALL-E, etc) ou no próprio Imagen futuramente.
  * **Persistência:** O modelo do Ollama é salvo no volume `ollama-models` para evitar downloads repetidos.
  * **API Key:** O Agent 2 não funcionará sem uma chave válida do Google Gemini configurada no `.env`.
