# Assistente Inteligente de Análise de Crédito

## 1. Visão Geral do Projeto

Este projeto consiste em um assistente baseado em Inteligência Artificial Generativa, projetado para otimizar o processo de análise de crédito para Pequenas e Médias Empresas (PMEs). A solução ingere dados de múltiplas fontes, identifica riscos e oportunidades, gera recomendações preliminares e permite a simulação interativa de cenários de crédito.

O objetivo principal é fornecer aos analistas de crédito uma ferramenta que aumente sua produtividade, reduza vieses e permita uma tomada de decisão mais profunda e fundamentada em dados.

---

## 2. Principais Funcionalidades

* **Análise de Crédito Automatizada:** Gera um parecer completo (recomendação, justificativa e pontos de risco) com base nos dados financeiros e contextuais da empresa.
* **Simulação de Cenários "What-If":** Permite ao analista ajustar parâmetros-chave da empresa (como Receita Anual, Dívida Total, Prazo de Pagamento e Rating) para testar a resiliência do perfil de crédito em diferentes cenários.
* **Ingestão de Múltiplos Formatos de Dados:** O sistema é capaz de processar dados de fontes variadas nos formatos CSV, JSON, XML e Parquet.
* **Interface Interativa:** Interface web amigável construída com Streamlit para facilitar a interação do analista com os dados e com a IA.

---

## 3. Arquitetura da Solução

A solução segue uma arquitetura de microsserviços desacoplada, com uma clara separação entre frontend e backend:

* **Frontend:** Uma aplicação web interativa desenvolvida em **Streamlit**. É responsável por toda a interação com o usuário, coleta de inputs de simulação e exibição dos resultados.
* **Backend:** Uma API RESTful robusta construída com **FastAPI**. Gerencia a lógica de negócios, o processamento de dados, as regras de simulação e a comunicação com o modelo de IA.
* **Módulo de IA Generativa:** Utiliza a API do **Google Gemini** para a geração das análises textuais. A abordagem de **RAG (Retrieval-Augmented Generation)** é simulada ao fornecer os dados específicos da empresa como contexto para cada consulta, mitigando alucinações e garantindo que a análise seja baseada em fatos.
* **Módulo de Ingestão de Dados:** Camada de parsing que lida com a leitura e padronização dos diferentes formatos de arquivos de entrada.

---

## 4. Estrutura dos Arquivos do Projeto
.
├── dados/                    # Pasta para armazenar os arquivos de dados brutos
│   ├── dadoscreditoficticios.csv
│   ├── dadoscreditoficticios.json
│   ├── dadoscreditoficticios.xml
│   └── dadoscreditoficticios.parquet
├── Empresa.py              # Define o modelo de dados canônico (Dataclass) da empresa.
├── Parses.py               # Contém as funções para ler e processar os arquivos (CSV, JSON, XML, Parquet).
├── GeminiAPI.py            # Gerencia a lógica de prompt e a comunicação com a API do Google Gemini.
├── main.py                 # Backend: Aplicação FastAPI com os endpoints da API (/analise, /simular, etc.).
├── interface.py            # Frontend: Aplicação Streamlit (a interface do usuário).
├── requirements.txt        # Lista de dependências Python do projeto.
└── .env                    # Arquivo de configuração para armazenar chaves secretas (ex: API Key).

---

## 5. Pré-requisitos e Instalação

Antes de começar, garanta que você tenha o Python 3.9 (ou superior) instalado.

### 5.1. Configuração do Ambiente

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/nome-do-repositorio.git](https://github.com/seu-usuario/nome-do-repositorio.git)
    cd nome-do-repositorio
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### 5.2. Chave de API

O projeto requer acesso à API do Google Gemini.

1.  Crie uma chave de API no [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Crie um arquivo chamado `.env` na raiz do projeto.
3.  Adicione sua chave de API ao arquivo `.env` da seguinte forma:
    ```env
    GEMINI_API_KEY=SUA_CHAVE_DE_API_AQUI
    ```

---

## 6. Como Executar a Aplicação

A aplicação consiste em dois componentes que precisam ser executados separadamente: o backend (FastAPI) e o frontend (Streamlit).

### Terminal 1: Iniciar o Backend (API)

Execute o servidor FastAPI usando o Uvicorn:

```bash
uvicorn main:app --reload
```

### Terminal 2: Iniciar o Frontend (Interface do Usuário)

Em um novo terminal (com o ambiente virtual ativado), execute a aplicação Streamlit:

```bash
streamlit run interface.py
```
O Streamlit abrirá automaticamente o seu navegador padrão no endereço http://localhost:8501.