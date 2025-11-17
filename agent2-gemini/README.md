# Agent 2 - Google Gemini

Agente que utiliza Google Gemini API para melhorar captions e gerar imagens para posts do Instagram.

## 🔑 Configuração

### Obter API Key

1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### Configurar .env

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env e adicionar sua chave
# GOOGLE_API_KEY=sua_chave_aqui
```

## 🚀 Executar

```bash
# Voltar para raiz do projeto
cd ..

# Iniciar apenas Agent 2
docker-compose up --build agent2-gemini

# Ou iniciar todos os agentes
docker-compose up --build
```

## 📡 Endpoints

### POST /improve
Melhora uma caption de Instagram

**Request:**
```json
{
  "draft_text": "texto original",
  "style": "casual",
  "target_audience": "público-alvo"
}
```

### POST /generate-image
Gera imagem para o post

**Request:**
```json
{
  "prompt": "descrição da imagem",
  "style": "realistic"
}
```

### GET /health
Verifica status do agente

## 🧪 Testar

```bash
# Na raiz do projeto
python test_gemini.py
```

## 📊 Modelos Utilizados

- **Texto:** gemini-2.0-flash-exp (mais recente, gratuito)
- **Imagem:** imagen-3.0-generate-001

## 📝 Notas

- API gratuita tem limites de uso
- Imagens são salvas em `/app/outputs/`
- Geração de imagem pode levar 30-60 segundos
