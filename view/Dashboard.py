import plotly.express as px
import streamlit as st
from load_data import carregar_dados_cidade
from sidebar import Sidebar


def main():
    st.set_page_config(layout="wide")

    st.title("Análise de Preços do Supermercado Irmãos Gonçalves")
    slidbar = Sidebar()
    slidbar.city()

    dados = carregar_dados_cidade(slidbar.city_id).dropna()

    dados = slidbar.create_product_filters_sidebar(dados)

    if dados is not None:
        df_total_diario = dados.groupby("Data")["Preço"].sum().reset_index()
        fig_receita_mensal = px.line(df_total_diario, x="Data", y="Preço", title="Soma dos Preços por Dia")
        st.plotly_chart(fig_receita_mensal, use_container_width=True)


if __name__ == "__main__":
    main()
