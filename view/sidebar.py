from datetime import timedelta

import streamlit as st
from load_data import load_city
from utils import criar_mascara_categorias, extrair_niveis_categorias


class Sidebar:
    def __init__(self):
        self.city_id = 1
        self.grupo1 = None
        self.grupo2 = None
        self.grupo3 = None

    def city(self):
        cidades_data = load_city()
        nomes_cidades = [cidade["nome"] for cidade in cidades_data[1:-4]]
        with st.sidebar:
            cidade_escolhida = st.selectbox("Selecione a cidade", nomes_cidades)

        self.city_id = next((cidade["id"] for cidade in cidades_data if cidade["nome"] == cidade_escolhida), None)

    def create_product_filters_sidebar(self, df, columns=None):
        filter_config = self._get_filter_ranges(df)

        st.sidebar.title("Filtros")
        self._create_reset_button(filter_config)
        selected_columns = self._create_column_selector(df) if columns else df.columns
        filtered_df = self._apply_all_filters(df, filter_config)

        if filtered_df.empty:
            return None

        return filtered_df[selected_columns]

    def _get_filter_ranges(self, df):
        return {
            "price_range": (df["Preço"].min(), df["Preço"].max()),
            "date_range": (df["Data"].min(), df["Data"].max()),
            "product_names": df["Nome do Produto"].sort_values().unique(),
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
        df = self._apply_product_name_filter(df)
        df = self._apply_price_filter(df, filter_config["price_range"])
        df = self._apply_date_filter(df, filter_config["date_range"])
        return self._apply_category_filter(df)

    def _apply_product_name_filter(self, df):
        with st.sidebar.expander("Nome do produto"):
            search_term = st.text_input("Buscar por produto:", key="search")
            if search_term:
                df = df[df["Nome do Produto"].str.contains(search_term, case=False, na=False)]

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
        return df[(df["Preço"] >= selected_price_range[0]) & (df["Preço"] <= selected_price_range[1])]

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
        return df[(df["Data"] <= selected_date_range[1]) & (df["Data"] >= selected_date_range[0])]

    def _apply_category_filter(self, df):
        with st.sidebar.expander("Categoria"):
            nivel1, _, _ = extrair_niveis_categorias(df)
            grupo_escolhido = st.selectbox("Categoria principal:", ["", *nivel1], key="category")

            subgrupo_escolhido = ""
            item_escolhido = ""
            if grupo_escolhido:
                _, nivel2, _ = extrair_niveis_categorias(df, grupo_escolhido)
                subgrupo_escolhido = st.selectbox("Categoria secundária:", ["", *nivel2])
                if subgrupo_escolhido:
                    _, _, nivel3 = extrair_niveis_categorias(df, grupo_escolhido, subgrupo_escolhido)
                    item_escolhido = st.selectbox("Categoria terciária:", ["", *nivel3])

            self.grupo1 = grupo_escolhido
            self.grupo2 = subgrupo_escolhido
            self.grupo3 = item_escolhido

            if not df.empty:
                mask = criar_mascara_categorias(df, grupo_escolhido, subgrupo_escolhido, item_escolhido)
                return df[mask]
            return df
