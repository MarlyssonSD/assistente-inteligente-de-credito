# interface.py
import streamlit as st
import requests

st.set_page_config(page_title="Assistente de Crédito", page_icon="🤖", layout="wide")
API_URL = "http://127.0.0.1:8000"

# --- Interface ---
st.title("🤖 Assistente Inteligente para Análise de Crédito")
st.markdown("Selecione uma empresa para análise ou para simular cenários de crédito.")

try:
    res = requests.get(f"{API_URL}/empresas")
    if res.status_code == 200:
        lista_nomes = res.json().get("nomes", [])
        empresa_selecionada = st.selectbox("Selecione a Empresa", options=lista_nomes, index=None, placeholder="...")
    else:
        st.error("Nao foi possivel carregar a lista de empresas.")
        empresa_selecionada = None
except requests.exceptions.ConnectionError:
    st.error("Backend offline. Verifique se o servidor FastAPI esta rodando.")
    empresa_selecionada = None

# --- Container para exibir os resultados ---
resultado_container = st.container()

# --- Ações do Usuário ---
if empresa_selecionada:
    if st.button("Analisar Crédito", use_container_width=True):
        with st.spinner(f"Analisando **{empresa_selecionada}**..."):
            res = requests.get(f"{API_URL}/analise/{empresa_selecionada}")
            if res.status_code == 200:
                resultado = res.json()
                analise_texto = resultado.get("analise_de_credito", "Erro ao obter analise.")
                # Exibe o resultado dentro de uma área de texto
                resultado_container.text_area("Resultado da Análise", value=analise_texto, height=300, disabled=True)
            else:
                st.error(f"Erro na análise: {res.json().get('detail', 'Erro desconhecido')}")

    # Simulação (Simplificada para texto)
    st.divider()
    with st.form("formulario_simulacao"):
        st.subheader(f"🔬 Simular Cenário para: {empresa_selecionada}")
        receita = st.number_input("Alterar Receita Anual para:", value=None)
        divida = st.number_input("Alterar Dívida Total para:", value=None)
        
        if st.form_submit_button("Simular Cenário"):
            alteracoes = {}
            if receita is not None: alteracoes["receita_anual"] = receita
            if divida is not None: alteracoes["divida_total"] = divida
            
            if not alteracoes:
                st.warning("Nenhum parametro de simulacao foi alterado.")
            else:
                payload = {"nome_empresa": empresa_selecionada, "alteracoes": alteracoes}
                with st.spinner("Executando simulacao..."):
                    res = requests.post(f"{API_URL}/simular", json=payload)
                    if res.status_code == 200:
                        resultado = res.json()
                        analise_texto = resultado.get("analise_simulada", "Erro ao obter analise simulada.")
                        resultado_container.text_area(f"Resultado da Simulação (Cenário: {resultado.get('cenario_simulado')})", value=analise_texto, height=300, disabled=True)
                    else:
                        st.error(f"Erro na simulacao: {res.json().get('detail', 'Erro desconhecido')}")