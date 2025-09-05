# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from Parses import carregar_dados_de_arquivo
from GeminiAPI import gerar_analise_de_credito
from Empresa import Empresa
from typing import List

app = FastAPI()

# HABILITAR CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)


# Carrega os dados uma vez quando a aplicação inicia
print("Iniciando a aplicação e carregando a base de dados...")
LISTA_EMPRESAS: List[Empresa] = carregar_dados_de_arquivo('dados/dadoscreditoficticios.csv', debug=False)
print(f"{len(LISTA_EMPRESAS)} empresas carregadas.")

@app.get("/analise/{nome_empresa}")
def analisar_empresa_endpoint(nome_empresa: str):
    print(f"Recebida requisição para analisar: {nome_empresa}")
    
    empresa_encontrada = next((emp for emp in LISTA_EMPRESAS if emp.nome == nome_empresa), None)
            
    if not empresa_encontrada:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
    try:
        analise = gerar_analise_de_credito(empresa_encontrada)
        return {"empresa": nome_empresa, "analise_de_credito": analise}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar análise: {e}")

@app.get("/empresas")
def listar_empresas_endpoint():
    """Endpoint bônus para o frontend poder listar as empresas."""
    return {"nomes": [emp.nome for emp in LISTA_EMPRESAS]}