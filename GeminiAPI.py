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
    # 1. Formatar os dados do objeto em uma string clara
    dados_formatados = f"""
    - Nome da Empresa: {empresa.nome}
    - Setor de Atuação: {empresa.setor}
    - Receita Anual: R$ {empresa.receita_anual:,}
    - Dívida Total: R$ {empresa.divida_total:,}
    - Prazo Médio de Pagamento: {empresa.prazo_pagamento} dias
    - Rating de Crédito Atual: {empresa.rating}
    - Resumo de Notícias Recentes: "{empresa.noticias_recentes}"
    """

    # Prompt aprimorado
    prompt = f"""
    **Instrução:** Você é um analista de crédito sênior e cético, responsável por aprovar ou negar pedidos de crédito para o Banco XPTO. Sua análise deve ser baseada **exclusivamente** nos dados fornecidos abaixo. Não invente informações.

    **Dados da Empresa:**
    {dados_formatados}

    **Sua Tarefa:**
    Gere um parecer de crédito conciso e profissional no seguinte formato:

    1.  **Recomendação Preliminar:** (Escolha UMA e APENAS UMA das seguintes opções: "Aprovar Concessão de Crédito", "Aprovar com Cautela", "Recusar Concessão de Crédito").
    2.  **Justificativa da Decisão:** (Escreva um parágrafo explicando o raciocínio por trás da sua recomendação, conectando os pontos fortes e fracos identificados nos dados. Ex: A receita cobre a dívida? O rating é condizente com as notícias?).
    3.  **Principais Pontos de Risco:** (Liste em formato de tópicos 2 a 3 riscos principais que você observou).
    """
    
    print("\n--- Gerando análise com a IA ---")
    response = model.generate_content(prompt)
    return response.text


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