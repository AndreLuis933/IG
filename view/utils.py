import pandas as pd
import requests

def criar_mascara_categorias(dados, grupo_escolhido="", subgrupo_escolhido="", item_escolhido=""):
    categorias_split = dados["Categoria"].str.split("/", expand=True)
    mask = pd.Series([True] * len(dados), index=dados.index)
    if grupo_escolhido:
        mask &= categorias_split[0] == grupo_escolhido
    if subgrupo_escolhido:
        mask &= categorias_split[1] == subgrupo_escolhido
    if item_escolhido:
        mask &= categorias_split[2] == item_escolhido
        mask &= categorias_split[2].notna()
    return mask


def extrair_niveis_categorias(dados, grupo_escolhido="", subgrupo_escolhido=""):
    """Extrai os níveis de categoria baseado na seleção atual."""
    categorias = dados["Categoria"].tolist()
    nivel1 = sorted({cat.split("/")[0] for cat in categorias})

    if grupo_escolhido:
        nivel2 = sorted(
            {
                cat.split("/")[1]
                for cat in categorias
                if cat.startswith(grupo_escolhido + "/") and len(cat.split("/")) > 1
            },
        )
    else:
        nivel2 = []

    if grupo_escolhido and subgrupo_escolhido:
        nivel3 = sorted(
            {
                cat.split("/")[2]
                for cat in categorias
                if cat.startswith(f"{grupo_escolhido}/{subgrupo_escolhido}") and len(cat.split("/")) > 2
            },
        )
    else:
        nivel3 = []

    return nivel1, nivel2, nivel3

def verificar_url_imagem(url):
    """Verifica se a URL da imagem existe."""
    try:
        response = requests.head(url, timeout=5)
    except requests.exceptions.RequestException:
        return False
    else:
        return response.status_code == 200
