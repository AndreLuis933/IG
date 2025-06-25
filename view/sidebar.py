from datetime import timedelta

import streamlit as st
from load_data import load_city


class Sidebar:
    def __init__(self):
        self.city_id = 1

    def build(self):
        cidades_data = load_city()
        nomes_cidades = [cidade["nome"] for cidade in cidades_data[1:-4]]
        with st.sidebar:
            cidade_escolhida = st.selectbox("Selecione a cidade", nomes_cidades)

        self.city_id = next((cidade["id"] for cidade in cidades_data if cidade["nome"] == cidade_escolhida), None)

    def date(self, data_inicial, data_final):
        with st.sidebar:
            st.subheader("Filtro por Data")
            return st.sidebar.slider(
                "Selecione o período",
                min_value=data_inicial,
                max_value=data_final,
                value=(data_inicial, data_final),
                step=timedelta(days=1),
            )
    def category(self):
        with st.sidebar:
            st.subheader("Filtro por Categoria")
