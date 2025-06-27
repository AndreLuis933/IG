import streamlit as st
from load_data import carregar_dados_cidade
from sidebar import Sidebar


def main():
    st.set_page_config(layout="wide")

    st.title("Análise de Preços do Supermercado Irmãos Gonçalves")
    slidbar = Sidebar()
    slidbar.city()

    dados = carregar_dados_cidade(slidbar.city_id)
    dados = dados.dropna().sort_values(["data_inicio", "data_fim"], ascending=[True, False])

    dados = slidbar.create_product_filters_sidebar(dados)
    st.dataframe(dados)


if __name__ == "__main__":
    main()
