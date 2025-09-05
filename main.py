from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Importar BaseModel
import copy # Importar copy

from Parses import carregar_dados_de_arquivo
from GeminiAPI import gerar_analise_de_credito
from Empresa import Empresa
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Dados (Pydantic) ---
class SimulacaoPayload(BaseModel):
    nome_empresa: str
    alteracoes: Dict[str, Any]

# --- Carregamento de Dados ---
print("Iniciando a aplicação e carregando a base de dados...")
LISTA_EMPRESAS: List[Empresa] = carregar_dados_de_arquivo('dados/dadoscreditoficticios.csv', debug=False)
print(f"{len(LISTA_EMPRESAS)} empresas carregadas.")

# --- Endpoints da API ---
@app.get("/empresas")
def listar_empresas_endpoint():
    return {"nomes": [emp.nome for emp in LISTA_EMPRESAS]}

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

# --- NOVO ENDPOINT DE SIMULAÇÃO ---
@app.post("/simular")
def simular_cenario_endpoint(payload: SimulacaoPayload):
    print(f"Recebida requisição de simulação para: {payload.nome_empresa}")
    print(f"Com as alterações: {payload.alteracoes}")

    empresa_original = next((emp for emp in LISTA_EMPRESAS if emp.nome == payload.nome_empresa), None)
    if not empresa_original:
        raise HTTPException(status_code=404, detail="Empresa não encontrada para simulação")

    # 1. Criar uma cópia profunda para não alterar os dados originais em memória
    empresa_simulada = copy.deepcopy(empresa_original)

    # 2. Aplicar as alterações do payload na cópia
    for campo, valor in payload.alteracoes.items():
        if hasattr(empresa_simulada, campo):
            # Tenta converter o valor para o tipo correto do campo
            tipo_original = type(getattr(empresa_simulada, campo))
            try:
                setattr(empresa_simulada, campo, tipo_original(valor))
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail=f"Valor inválido para o campo '{campo}'")
        else:
            raise HTTPException(status_code=400, detail=f"Campo desconhecido na simulação: '{campo}'")
    
    # 3. Gerar a nova análise com os dados simulados
    try:
        analise_simulada = gerar_analise_de_credito(empresa_simulada)
        return {"empresa": payload.nome_empresa, "cenario_simulado": payload.alteracoes, "analise_simulada": analise_simulada}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar análise simulada: {e}")