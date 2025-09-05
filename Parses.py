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





dados_carregados = carregar_dados_csv('dados/dadoscreditoficticios.csv')
print(dados_carregados[1].nome)
print(f"Total de registros carregados: {len(dados_carregados)}")

dados_carregados = carregar_dados_json('dados/dadoscreditoficticios.json')
print(dados_carregados[1].nome)
print(f"Total de registros carregados: {len(dados_carregados)}")

dados_carregados = carregar_dados_xml('dados/dadoscreditoficticios.xml')
print(dados_carregados[1].nome)
print(f"Total de registros carregados: {len(dados_carregados)}")

dados_carregados = carregar_dados_parquet("dados/dadoscreditoficticios.parquet")
print(dados_carregados[1].nome)
print(f"Total de registros carregados: {len(dados_carregados)}")