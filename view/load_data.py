import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")
LOCAL = os.getenv("LOCAL", "false").lower() == "true"
supabase = create_client(os.environ["PROJECT_URL"], os.environ["API_KEY_SECRET"]) if not LOCAL else None


@st.cache_data
def load_data(cidade):
    historico_precos_df = """
    SELECT
    p.id AS "ID do Produto",
    p.nome AS "Nome do Produto",
    hp.preco AS "Preço",
    hp.data_inicio,
    hp.data_fim,
    p.categoria AS "Categoria"
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
                    AND COALESCE(hp2.data_fim, CURRENT_DATE) = COALESCE(hp.data_fim, CURRENT_DATE)
            )
            AND EXISTS (
                SELECT 1
                FROM DISPONIBILIDADE_CIDADES dc2
                WHERE
                    dc2.produto_id = hp.produto_id
                    AND dc2.cidade_id = %s
                    AND dc2.disponivel = TRUE
                    AND dc2.data_inicio <= COALESCE(hp.data_fim, CURRENT_DATE)
                    AND COALESCE(dc2.data_fim, CURRENT_DATE) >= hp.data_inicio
            )
        )
    )
    """
    df = pd.read_sql_query(historico_precos_df, DB_URL, params=(cidade, cidade, cidade))
    df["data_inicio"] = pd.to_datetime(df["data_inicio"]).dt.date
    df["data_fim"] = pd.to_datetime(df["data_fim"]).dt.date
    df["data_fim"] = df["data_fim"].fillna(pd.Timestamp.now().date())

    df["Data"] = df.apply(lambda row: pd.date_range(row["data_inicio"], row["data_fim"]).tolist(), axis=1)

    df = df.explode("Data").reset_index(drop=True)
    df["Data"] = pd.to_datetime(df["Data"]).dt.date
    return df.drop(["data_inicio", "data_fim"], axis=1)


def load_city():
    return (
        supabase.table("cidades").select("*").execute().data
        if supabase
        else pd.read_sql_query("SELECT * FROM cidades;", DB_URL).to_dict(orient="records")
    )
