import time

import streamlit as st
from load_data import load_data
from sidebar import Sidebar


@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode("utf-8")


def mensagem_sucesso():
    sucesso = st.success("Arquivo baixado com sucesso!", icon="✅")
    time.sleep(5)
    sucesso.empty()

def main():
    st.set_page_config(layout="wide")

    st.title("Análise de Preços do Supermercado Irmãos Gonçalves")
    slidbar = Sidebar()
    slidbar.city()

    dados = load_data(slidbar.city_id).dropna()

    dados = slidbar.create_product_filters_sidebar(dados, True).drop(columns=["ID do Produto"])

    page_size = 1000
    total_rows = dados.shape[0]
    total_pages = (total_rows // page_size) + 1
    page = st.number_input("Página", min_value=1, max_value=total_pages, value=1)
    start = (page - 1) * page_size
    end = start + page_size

    st.dataframe(dados.iloc[start:end])

    st.markdown(f"A tabela possui :blue[{dados.shape[0]:,}] linhas e :blue[{dados.shape[1]}] colunas")

    st.markdown("Escreva um nome para o arquivo")
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        nome_arquivo = st.text_input("Nome do arquivo", label_visibility="collapsed", value="dados")
        nome_arquivo += ".csv"
    with coluna2:
        st.download_button(
            "Fazer o download da tabela em csv",
            data=converte_csv(dados),
            file_name=nome_arquivo,
            mime="text/csv",
            on_click=mensagem_sucesso,
        )


if __name__ == "__main__":
    main()
