# interface.py
import streamlit as st
import requests

st.set_page_config(page_title="Assistente de Crédito", page_icon="🤖", layout="wide")
API_URL = "http://127.0.0.1:8000"

# --- Função de Ordenação customizada ---
def chave_de_ordenacao_numerica(nome_empresa):
    try:
        numero = int(nome_empresa.split(' ')[1])
        return numero
    except (IndexError, ValueError):
        return float('inf')

# --- Interface ---
st.title("🤖 Assistente Inteligente para Análise de Crédito")
st.markdown("Selecione uma empresa para visualizar seus dados e iniciar a análise.")

# --- Carregamento Inicial da Lista de Empresas ---
try:
    res = requests.get(f"{API_URL}/empresas")
    if res.status_code == 200:
        lista_nomes_desordenada = res.json().get("nomes", [])
        lista_nomes = sorted(lista_nomes_desordenada, key=chave_de_ordenacao_numerica)
    else:
        lista_nomes = []
        st.error("Nao foi possivel carregar a lista de empresas.")
except requests.exceptions.ConnectionError:
    lista_nomes = []
    st.error("Backend offline. Verifique se o servidor FastAPI esta rodando.")

# --- Seleção da Empresa ---
empresa_selecionada = st.selectbox(
    "Selecione a Empresa",
    options=lista_nomes,
    index=None,
    placeholder="Digite ou selecione um nome..."
)

# --- Inicialização do Estado da Sessão para guardar o resultado ---
if 'resultado_texto' not in st.session_state:
    st.session_state.resultado_texto = ""
if 'titulo_resultado' not in st.session_state:
    st.session_state.titulo_resultado = ""

# --- Container de Ação Principal (Dados + Ações) ---
if empresa_selecionada:
    # 1. Exibir Dados da Empresa (Exatamente como no seu código)
    try:
        res = requests.get(f"{API_URL}/empresa/{empresa_selecionada}")
        if res.status_code == 200:
            dados_empresa = res.json()
            with st.container(border=True): # Agrupa visualmente
                st.subheader(f"Dados Cadastrais de: {dados_empresa.get('nome')}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Receita Anual", f"R$ {dados_empresa.get('receita_anual', 0):,}")
                    st.metric("Setor", dados_empresa.get('setor', 'N/A'))
                with col2:
                    st.metric("Dívida Total", f"R$ {dados_empresa.get('divida_total', 0):,}")
                    st.metric("Rating", dados_empresa.get('rating', 'N/A'))
                with col3:
                    st.metric("Prazo Pagamento", f"{dados_empresa.get('prazo_pagamento', 0)} dias")
                st.text_area("Notícias Recentes", value=dados_empresa.get('noticias_recentes', 'N/A'), height=100, disabled=True)
    except Exception as e:
        st.error(f"Nao foi possivel buscar os dados da empresa: {e}")

    st.divider()

    # 2. Ações do Usuário (Análise e Simulação) - Movidas para cima no fluxo lógico
    col_analise, col_simulacao = st.columns([1, 2]) # [proporção de tamanho]

    # Coluna de Análise Simples
    with col_analise:
        st.markdown("**Análise Padrão**")
        st.markdown("Clique para gerar a análise completa com os dados atuais.")
        if st.button("Analisar Crédito", use_container_width=True, type="primary"):
            with st.spinner(f"Analisando **{empresa_selecionada}**..."):
                res = requests.get(f"{API_URL}/analise/{empresa_selecionada}")
                if res.status_code == 200:
                    resultado = res.json()
                    st.session_state.titulo_resultado = f"Resultado da Análise Padrão para **{empresa_selecionada}**"
                    st.session_state.resultado_texto = resultado.get("analise_de_credito", "Erro ao obter analise.")
                else:
                    st.error(f"Erro na análise: {res.json().get('detail', 'Erro desconhecido')}")

    # Coluna de Simulação
    with col_simulacao:
        with st.form("formulario_simulacao"):
            st.markdown("**Simular Cenário**")
            receita = st.number_input("Alterar Receita Anual para:", value=None, key="sim_receita")
            divida = st.number_input("Alterar Dívida Total para:", value=None, key="sim_divida")
            
            if st.form_submit_button("Executar Simulação", use_container_width=True):
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
                            st.session_state.titulo_resultado = f"Resultado da Simulação para **{empresa_selecionada}** (Cenário: {resultado.get('cenario_simulado')})"
                            st.session_state.resultado_texto = resultado.get("analise_simulada", "Erro ao obter analise simulada.")
                        else:
                            st.error(f"Erro na simulacao: {res.json().get('detail', 'Erro desconhecido')}")

# --- Área de Resultados Dedicada ---
st.divider()
st.subheader("Resultado da Análise da IA")

if st.session_state.resultado_texto:
    st.markdown(st.session_state.titulo_resultado)
    st.text_area("", value=st.session_state.resultado_texto, height=300, disabled=True)
else:
    st.info("O resultado da análise aparecerá aqui.")