import plotly.express as px
import streamlit as st
from load_data import load_data
from sidebar import Sidebar
from utils import verificar_url_imagem


def main():
    st.set_page_config(layout="wide")

    st.title("Análise de Preços do Supermercado Irmãos Gonçalves")
    slidbar = Sidebar()
    slidbar.city()

    tab1, tab2, tab3 = st.tabs(["Todos os Produtos", "Produto Especifico", "Categorias"])

    dados = load_data(slidbar.city_id).dropna()

    tabela = slidbar.create_product_filters_sidebar(dados)
    with tab1:
        if tabela is not None:
            df_total_diario = tabela.groupby("Data")["Preço"].mean().reset_index()
            fig_receita_mensal = px.line(df_total_diario, x="Data", y="Preço", title="Media dos Preços")
            st.plotly_chart(fig_receita_mensal, use_container_width=True)

    with tab2:
        selected_product = st.selectbox("Escolha um produto:", dados["Nome do Produto"].sort_values().unique())
        col1, col2 = st.columns(2)

        produtos = dados[dados["Nome do Produto"] == selected_product].sort_values("Data")
        id_produto = produtos["ID do Produto"].iloc[0]

        fig_receita_mensal = px.line(produtos, x="Data", y="Preço", title="Preços")

        url = f"https://xzipxocmqgjtvfbuxafi.supabase.co/storage/v1/object/public/images//{id_produto}.jpg"
        largura_max = 400
        altura_max = 300

        with col1:
            if verificar_url_imagem(url):
                st.markdown(
                    f'<img src="{url}" style="max-width:{largura_max}px; max-height:{altura_max}px; object-fit: contain; display: block; margin-bottom: 20px;">',
                    unsafe_allow_html=True,
                )
            else:
                st.warning("Não foi possível carregar a imagem")
        with col2:
            st.plotly_chart(fig_receita_mensal, use_container_width=True)

    with tab3:
        if not slidbar.grupo1:
            tabela["Categoria"] = tabela["Categoria"].str.split("/").str[0]
        elif not slidbar.grupo2:
            tabela["Categoria"] = tabela["Categoria"].str.split("/").str[1]
        elif not slidbar.grupo3:
            tabela["Categoria"] = tabela["Categoria"].str.split("/").str[2]
        else:
            tabela["Categoria"] = tabela["Nome do Produto"]

        df_total_diario = tabela.groupby(["Categoria", "Data"])["Preço"].mean().reset_index()
        fig = px.line(
            df_total_diario,
            x="Data",
            y="Preço",
            color="Categoria",
            title="Media dos Preços por categoria",
        )
        # for trace in fig.data:
        #     if trace.name == "magazine":
        #         trace.visible = "legendonly"
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
