import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(
    os.environ["PROJECT_URL"],
    os.environ["API_KEY_PUBLIC"],
)

DB_URL = os.environ.get("DATABASE_URL")

st.set_page_config(layout="wide")

# Carregar dados
cidades_data = supabase.table("cidades").select("*").execute().data
# Barra de pesquisa para outra coisa
busca = st.text_input("Buscar por produto:")

# Selectbox para escolher cidade
nomes_cidades = [cidade["nome"] for cidade in cidades_data[1:-4]]
cidade_escolhida = st.selectbox("Escolha uma cidade:", nomes_cidades)

# Se quiser pegar o ID da cidade escolhida:
cidade_id = next((cidade["id"] for cidade in cidades_data if cidade["nome"] == cidade_escolhida), None)


@st.cache_data
def carregar_dados_cidade(cidade):
    historico_precos_df = """
    SELECT hp.*, p.nome, p.categoria as categoria_completa
    FROM HISTORICO_PRECOS hp
    JOIN PRODUTOS p ON p.id = hp.produto_id
    WHERE
    (
        hp.cidade_id = %s
        OR (
            hp.cidade_id = 1
            AND NOT EXISTS (
                SELECT 1
                FROM HISTORICO_PRECOS hp2
                WHERE
                    hp2.produto_id = hp.produto_id
                    AND hp2.cidade_id = %s
                    AND hp2.data_inicio = hp.data_inicio
                    AND hp2.data_fim = hp.data_fim
            )
            AND EXISTS (
                SELECT 1
                FROM DISPONIBILIDADE_CIDADES dc2
                WHERE
                    dc2.produto_id = hp.produto_id
                    AND dc2.cidade_id = %s
                    AND dc2.disponivel = TRUE
                    AND dc2.data_inicio <= hp.data_fim
                    AND dc2.data_fim >= hp.data_inicio
            )
        )
    )
    """
    df = pd.read_sql_query(historico_precos_df, DB_URL, params=(cidade, cidade, cidade))
    df["data_inicio"] = pd.to_datetime(df["data_inicio"]).dt.date
    df["data_fim"] = pd.to_datetime(df["data_fim"]).dt.date
    df["data_fim"] = df["data_fim"].fillna(pd.Timestamp.now().date)
    return df


# Função para filtrar categorias conforme seleção
def filtrar_categoria(cat):
    partes = cat.split("/")
    if grupo_escolhido and partes[0] != grupo_escolhido:
        return False
    if subgrupo_escolhido and len(partes) > 1 and partes[1] != subgrupo_escolhido:
        return False
    if item_escolhido and len(partes) > 2 and partes[2] != item_escolhido:
        return False
    return not (item_escolhido and len(partes) <= 2)


if cidade_id:
    dados = carregar_dados_cidade(cidade_id)[
        ["nome", "preco", "data_inicio", "data_fim", "categoria_completa"]
    ].dropna()
    if busca:
        dados = dados[dados["nome"].str.contains(busca, case=False, na=False)]

    # Extrair categorias do DataFrame filtrado
    categorias = dados["categoria_completa"].tolist()

    # Extrair níveis
    nivel1 = sorted({cat.split("/")[0] for cat in categorias})
    grupo_escolhido = st.selectbox("Grupo principal (opcional):", ["", *nivel1])

    if grupo_escolhido:
        nivel2 = sorted(
            {
                cat.split("/")[1]
                for cat in categorias
                if cat.startswith(grupo_escolhido + "/") and len(cat.split("/")) > 1
            },
        )
        subgrupo_escolhido = st.selectbox("Subgrupo (opcional):", ["", *nivel2])
    else:
        subgrupo_escolhido = ""

    if grupo_escolhido and subgrupo_escolhido:
        nivel3 = sorted(
            {
                cat.split("/")[2]
                for cat in categorias
                if cat.startswith(f"{grupo_escolhido}/{subgrupo_escolhido}") and len(cat.split("/")) > 2
            },
        )
        item_escolhido = st.selectbox("Item (opcional):", ["", *nivel3])
    else:
        item_escolhido = ""

    # Filtrar o DataFrame conforme seleção de categoria
    dados_filtrados = dados[dados["categoria_completa"].apply(filtrar_categoria)]

    st.dataframe(dados_filtrados)
