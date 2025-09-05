from dataclasses import dataclass

@dataclass
class Empresa:
    nome: str
    receita_anual: int
    divida_total: int
    prazo_pagamento: int
    setor: str
    rating: str
    noticias_recentes: str