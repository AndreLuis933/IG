import os
from datetime import date, datetime

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
    df["data_fim"] = df["data_fim"].fillna(pd.Timestamp.now().date())
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


def filtrar_por_data(df, data_inicio_filtro, data_fim_filtro):
    """Filtra o DataFrame baseado no intervalo de datas.
    Considera registros que tenham sobreposição com o período selecionado.
    """
    if data_inicio_filtro and data_fim_filtro:
        # Filtrar registros que tenham sobreposição com o período selecionado
        mask = (df["data_inicio"] <= data_fim_filtro) & (df["data_fim"] >= data_inicio_filtro)
        return df[mask]
    return df


if cidade_id:
    dados = (
        carregar_dados_cidade(cidade_id)[["nome", "preco", "data_inicio", "data_fim", "categoria_completa"]]
        .dropna()
        .sort_values(["data_inicio", "data_fim"], ascending=[True, False])
    )

    st.subheader("Filtro por Data")
    col1, col2 = st.columns(2)

    with col1:
        data_inicio_filtro = st.date_input(
            "Data de início:",
            value=None,  # Sem valor padrão
            help="Selecione a data de início do período (opcional)",
            format="DD/MM/YYYY",
        )

    with col2:
        data_fim_filtro = st.date_input(
            "Data de fim:",
            value=None,  # Sem valor padrão
            help="Selecione a data de fim do período (opcional)",
            format="DD/MM/YYYY",
        )

    # Aplicar filtro de data apenas se ambas as datas forem preenchidas
    if data_inicio_filtro and data_fim_filtro:
        if data_inicio_filtro > data_fim_filtro:
            st.error("A data de início deve ser anterior à data de fim!")
        else:
            dados = filtrar_por_data(dados, data_inicio_filtro, data_fim_filtro)
            st.info(f"Mostrando dados de {data_inicio_filtro} até {data_fim_filtro}")

    categorias = dados["categoria_completa"].tolist()
    nomes = dados["nome"].tolist()
    nivel1 = sorted({cat.split("/")[0] for cat in categorias})

    # Escolher tipo de filtro
    tipo_filtro = st.radio("Escolha o tipo de busca:", ["Busca livre", "Seleção da lista"])
    grupo_escolhido = ""
    if tipo_filtro == "Busca livre":
        busca = st.text_input("Buscar por produto:")
        if busca:
            dados = dados[dados["nome"].str.contains(busca, case=False, na=False)]
        grupo_escolhido = st.selectbox("Categoria principal:", ["", *nivel1])
    else:
        busca_nome = st.selectbox("Escolha um produto:", nomes)
        if busca_nome:
            dados = dados[dados["nome"] == busca_nome]  # Filtro exato para selectbox

    # Extrair níveis

    if grupo_escolhido:
        nivel2 = sorted(
            {
                cat.split("/")[1]
                for cat in categorias
                if cat.startswith(grupo_escolhido + "/") and len(cat.split("/")) > 1
            },
        )
        subgrupo_escolhido = st.selectbox("Categoria secundária:", ["", *nivel2])
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
        item_escolhido = st.selectbox("Categoria terciária:", ["", *nivel3])
    else:
        item_escolhido = ""

    # Filtrar o DataFrame conforme seleção de categoria
    dados_filtrados = dados[dados["categoria_completa"].apply(filtrar_categoria)]

    st.dataframe(dados_filtrados)
