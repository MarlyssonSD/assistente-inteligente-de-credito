# GeminiAPI.py

"""
Módulo central de interação com a API Generativa do Google (Gemini).
Responsável por formatar os dados da empresa em um prompt estruturado
e processar a resposta da IA para gerar a análise de crédito.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from Empresa import Empresa as emp

# --- Configuração Inicial ---

# Carregar variáveis do .env
load_dotenv()

# Configurar a chave
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modelos
model = genai.GenerativeModel("gemini-2.5-flash")
# model = genai.GenerativeModel("gemini-2.5-pro")


def gerar_analise_de_credito(empresa: emp) -> str:
    """
    Gera uma análise de crédito textual para uma única empresa usando a IA Generativa.

    Esta função implementa a lógica central de RAG (Retrieval-Augmented Generation):
    1. Recebe os dados específicos de uma empresa (empresa).
    2. Formata esses dados em um prompt detalhado.
    3. Define regras estritas para a IA (ex: formato de saída, proibição de formatação)
       para garantir consistência e evitar problemas de renderização.
    4. Captura e trata erros de segurança da API da IA.

    Args:
        empresa (emp.Empresa): Objeto contendo todos os dados da empresa a ser analisada.

    Returns:
        str: A análise de crédito textual gerada pela IA ou uma mensagem de erro formatada.
    """
    
    # 1. Formatação dos dados de entrada para o prompt.
    # Simplificamos os dados (sem R$, etc.) para evitar que a IA se confunda
    # ou gere artefatos de formatação indesejados.
    dados_formatados = f"""
    - Nome da Empresa: {empresa.nome}
    - Setor de Atuacao: {empresa.setor}
    - Receita Anual: {empresa.receita_anual}
    - Divida Total: {empresa.divida_total}
    - Prazo Medio de Pagamento: {empresa.prazo_pagamento} dias
    - Rating de Credito Atual: {empresa.rating}
    - Resumo de Noticias Recentes: "{empresa.noticias_recentes}"
    """

    # 2. Construção do prompt com engenharia de prompt detalhada.
    # As instruções são explícitas para mitigar "alucinações" e forçar
    # a IA a gerar um texto limpo e sem formatação complexa (Markdown).
    prompt = f"""
    **Instrucoes Criticas:**
    1.  Voce e um analista de credito senior. Sua resposta deve ser em **TEXTO PURO**.
    2.  **NAO USE** formatacao Markdown (sem **, *, #, etc).
    3.  **NAO USE** acentos ou caracteres especiais complexos (ex: ç, ´, ~). Escreva "aprovacao", "decisao", "credito".
    4.  Baseie-se **APENAS** nos dados fornecidos abaixo.

    **Dados da Empresa para Analise:**
    {dados_formatados}

    **Tarefa de Analise:**
    Gere um parecer de credito seguindo o formato abaixo:

    Recomendacao Preliminar: (Escolha UMA: Aprovar Credito, Aprovar com Cautela, Recusar Credito).

    Justificativa da Decisao: (Escreva um paragrafo explicando o motivo da recomendacao, conectando os dados fornecidos).

    Principais Pontos de Risco:
    - (Liste o primeiro risco aqui).
    - (Liste o segundo risco aqui).
    """
    
    print(f"\nINFO: Gerando analise para {empresa.nome}...")
    
    try:
        # 3. Chamada para a API Generativa
        response = model.generate_content(prompt)

        # 4. Tratamento de bloqueios de segurança da IA.
        # Se response.parts estiver vazio, significa que a IA bloqueou a resposta
        # por motivos de segurança (ex: política de conteúdo financeiro).
        if not response.parts:
            block_reason = "Nao especificado"
            if response.prompt_feedback:
                block_reason = response.prompt_feedback.block_reason.name
            error_message = f"ERRO: A analise foi bloqueada pelo filtro de seguranca da IA. Motivo: {block_reason}."
            print(f"!!! ANALISE BLOQUEADA. Motivo: {block_reason} !!!")
            return error_message

        print(f"INFO: Analise para {empresa.nome} gerada com sucesso.")
        return response.text

    except Exception as e:
        error_message = f"ERRO INESPERADO: Falha na comunicacao com a API de IA. Detalhes: {str(e)}"
        print(f"!!! ERRO NA API: {e} !!!")
        return error_message