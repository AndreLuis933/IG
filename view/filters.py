import streamlit as st
from utils import criar_mascara_categorias, extrair_niveis_categorias


def filtrar_por_data(df, data_inicio_filtro, data_fim_filtro):
    """Filtra o DataFrame baseado no intervalo de datas.
    Considera registros que tenham sobreposição com o período selecionado.
    """
    if data_inicio_filtro and data_fim_filtro:
        mask = (df["data_inicio"] <= data_fim_filtro) & (df["data_fim"] >= data_inicio_filtro)
        return df[mask]
    return df


def categoria_filtro(dados):
    nomes = dados["nome"].sort_values(ascending=True).drop_duplicates().tolist()
    nivel1, _, _ = extrair_niveis_categorias(dados)

    aba1, aba2 = st.tabs(["Busca livre", "Seleção da lista"])

    with aba1:
        busca = st.text_input("Buscar por produto:")
        grupo_escolhido = st.selectbox("Categoria principal:", ["", *nivel1])
        dados_filtrados = dados.copy()
        if busca:
            dados_filtrados = dados_filtrados[dados_filtrados["nome"].str.contains(busca, case=False, na=False)]

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
            resultado = dados_filtrados[mask][["nome", "preco", "data_inicio", "data_fim", "categoria_completa"]]

        st.dataframe(resultado)

    with aba2:
        busca_nome = st.selectbox("Escolha um produto:", nomes)
        dados_filtrados = dados.copy()
        if busca_nome:
            dados_filtrados = dados_filtrados[dados_filtrados["nome"] == busca_nome]

        st.dataframe(dados_filtrados[["nome", "preco", "data_inicio", "data_fim", "categoria_completa"]])
