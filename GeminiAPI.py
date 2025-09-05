import os
import google.generativeai as genai
from dotenv import load_dotenv
from Empresa import Empresa as emp
from Parses import carregar_dados_de_arquivo


# Carregar variáveis do .env
load_dotenv()

# Configurar a chave
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modelos
model = genai.GenerativeModel("gemini-2.5-flash")
# model = genai.GenerativeModel("gemini-2.5-pro")


# Função de análise APRIMORADA
def gerar_analise_de_credito(empresa: emp) -> str:
    """
    Gera uma análise de crédito de forma robusta, com tratamento de erros
    e verificação de bloqueios de segurança da API.
    """
    dados_formatados = f"""
    - Nome da Empresa: {empresa.nome}
    - Setor de Atuação: {empresa.setor}
    - Receita Anual: R$ {empresa.receita_anual:,}
    - Dívida Total: R$ {empresa.divida_total:,}
    - Prazo Médio de Pagamento: {empresa.prazo_pagamento} dias
    - Rating de Crédito Atual: {empresa.rating}
    - Resumo de Notícias Recentes: "{empresa.noticias_recentes}"
    """

    prompt = f"""
    **Contexto:** Você é um assistente de IA especialista em análise de crédito. Sua única e exclusiva fonte de informação para a tarefa abaixo são os dados fornecidos no campo "Dados da Empresa". Você está proibido de usar conhecimento externo ou solicitar mais informações. Sua resposta DEVE ser baseada 100% nos dados a seguir.

    **Dados da Empresa:**
    {dados_formatados}

    **Tarefa Obrigatória:**
    Com base estritamente nos "Dados da Empresa" acima, gere um parecer de crédito estruturado exatamente no formato abaixo. Não inclua preâmbulos ou notas adicionais.

    **Formato da Resposta:**
    1.  Recomendação Preliminar: (Escolha UMA: "Aprovar Concessão de Crédito", "Aprovar com Cautela", "Recusar Concessão de Crédito").
    2.  Justificativa da Decisão: (Um parágrafo explicando o raciocínio, conectando os diferentes dados fornecidos).
    3.  Principais Pontos de Risco: (Liste em formato de tópicos 2 a 3 riscos observados nos dados).
    """
    
    print("\n--- Tentando gerar análise com a IA (Versão Robusta) ---")
    
    try:
        # Tenta gerar o conteúdo
        response = model.generate_content(prompt)

        # ---- VERIFICAÇÃO DE SEGURANÇA E VALIDADE ----
        # 1. Verifica se a resposta tem partes válidas. Se não tiver, foi bloqueada.
        if not response.parts:
            # Tenta encontrar o motivo do bloqueio para dar uma mensagem mais clara
            block_reason = response.prompt_feedback.block_reason.name if response.prompt_feedback else "Não especificado"
            error_message = f"**ERRO:** A análise foi bloqueada pelo filtro de segurança da IA. Motivo: {block_reason}. Tente reformular o prompt ou analisar outra empresa."
            print(f"!!! ANÁLISE BLOQUEADA. Motivo: {block_reason} !!!")
            return error_message

        # 2. Se passou, retorna o texto normalmente
        print("--- Análise gerada com sucesso ---")
        return response.text

    except Exception as e:
        # Captura qualquer outro erro inesperado durante a chamada da API
        error_message = f"**ERRO INESPERADO:** Ocorreu uma falha na comunicação com a API de IA. Detalhes: {str(e)}"
        print(f"!!! ERRO NA API: {e} !!!")
        return error_message


# MAIN
if __name__ == "__main__":
    # nome_da_empresa = "Empresa 4987"
    # nome_da_empresa = "Empresa 4976"
    nome_da_empresa = "Empresa 4957"
    
    print("Carregando dados das empresas...")
    # Usando a função dinâmica que você criou para carregar os dados do CSV
    lista_de_empresas = carregar_dados_de_arquivo('dados/dadoscreditoficticios.csv', debug=True)
    print(f"{len(lista_de_empresas)} registros carregados com sucesso.")


    empresa_para_analise = None
    for empresa in lista_de_empresas:
        if empresa.nome == nome_da_empresa:
            empresa_para_analise = empresa
            break

    if not empresa_para_analise:
        raise ValueError(f"{nome_da_empresa} não encontrada nos dados!")

    print(f"\nEmpresa selecionada para análise: {empresa_para_analise.nome}")
    
    analise_gerada = gerar_analise_de_credito(empresa_para_analise)
    print("\n--- Análise de Crédito Gerada ---")
    print(analise_gerada)