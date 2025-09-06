# test_app.py

import pytest
from fastapi.testclient import TestClient
import httpx

# --- Importação dos módulos que vamos testar ---
# Importa o app FastAPI do seu arquivo main.py
from main import app, get_lista_empresas
# Importa as funções de parsing do seu arquivo Parses.py
import Parses
# Importa a classe de dados Empresa
from Empresa import Empresa

# --- Configuração do Cliente de Teste para a API ---

# Fixture do Pytest para criar um cliente de teste para a API.
# Isso nos permite simular requisições HTTP sem precisar rodar o servidor real.
@pytest.fixture(scope="module")
def client():
    # Antes de criar o cliente, precisamos garantir que a API não tente ler
    # os arquivos reais do disco durante os testes. Vamos sobrescrever a dependência.
    
    # 1. Criar dados mockados para os testes da API
    mock_data = [
        Empresa(nome="Empresa Teste Sucesso", receita_anual=100000, divida_total=5000, 
                prazo_pagamento=30, setor="Tecnologia", rating="A", noticias_recentes="Tudo certo."),
        Empresa(nome="Empresa Teste Risco", receita_anual=50000, divida_total=40000, 
                prazo_pagamento=90, setor="Varejo", rating="C", noticias_recentes="Risco detectado.")
    ]

    # 2. Criar a função de override que retorna os dados mockados em vez de ler do arquivo
    def override_get_lista_empresas():
        return mock_data

    # 3. Aplicar o override na aplicação FastAPI
    # Isso substitui a função original get_lista_empresas pela nossa mock_data durante os testes.
    app.dependency_overrides[get_lista_empresas] = override_get_lista_empresas
    
    # 4. Criar e retornar o cliente de teste
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpeza: remove o override depois que os testes terminam
    app.dependency_overrides.clear()


# --- Bloco 1: Testes Unitários dos Parsers ---

# Fixture para criar um arquivo CSV temporário para os testes de parsing
@pytest.fixture
def mock_csv_file(tmp_path):
    # tmp_path é uma fixture mágica do pytest que cria um diretório temporário
    file_path = tmp_path / "test_data.csv"
    content = (
        "Empresa,Receita Anual,Dívida Total,Prazo de Pagamento (dias),Setor,Rating,Notícias Recentes\n"
        "Empresa CSV 1,100000,50000,30,Tecnologia,A,Noticia boa\n"
        "Empresa CSV 2,200000,150000,60,Saude,B,Noticia ruim\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

def test_carregar_dados_csv_sucesso(mock_csv_file):
    """
    Testa se a função carregar_dados_csv processa corretamente um arquivo válido.
    Verifica se a quantidade de registros lidos está correta e se os dados da primeira
    empresa correspondem ao esperado.
    """
    # Arrange: mock_csv_file é criado pela fixture

    # Act: Executa a função de carregamento
    empresas = Parses.carregar_dados_csv(mock_csv_file)

    # Assert: Verifica os resultados
    assert len(empresas) == 2
    assert empresas[0].nome == "Empresa CSV 1"
    assert empresas[0].receita_anual == 100000
    assert empresas[1].setor == "Saude"

def test_carregar_dados_arquivo_inexistente():
    """
    Testa se a função de carregamento principal levanta a exceção correta (FileNotFoundError)
    quando um arquivo que não existe é passado como parâmetro.
    """
    # Arrange: Define um caminho de arquivo заведомо inexistente
    caminho_falso = "caminho/que/nao/existe/fakefile.csv"

    # Act & Assert: Verifica se a exceção FileNotFoundError é levantada
    with pytest.raises(FileNotFoundError):
        Parses.carregar_dados_de_arquivo(caminho_falso)

# --- Bloco 2: Testes de Integração da API ---

def test_endpoint_get_empresa_details_sucesso(client: TestClient):
    # Arrange: mocka a lista de empresas diretamente no estado do app
    client.app.state.lista_empresas = [
        Empresa(
            nome="Empresa Teste Sucesso",
            receita_anual=100000,
            divida_total=5000,
            prazo_pagamento=30,
            setor="Tecnologia",
            rating="A",
            noticias_recentes="Tudo certo."
        )
    ]
    nome_empresa_existente = "Empresa Teste Sucesso"
    
    # Act: faz a requisição HTTP GET
    response = client.get(f"/empresa/{nome_empresa_existente}")
    
    # Assert: verifica o status code e o conteúdo da resposta
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == nome_empresa_existente
    assert data["rating"] == "A"


def test_endpoint_get_empresa_details_nao_encontrado(client: TestClient):
    """
    Testa o endpoint GET /empresa/{nome_empresa} para um caso de falha (empresa inexistente).
    Verifica se o status code é 404 (Not Found).
    """
    # Arrange: Um nome de empresa que não existe no mock_data
    nome_empresa_inexistente = "Empresa Fantasma"
    
    # Act: Faz a requisição HTTP GET
    response = client.get(f"/empresa/{nome_empresa_inexistente}")
    
    # Assert: Verifica o status code
    assert response.status_code == 404