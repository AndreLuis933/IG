import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")
supabase = create_client(
    os.environ["PROJECT_URL"],
    os.environ["API_KEY_PUBLIC"],
)


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


def load_city():
    return supabase.table("cidades").select("*").execute().data
