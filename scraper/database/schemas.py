from __future__ import annotations

from typing import NamedTuple


class PrecoInfo(NamedTuple):
    link: str
    preco: float


class PrecoVariavel(NamedTuple):
    link: str
    preco: float
    cidade: str


class DisponibilidadeInfo(NamedTuple):
    produto_link: str
    cidade: str


class ProdutoInfo(NamedTuple):
    nome: str
    link: str
    categoria: str | None


class DadosProcessados(NamedTuple):
    products: list[ProdutoInfo]
    uniform_prices: list[PrecoInfo]
    variable_prices: list[PrecoVariavel]
    availabilities: list[DisponibilidadeInfo]
