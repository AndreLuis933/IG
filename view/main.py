import streamlit as st
from filters import categoria_filtro, filtrar_por_data
from load_data import carregar_dados_cidade
from sidebar import Sidebar


def main():
    st.set_page_config(layout="wide")

    st.title("Análise de Preços do Supermercado Irmãos Gonçalves")
    slidbar = Sidebar()
    slidbar.build()

    dados = carregar_dados_cidade(slidbar.city_id)
    dados = dados.dropna().sort_values(["data_inicio", "data_fim"], ascending=[True, False])

    data_inicial = dados["data_inicio"].min()
    data_final = dados["data_fim"].max()
    intervalo = slidbar.date(data_inicial, data_final)

    dados = filtrar_por_data(dados, intervalo[0], intervalo[1])

    categoria_filtro(dados)


if __name__ == "__main__":
    main()
