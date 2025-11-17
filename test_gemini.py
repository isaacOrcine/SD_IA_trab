"""
Script de teste para validar o Agent 2 - Gemini
"""
import requests
import json
import sys

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8002"


def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")


def test_root():
    """Testa o endpoint raiz"""
    print_header("Teste 1: GET /")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Agente: {data.get('agent')}")
            print_info(f"Modelos: {json.dumps(data.get('models'), indent=2)}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False


def test_health():
    """Testa o healthcheck"""
    print_header("Teste 2: GET /health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Health: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False


def test_improve_caption():
    """Testa melhoria de caption"""
    print_header("Teste 3: POST /improve")
    
    draft = """dia incrivel na praia!! sol mar e muita diversao 
    #praia #verao"""
    
    payload = {
        "draft_text": draft,
        "style": "casual",
        "target_audience": "jovens adultos"
    }
    
    print_info(f"Draft original:\n{draft}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/improve",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Agente: {data.get('agent')}")
            print_info(f"Modelo: {data.get('model')}")
            print(f"\n{YELLOW}Texto melhorado:{RESET}")
            print(data.get('improved_text'))
            print(f"\n{YELLOW}Hashtags:{RESET}")
            print(" ".join(data.get('hashtags', [])))
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return False
    except requests.Timeout:
        print_error("Timeout - API do Gemini pode estar processando")
        return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False


def test_generate_image():
    """Testa geração de imagem"""
    print_header("Teste 4: POST /generate-image")
    
    payload = {
        "prompt": "beautiful sunset at the beach with palm trees",
        "style": "realistic"
    }
    
    print_info(f"Prompt: {payload['prompt']}")
    print_info(f"Style: {payload['style']}")
    print_info("⏳ Gerando imagem... (isso pode demorar 30-60 segundos)\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-image",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Agente: {data.get('agent')}")
            print_info(f"Modelo: {data.get('model')}")
            print_success(f"Imagem salva em: {data.get('image_path')}")
            print_info(f"Prompt usado: {data.get('prompt_used')[:80]}...")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return False
    except requests.Timeout:
        print_error("Timeout - Geração de imagem levou muito tempo")
        return False
    except Exception as e:
        print_error(f"Erro: {str(e)}")
        return False


def main():
    print_header("TESTES DO AGENT 2 - GOOGLE GEMINI")
    
    # Verificar se o servidor está rodando
    print_info("Verificando se o servidor está rodando...")
    try:
        requests.get(f"{BASE_URL}/", timeout=5)
    except requests.exceptions.ConnectionError:
        print_error("Servidor não está rodando!")
        print_info("Execute: docker-compose up agent2-gemini")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        sys.exit(1)
    
    # Executar testes
    results = []
    
    results.append(("GET /", test_root()))
    results.append(("GET /health", test_health()))
    results.append(("POST /improve", test_improve_caption()))
    results.append(("POST /generate-image", test_generate_image()))
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASSOU{RESET}" if result else f"{RED}FALHOU{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{YELLOW}Total: {passed}/{total} testes passaram{RESET}\n")
    
    if passed == total:
        print_success("Todos os testes passaram! 🎉")
        sys.exit(0)
    else:
        print_error(f"{total - passed} teste(s) falharam")
        sys.exit(1)


if __name__ == "__main__":
    main()
