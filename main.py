# main.py

"""
Serviço de API para o Assistente de Análise de Crédito.
Fornece endpoints para listar empresas, obter detalhes de uma empresa,
executar análises de crédito padrão e simular cenários.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import copy
from typing import List, Dict, Any

# Importações dos módulos locais
from Parses import carregar_dados_de_arquivo
from GeminiAPI import gerar_analise_de_credito
from Empresa import Empresa

# --- Modelos de Dados Pydantic ---

class SimulacaoPayload(BaseModel):
    """Define a estrutura de dados esperada para o corpo da requisição de simulação."""
    nome_empresa: str
    alteracoes: Dict[str, Any]

# --- Inicialização da Aplicação FastAPI ---
app = FastAPI(
    title="Assistente de Análise de Crédito API",
    description="API para análise de crédito de PMEs usando IA Generativa.",
    version="1.0.0"
)

# Configuração do CORS para permitir que o frontend (Streamlit) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Carregamento de Dados e Estado da Aplicação ---

@app.on_event("startup")
def carregar_modelo_e_dados():
    """
    Função executada na inicialização do servidor. Carrega os dados das empresas
    para a memória da aplicação, evitando recargas a cada requisição.
    """
    try:
        caminho_dados = 'dados/dadoscreditoficticios.csv'
        app.state.lista_empresas = carregar_dados_de_arquivo(caminho_dados)
        print(f"INFO: Carregados {len(app.state.lista_empresas)} registros de empresas na inicialização.")
    except Exception as e:
        print(f"ERRO CRÍTICO na inicialização: Não foi possível carregar os dados. {e}")
        app.state.lista_empresas = []

# --- Endpoints da API ---

def get_lista_empresas(request: Request) -> List[Empresa]:
    """Função utilitária para acessar a lista de empresas do estado da aplicação."""
    return request.app.state.lista_empresas

@app.get("/empresas", summary="Lista todas as empresas disponíveis")
def listar_empresas_endpoint(request: Request):
    """
    Retorna uma lista contendo os nomes de todas as empresas carregadas na base de dados.
    """
    lista_nomes = [emp.nome for emp in get_lista_empresas(request)]
    return {"nomes": lista_nomes}

@app.get("/empresa/{nome_empresa}", summary="Obtém detalhes de uma empresa específica")
def get_empresa_details_endpoint(nome_empresa: str, request: Request):
    """
    Retorna os dados cadastrais completos de uma única empresa, buscada pelo nome.

    Args:
        nome_empresa (str): O nome exato da empresa a ser buscada.
    """
    empresa_encontrada = next((emp for emp in get_lista_empresas(request) if emp.nome == nome_empresa), None)
    if not empresa_encontrada:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa_encontrada # Pydantic/FastAPI converte automaticamente para JSON

@app.get("/analise/{nome_empresa}", summary="Executa análise de crédito padrão")
def analisar_empresa_endpoint(nome_empresa: str, request: Request):
    """
    Executa a análise de crédito padrão para a empresa especificada, utilizando
    os dados cadastrais atuais e o modelo de IA.

    Args:
        nome_empresa (str): O nome exato da empresa a ser analisada.
    """
    print(f"INFO: Recebida requisição de análise para: {nome_empresa}")
    empresa_encontrada = next((emp for emp in get_lista_empresas(request) if emp.nome == nome_empresa), None)
    if not empresa_encontrada:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    try:
        analise = gerar_analise_de_credito(empresa_encontrada)
        return {"empresa": nome_empresa, "analise_de_credito": analise}
    except Exception as e:
        print(f"ERRO: Falha ao gerar análise para {nome_empresa}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar análise de IA: {e}")

@app.post("/simular", summary="Executa simulação de cenário de crédito")
def simular_cenario_endpoint(payload: SimulacaoPayload, request: Request):
    """
    Executa uma análise de crédito simulada, aplicando alterações temporárias
    nos dados da empresa conforme solicitado pelo usuário.

    Args:
        payload (SimulacaoPayload): Objeto JSON contendo o nome da empresa e um
                                    dicionário de alterações (ex: {"receita_anual": 500000}).
    """
    print(f"INFO: Recebida requisição de simulação para: {payload.nome_empresa}")
    empresa_original = next((emp for emp in get_lista_empresas(request) if emp.nome == payload.nome_empresa), None)
    if not empresa_original:
        raise HTTPException(status_code=404, detail="Empresa não encontrada para simulação")

    # 1. Cria uma cópia profunda para evitar modificar os dados originais em cache.
    # Isso garante que a simulação de um usuário não afete a análise de outro.
    empresa_simulada = copy.deepcopy(empresa_original)

    # 2. Aplica as alterações dinamicamente.
    # Esta abordagem flexível permite que o frontend adicione novos campos de simulação
    # sem exigir alterações no código do backend, contanto que o nome do campo exista na classe Empresa.
    for campo, valor in payload.alteracoes.items():
        if hasattr(empresa_simulada, campo):
            tipo_original = type(getattr(empresa_simulada, campo))
            try:
                # Converte o valor recebido para o tipo original do atributo da classe
                setattr(empresa_simulada, campo, tipo_original(valor))
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail=f"Valor inválido para o campo '{campo}': {valor}")
        else:
            logging.warning(f"Tentativa de simular campo inexistente: '{campo}'")
    
    # 3. Gera a nova análise com base nos dados simulados.
    try:
        analise_simulada = gerar_analise_de_credito(empresa_simulada)
        return {"empresa": payload.nome_empresa, "cenario_simulado": payload.alteracoes, "analise_simulada": analise_simulada}
    except Exception as e:
        print(f"ERRO: Falha ao gerar análise simulada para {payload.nome_empresa}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar simulação de IA: {e}")