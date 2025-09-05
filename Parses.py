# Parses.py

"""
Módulo responsável pela ingestão e parsing de dados de empresas de diferentes formatos.
Converte os dados brutos de arquivos CSV, JSON, XML e Parquet em uma lista padronizada
de objetos Empresa.
"""

import csv
import json
import xml.etree.ElementTree as ET
import pandas as pd
import logging
from typing import List
import Empresa as emp  # Certifique-se que o arquivo Empresa.py está no mesmo diretório

# Configuração de logging para registrar erros durante o parsing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def carregar_dados_csv(caminho_arquivo: str) -> List[emp.Empresa]:
    """
    Carrega dados de um arquivo CSV e converte para uma lista de objetos Empresa.

    Args:
        caminho_arquivo (str): O caminho completo para o arquivo .csv.

    Returns:
        List[emp.Empresa]: Uma lista de instâncias da classe Empresa.
    """
    empresas = []
    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo_csv:
            leitor = csv.DictReader(arquivo_csv)
            for i, linha in enumerate(leitor):
                try:
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
                except ValueError as e:
                    logging.warning(f"Erro ao processar linha {i+1} do CSV: {e}. Linha ignorada: {linha}")
                except KeyError as e:
                    logging.warning(f"Coluna esperada não encontrada na linha {i+1} do CSV: {e}. Linha ignorada.")

    except FileNotFoundError:
        logging.error(f"Arquivo CSV não encontrado em: {caminho_arquivo}")
        raise
    return empresas


def carregar_dados_json(caminho_arquivo: str) -> List[emp.Empresa]:
    """
    Carrega dados de um arquivo JSON (JSON Lines) e converte para uma lista de objetos Empresa.

    Args:
        caminho_arquivo (str): O caminho completo para o arquivo .json.

    Returns:
        List[emp.Empresa]: Uma lista de instâncias da classe Empresa.
    """
    empresas = []
    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo_json:
            for i, linha_json in enumerate(arquivo_json):
                try:
                    dados = json.loads(linha_json)
                    empresa = emp.Empresa(
                        nome=dados["Empresa"],
                        receita_anual=int(dados["Receita Anual"]),
                        divida_total=int(dados["Dívida Total"]),
                        prazo_pagamento=int(dados["Prazo de Pagamento (dias)"]),
                        setor=dados["Setor"],
                        rating=dados["Rating"],
                        noticias_recentes=dados["Notícias Recentes"]
                    )
                    empresas.append(empresa)
                except ValueError as e:
                    logging.warning(f"Erro de conversão de tipo na linha {i+1} do JSON: {e}. Linha ignorada: {dados}")
                except KeyError as e:
                    logging.warning(f"Chave esperada não encontrada na linha {i+1} do JSON: {e}. Linha ignorada.")

    except FileNotFoundError:
        logging.error(f"Arquivo JSON não encontrado em: {caminho_arquivo}")
        raise
    return empresas


def carregar_dados_xml(caminho_arquivo: str) -> List[emp.Empresa]:
    """
    Carrega dados de um arquivo XML e converte para uma lista de objetos Empresa.

    Args:
        caminho_arquivo (str): O caminho completo para o arquivo .xml.

    Returns:
        List[emp.Empresa]: Uma lista de instâncias da classe Empresa.
    """
    empresas = []
    try:
        tree = ET.parse(caminho_arquivo)
        root = tree.getroot()
        
        for i, row in enumerate(root.findall("row")):
            try:
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
            except (ValueError, AttributeError) as e:
                logging.warning(f"Erro ao processar nó XML {i+1}: {e}. Nó ignorado.")

    except ET.ParseError:
        logging.error(f"Erro ao fazer o parse do arquivo XML: {caminho_arquivo}")
        raise
    except FileNotFoundError:
        logging.error(f"Arquivo XML não encontrado em: {caminho_arquivo}")
        raise
    return empresas


def carregar_dados_parquet(caminho_arquivo: str) -> List[emp.Empresa]:
    """
    Carrega dados de um arquivo Parquet e converte para uma lista de objetos Empresa.

    Args:
        caminho_arquivo (str): O caminho completo para o arquivo .parquet.

    Returns:
        List[emp.Empresa]: Uma lista de instâncias da classe Empresa.
    """
    empresas = []
    try:
        df = pd.read_parquet(caminho_arquivo)
        for i, linha in df.iterrows():
            try:
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
            except (ValueError, TypeError) as e:
                logging.warning(f"Erro de conversão de tipo na linha {i} do Parquet: {e}. Linha ignorada.")
            except KeyError as e:
                logging.warning(f"Coluna esperada não encontrada no Parquet: {e}.")

    except FileNotFoundError:
        logging.error(f"Arquivo Parquet não encontrado em: {caminho_arquivo}")
        raise
    return empresas


def carregar_dados_de_arquivo(caminho_do_arquivo: str, debug: bool = False) -> List[emp.Empresa]:
    """
    Função despachante que identifica o formato do arquivo pela extensão
    e chama o parser apropriado.

    Args:
        caminho_do_arquivo (str): O caminho para o arquivo de dados.
        debug (bool, optional): Se True, imprime logs de informação. Default é False.

    Raises:
        ValueError: Se a extensão do arquivo não for suportada (.csv, .json, .xml, .parquet).

    Returns:
        List[emp.Empresa]: A lista de empresas carregada do arquivo.
    """
    extensao = caminho_do_arquivo.lower().split('.')[-1]
    if debug:
        logging.info(f"Tentando carregar arquivo: {caminho_do_arquivo} (Extensão detectada: {extensao})")

    if extensao == 'csv':
        return carregar_dados_csv(caminho_do_arquivo)
    elif extensao == 'json':
        return carregar_dados_json(caminho_do_arquivo)
    elif extensao == 'xml':
        return carregar_dados_xml(caminho_do_arquivo)
    elif extensao == 'parquet':
        return carregar_dados_parquet(caminho_do_arquivo)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {extensao}")


# Bloco de execução principal para testes locais
if __name__ == "__main__":
    logging.info("Iniciando testes de carregamento de dados...")
    
    arquivos_para_testar = [
        'dados/dadoscreditoficticios.csv',
        'dados/dadoscreditoficticios.json',
        'dados/dadoscreditoficticios.xml',
        'dados/dadoscreditoficticios.parquet',
    ]

    for arquivo in arquivos_para_testar:
        try:
            logging.info(f"--- Testando carregamento de: {arquivo} ---")
            lista_de_empresas = carregar_dados_de_arquivo(arquivo)
            if lista_de_empresas:
                logging.info(f"SUCESSO: Carregados {len(lista_de_empresas)} registros.")
                logging.info(f"Exemplo de registro (primeira empresa): {lista_de_empresas[0].nome}")
            else:
                logging.warning(f"AVISO: Nenhum dado carregado de {arquivo}.")

        except Exception as e:
            logging.error(f"FALHA AO PROCESSAR {arquivo}: {e}")