"""
Script para listar os modelos disponíveis na sua API Key do Google Gemini.
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carregar a API Key do arquivo .env do Agente 2
dotenv_path = os.path.join(os.path.dirname(__file__), 'agent2-gemini', '.env')
load_dotenv(dotenv_path=dotenv_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_api_key_here":
    print("❌ ERRO: GOOGLE_API_KEY não encontrada ou não configurada em 'agent2-gemini/.env'")
    exit()

try:
    genai.configure(api_key=GOOGLE_API_KEY)

    print("✅ Chave de API configurada. Buscando modelos...\n")
    print("="*50)
    print("Modelos disponíveis que suportam 'generateContent':")
    print("="*50)

    found_model = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            found_model = True

    if not found_model:
        print("\nNenhum modelo com suporte a 'generateContent' foi encontrado.")
        print("Verifique as permissões da sua API Key no Google AI Studio.")
    
    print("="*50)
    print("\nCopie um dos nomes de modelo acima e me informe qual usar.")

except Exception as e:
    print(f"❌ Ocorreu um erro ao conectar com a API do Google: {e}")

