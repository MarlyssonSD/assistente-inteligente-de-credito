import csv, json, xml.etree.ElementTree as ET, pandas as pd
import Empresa as emp

def carregar_dados_csv(caminho_arquivo: str) -> list[emp.Empresa]:
    empresas = []
    with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        for linha in leitor:
            empresa = emp.Empresa(
                nome=linha["Empresa"],
                receita_anual=int(linha["Receita Anual"]),
                divida_total=int(linha["Dívida Total"]),
                prazo_pagamento=int(linha["Prazo de Pagamento (dias)"]),
                setor=linha["Setor"],
                rating=linha["Rating"],
                noticias_recentes=linha["Notícias Recentes"]
            )
            empresas.append(empresa)
    return empresas


def carregar_dados_json(caminho_arquivo: str) -> list[emp.Empresa]:
    empresas = []
    with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo_json:
        for linha_json in arquivo_json:
            dados = json.loads(linha_json)
            empresa = emp.Empresa(
                nome=dados["Empresa"],
                receita_anual=dados["Receita Anual"],
                divida_total=dados["Dívida Total"],
                prazo_pagamento=dados["Prazo de Pagamento (dias)"],
                setor=dados["Setor"],
                rating=dados["Rating"],
                noticias_recentes=dados["Notícias Recentes"]
            )
            empresas.append(empresa)
    return empresas


def carregar_dados_xml(caminho_arquivo: str) -> list[emp.Empresa]:
    empresas = []
    tree = ET.parse(caminho_arquivo)
    root = tree.getroot()
    
    for row in root.findall("row"):
        empresa = emp.Empresa(
            nome=row.find("Empresa").text,
            receita_anual=int(row.find("Receita_Anual").text),
            divida_total=int(row.find("Dívida_Total").text),
            prazo_pagamento=int(row.find("Prazo_de_Pagamento_dias").text),
            setor=row.find("Setor").text,
            rating=row.find("Rating").text,
            noticias_recentes=row.find("Notícias_Recentes").text
        )
        empresas.append(empresa)
    return empresas



def carregar_dados_parquet(caminho_arquivo: str) -> list[emp.Empresa]:
    empresas = []

    df = pd.read_parquet(caminho_arquivo, engine="pyarrow")  # ou engine="fastparquet"
    
    for _, linha in df.iterrows():
        empresa = emp.Empresa(
            nome=linha["Empresa"],
            receita_anual=int(linha["Receita Anual"]),
            divida_total=int(linha["Dívida Total"]),
            prazo_pagamento=int(linha["Prazo de Pagamento (dias)"]),
            setor=linha["Setor"],
            rating=linha["Rating"],
            noticias_recentes=linha["Notícias Recentes"]
        )
        empresas.append(empresa)
    return empresas

def carregar_dados_de_arquivo(caminho_do_arquivo: str) -> list[emp.Empresa]:
    """
    Carrega os dados de um arquivo, identificando seu formato pela extensão
    e chamando a função de carregamento apropriada.
    """
    if caminho_do_arquivo.lower().endswith('.csv'):
        print(f"INFO: Identificado arquivo CSV em '{caminho_do_arquivo}'. Chamando o leitor de CSV...")
        return carregar_dados_csv(caminho_do_arquivo)
    
    elif caminho_do_arquivo.lower().endswith('.json'):
        print(f"INFO: Identificado arquivo JSON em '{caminho_do_arquivo}'. Chamando o leitor de JSON...")
        return carregar_dados_json(caminho_do_arquivo)
    
    elif caminho_do_arquivo.lower().endswith('.xml'):
        print(f"INFO: Identificado arquivo XML em '{caminho_do_arquivo}'. Chamando o leitor de XML...")
        return carregar_dados_xml(caminho_do_arquivo)
        
    elif caminho_do_arquivo.lower().endswith('.parquet'):
        print(f"INFO: Identificado arquivo Parquet em '{caminho_do_arquivo}'. Chamando o leitor de Parquet...")
        return carregar_dados_parquet(caminho_do_arquivo)
        
    else:
        # Lança um erro se o formato não for suportado
        raise ValueError(f"ERRO: Formato de arquivo não suportado: {caminho_do_arquivo}")

# --- TESTANDO A FUNÇÃO DINÂMICA ---

# Defina a lista de arquivos que você quer testar
arquivos_para_testar = [
    'dados/dadoscreditoficticios.csv',
    'dados/dadoscreditoficticios.json',
    'dados/dadoscreditoficticios.xml',
    'dados/dadoscreditoficticios.parquet',
]

for arquivo in arquivos_para_testar:
    try:
        print(f"\n--- Tentando carregar o arquivo: {arquivo} ---")
        lista_de_empresas = carregar_dados_de_arquivo(arquivo)
        
        print(f"SUCESSO: Carregados {len(lista_de_empresas)} registros.")
        # Verificando se os dados estão corretos (opcional)
        if lista_de_empresas:
            print(f"Exemplo de registro: {lista_de_empresas[0].nome}")

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{arquivo}' não foi encontrado.")
    except ValueError as e:
        print(e) # Imprime a mensagem de erro da nossa função
    except Exception as e:
        print(f"ERRO inesperado ao processar '{arquivo}': {e}")