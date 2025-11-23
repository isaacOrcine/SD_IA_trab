# Script de teste completo para o sistema de geração de posts
# Testa os dois agentes em sequência

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE COMPLETO - SISTEMA DE POSTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se os serviços estão rodando
Write-Host "[1/4] Verificando conectividade dos agentes..." -ForegroundColor Yellow

try {
    $agent1Health = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5
    Write-Host "✓ Agente 1 (Ollama) está online" -ForegroundColor Green
} catch {
    Write-Host "✗ Agente 1 (Ollama) não está respondendo na porta 8001" -ForegroundColor Red
    Write-Host "  Execute 'docker-compose up' antes de rodar este teste." -ForegroundColor Red
    exit 1
}

try {
    $agent2Health = Invoke-RestMethod -Uri "http://localhost:8002/health" -TimeoutSec 5
    Write-Host "✓ Agente 2 (Gemini) está online" -ForegroundColor Green
} catch {
    Write-Host "✗ Agente 2 (Gemini) não está respondendo na porta 8002" -ForegroundColor Red
    Write-Host "  Execute 'docker-compose up' antes de rodar este teste." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Teste 1: Gerar rascunho com o Agente 1
Write-Host "[2/4] Gerando rascunho com Agente 1 (Ollama)..." -ForegroundColor Yellow

$tema = "A importância de participar de uma empresa júnior para o desenvolvimento profissional"

$bodyAgente1 = @{
    topic = $tema
    style = "motivacional"
} | ConvertTo-Json

try {
    $rascunho = Invoke-RestMethod -Method Post -Uri "http://localhost:8001/generate" -Body $bodyAgente1 -ContentType "application/json" -TimeoutSec 60
    
    Write-Host "✓ Rascunho gerado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "--- RASCUNHO GERADO ---" -ForegroundColor Cyan
    Write-Host $rascunho.draft -ForegroundColor White
    Write-Host "----------------------" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "✗ Erro ao gerar rascunho: $_" -ForegroundColor Red
    exit 1
}

# Teste 2: Melhorar o rascunho com o Agente 2
Write-Host "[3/4] Refinando legenda com Agente 2 (Gemini)..." -ForegroundColor Yellow

$bodyAgente2Improve = @{
    draft_text = $rascunho.draft
    style = "profissional"
} | ConvertTo-Json

try {
    $legendaFinal = Invoke-RestMethod -Method Post -Uri "http://localhost:8002/improve" -Body $bodyAgente2Improve -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "✓ Legenda refinada com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "--- LEGENDA FINAL ---" -ForegroundColor Cyan
    Write-Host $legendaFinal.improved_text -ForegroundColor White
    Write-Host ""
    Write-Host "--- HASHTAGS ---" -ForegroundColor Cyan
    Write-Host ($legendaFinal.hashtags -join " ") -ForegroundColor White
    Write-Host "--------------------" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "✗ Erro ao refinar legenda: $_" -ForegroundColor Red
    exit 1
}

# Teste 3: Gerar prompt de imagem com o Agente 2
Write-Host "[4/4] Gerando prompt de imagem com Agente 2 (Gemini)..." -ForegroundColor Yellow

$bodyAgente2Image = @{
    prompt = "jovens universitários trabalhando juntos em projetos de tecnologia em uma empresa júnior moderna"
} | ConvertTo-Json

try {
    $imagemPrompt = Invoke-RestMethod -Method Post -Uri "http://localhost:8002/generate-image" -Body $bodyAgente2Image -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "✓ Prompt de imagem gerado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "--- INFORMAÇÕES DA IMAGEM ---" -ForegroundColor Cyan
    Write-Host "Arquivo salvo em: $($imagemPrompt.image_path)" -ForegroundColor White
    Write-Host "Modelo usado: $($imagemPrompt.model)" -ForegroundColor White
    Write-Host "-----------------------------" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "✗ Erro ao gerar prompt de imagem: $_" -ForegroundColor Red
    exit 1
}

# Resumo final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE CONCLUÍDO COM SUCESSO! ✓" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resumo do fluxo:" -ForegroundColor Yellow
Write-Host "1. ✓ Agente 1 gerou o rascunho inicial" -ForegroundColor Green
Write-Host "2. ✓ Agente 2 refinou a legenda e adicionou hashtags" -ForegroundColor Green
Write-Host "3. ✓ Agente 2 criou um prompt detalhado para a imagem" -ForegroundColor Green
Write-Host ""
Write-Host "O sistema está funcionando perfeitamente!" -ForegroundColor Green
Write-Host "Verifique a pasta 'agent2-gemini/outputs' para ver o arquivo de descrição da imagem." -ForegroundColor Yellow
