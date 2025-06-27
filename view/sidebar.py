from datetime import timedelta

import streamlit as st
from load_data import load_city
from utils import criar_mascara_categorias, extrair_niveis_categorias


class Sidebar:
    def __init__(self):
        self.city_id = 1

    def city(self):
        cidades_data = load_city()
        nomes_cidades = [cidade["nome"] for cidade in cidades_data[1:-4]]
        with st.sidebar:
            cidade_escolhida = st.selectbox("Selecione a cidade", nomes_cidades)

        self.city_id = next((cidade["id"] for cidade in cidades_data if cidade["nome"] == cidade_escolhida), None)

    def create_product_filters_sidebar(self, df):
        filtered_df = self._prepare_dataframe(df)
        filter_config = self._get_filter_ranges(filtered_df)

        st.sidebar.title("Filtros")
        self._create_reset_button(filter_config)
        selected_columns = self._create_column_selector(filtered_df)
        filtered_df = self._apply_all_filters(filtered_df, filter_config)

        if filtered_df.empty:
            return None

        return self._format_output_dataframe(filtered_df, selected_columns)


    def _prepare_dataframe(self, df):
        required_columns = ["nome", "preco", "data_inicio", "data_fim", "categoria_completa"]
        return df[required_columns].copy()


    def _get_filter_ranges(self, df):
        return {
            "price_range": (df["preco"].min(), df["preco"].max()),
            "date_range": (df["data_inicio"].min(), df["data_fim"].max()),
            "product_names": df["nome"].sort_values().unique(),
        }


    def _create_reset_button(self, filter_config):
        product_names = filter_config["product_names"]
        min_price, max_price = filter_config["price_range"]
        start_date, end_date = filter_config["date_range"]

        if st.sidebar.button("Resetar filtros"):
            st.session_state["search"] = ""
            st.session_state["filter_type"] = "Busca livre"
            st.session_state["products"] = product_names[0] if len(product_names) > 0 else ""
            st.session_state["price"] = (min_price, max_price)
            st.session_state["date_range"] = (start_date, end_date)
            st.session_state["category"] = ""


    def _create_column_selector(self, df):
        with st.expander("Colunas"):
            return st.multiselect("Selecione as colunas", list(df.columns), list(df.columns))


    def _apply_all_filters(self, df, filter_config):
        df = self._apply_product_name_filter(df, filter_config["product_names"])
        df = self._apply_price_filter(df, filter_config["price_range"])
        df = self._apply_date_filter(df, filter_config["date_range"])
        return self._apply_category_filter(df)


    def _apply_product_name_filter(self, df, product_names):
        with st.sidebar.expander("Nome do produto"):
            search_type = st.radio("Escolha o tipo de busca:", ["Busca livre", "Seleção da lista"], key="filter_type")
            if search_type == "Busca livre":
                search_term = st.text_input("Buscar por produto:", key="search")
                if search_term:
                    df = df[df["nome"].str.contains(search_term, case=False, na=False)]
            else:
                selected_product = st.selectbox("Escolha um produto:", product_names, key="products")
                if selected_product:
                    df = df[df["nome"] == selected_product]
        return df


    def _apply_price_filter(self, df, price_range):
        min_price, max_price = price_range
        with st.sidebar.expander("Preço"):
            selected_price_range = st.slider(
                "Selecione o preço",
                min_price,
                max_price,
                value=(min_price, max_price),
                key="price",
            )
        return df[(df["preco"] >= selected_price_range[0]) & (df["preco"] <= selected_price_range[1])]


    def _apply_date_filter(self, df, date_range):
        start_date, end_date = date_range
        with st.sidebar.expander("Data"):
            selected_date_range = st.slider(
                "Selecione o período",
                min_value=start_date,
                max_value=end_date,
                value=(start_date, end_date),
                step=timedelta(days=1),
                format="DD/MM/YYYY",
                key="date_range",
            )
        return df[(df["data_inicio"] <= selected_date_range[1]) & (df["data_fim"] >= selected_date_range[0])]


    def _apply_category_filter(self, df):
        with st.sidebar.expander("Categoria"):
            nivel1, _, _ = extrair_niveis_categorias(df)
            grupo_escolhido = st.selectbox("Categoria principal:", ["", *nivel1], key="category")
            dados_filtrados = df.copy()

            subgrupo_escolhido = ""
            item_escolhido = ""
            if grupo_escolhido:
                _, nivel2, _ = extrair_niveis_categorias(dados_filtrados, grupo_escolhido)
                subgrupo_escolhido = st.selectbox("Categoria secundária:", ["", *nivel2])
                if subgrupo_escolhido:
                    _, _, nivel3 = extrair_niveis_categorias(dados_filtrados, grupo_escolhido, subgrupo_escolhido)
                    item_escolhido = st.selectbox("Categoria terciária:", ["", *nivel3])

            if not dados_filtrados.empty:
                mask = criar_mascara_categorias(dados_filtrados, grupo_escolhido, subgrupo_escolhido, item_escolhido)
                return dados_filtrados[mask]
            return dados_filtrados


    def _format_output_dataframe(self, df, selected_columns):
        column_mapping = {
            "nome": "Nome do Produto",
            "preco": "Preço",
            "data_inicio": "Início",
            "data_fim": "Fim",
            "categoria_completa": "Categoria",
        }
        return df[selected_columns].rename(columns=column_mapping)
