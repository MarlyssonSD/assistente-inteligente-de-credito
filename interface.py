# interface.py
import streamlit as st
import requests
import re

# --- Configuração da Página ---
st.set_page_config(
    page_title="Assistente de Análise de Crédito",
    page_icon="🤖",
    layout="wide"
)

# --- Constantes ---
API_URL = "http://127.0.0.1:8000" 

# --- Funções Auxiliares ---
def formatar_analise(texto_analise):
    """Formata o texto da IA usando Markdown para melhor visualização."""
    texto_formatado = re.sub(r'\*\*(.*?)\*\*', r'### \1', texto_analise) # Transforma **Texto** em ### Texto
    texto_formatado = re.sub(r'\* (.*?)\n', r'- \1\n', texto_formatado) # Transforma * Item em - Item
    return texto_formatado


# --- Interface Principal ---
st.title("🤖 Assistente Inteligente para Análise de Crédito")
st.markdown("Bem-vindo! Selecione uma empresa para iniciar a análise de crédito baseada em IA Generativa.")


# --- Carregar a lista de empresas do backend ---
try:
    response = requests.get(f"{API_URL}/empresas")
    if response.status_code == 200:
        lista_nomes = response.json().get("nomes", [])
        empresa_selecionada = st.selectbox(
            "Selecione a Empresa",
            options=lista_nomes,
            index=None,
            placeholder="Digite ou selecione uma empresa..."
        )
    else:
        st.error("Não foi possível carregar a lista de empresas do backend.")
        empresa_selecionada = None

except requests.exceptions.ConnectionError:
    st.error("Não foi possível conectar ao backend. Verifique se o servidor FastAPI está rodando.")
    empresa_selecionada = None


# --- Botão de Análise e Exibição dos Resultados ---
if st.button("Analisar Crédito", disabled=(not empresa_selecionada)):
    if empresa_selecionada:
        # Mostra uma mensagem de "carregando" enquanto espera
        with st.spinner(f"Analisando o perfil de crédito da **{empresa_selecionada}**... Por favor, aguarde."):
            try:
                # Chama o endpoint do FastAPI
                response = requests.get(f"{API_URL}/analise/{empresa_selecionada}")
                
                # Verifica se a chamada foi bem sucedida
                if response.status_code == 200:
                    resultado = response.json()
                    analise_texto = resultado.get("analise_de_credito", "Análise não disponível.")
                    
                    st.divider()
                    st.subheader(f"Parecer de Crédito para: {empresa_selecionada}")
                    
                    # Usa a função para formatar e exibir o resultado
                    st.markdown(formatar_analise(analise_texto))

                else: # Se a API retornar um erro (ex: 404, 500)
                    erro_detalhe = response.json().get("detail", "Erro desconhecido.")
                    st.error(f"Ocorreu um erro ao buscar a análise: {erro_detalhe}")

            except requests.exceptions.ConnectionError:
                st.error("Erro de conexão. Não foi possível se comunicar com o servidor de análise.")
            except Exception as e:
                st.error(f"Um erro inesperado ocorreu: {e}")