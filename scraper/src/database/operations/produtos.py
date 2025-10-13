import logging

from sqlalchemy import case
from utils.data import get_current_date

from database.connection import Session
from database.models import Produto

from .utils import gerenciador_transacao

logger = logging.getLogger(__name__)


@gerenciador_transacao
def save_product(session, produtos):
    """Salva ou atualiza produtos no banco."""
    if not produtos:
        logger.info("Nenhum produto válido para inserir.")
        return 0
    logger.info("Iniciando produtos")
    hoje = get_current_date()

    links_recebidos = {p.link for p in produtos}
    produtos_atuais = {p.link: p for p in session.query(Produto).filter(Produto.link.in_(links_recebidos)).all()}

    links_para_inserir = links_recebidos - produtos_atuais.keys()
    links_para_atualizar = links_recebidos.intersection(produtos_atuais.keys())

    produtos_para_inserir = []
    produtos_para_atualizar = []

    logger.info("loop produtos")
    for produto_info in produtos:
        if produto_info.link in links_para_inserir:
            produtos_para_inserir.append(
                Produto(
                    nome=produto_info.nome,
                    link=produto_info.link,
                    categoria=produto_info.categoria,
                    data_atualizacao=hoje,
                ),
            )
        elif produto_info.link in links_para_atualizar:
            atualizar = False
            produto_atual = produtos_atuais[produto_info.link]
            update_data = {"data_atualizacao": hoje}

            if produto_atual.nome != produto_info.nome:
                atualizar = True
                update_data["nome"] = produto_info.nome

            if produto_info.categoria and produto_atual.categoria != produto_info.categoria:
                atualizar = True

                update_data["categoria"] = produto_info.categoria

            if atualizar:
                update_data["id"] = produto_atual.id
                produtos_para_atualizar.append(update_data)

    logger.info("salvando produtos")
    if produtos_para_inserir:
        session.bulk_save_objects(produtos_para_inserir)
    if produtos_para_atualizar:
        BATCH_SIZE = 1000

        for i in range(0, len(produtos_para_atualizar), BATCH_SIZE):
            batch = produtos_para_atualizar[i : i + BATCH_SIZE]

            ids = [p["id"] for p in batch]

            nome_map = {p["id"]: p["nome"] for p in batch if "nome" in p}
            categoria_map = {p["id"]: p["categoria"] for p in batch if "categoria" in p}

            updates = {"data_atualizacao": hoje}

            if nome_map:
                updates["nome"] = case(nome_map, value=Produto.id, else_=Produto.nome)

            if categoria_map:
                updates["categoria"] = case(categoria_map, value=Produto.id, else_=Produto.categoria)

            session.query(Produto).filter(Produto.id.in_(ids)).update(updates, synchronize_session=False)

            session.flush()
            session.expunge_all()

    logger.info("commmit produtos")
    return len(produtos_para_inserir) + len(produtos_para_atualizar)


def get_link_produto():
    with Session() as session:
        return session.query(Produto).all()


def get_null_product_category():
    with Session() as session:
        return {produto.id for produto in session.query(Produto.id).filter(Produto.categoria.is_(None)).all()}


def update_categoria(dados):
    """Atualiza a categoria de múltiplos produtos no banco de dados.

    Args:
        dados: Lista de tuplas no formato (id_produto, categoria) contendo
              o ID do produto e sua nova categoria.

    """
    with Session() as session:
        for id_produto, categoria in dados:
            produto = session.query(Produto).filter(Produto.id == id_produto).first()
            produto.categoria = categoria

        session.commit()
        logger.info(f"{len(dados)} categorias de produtos atualizadas com sucesso.")


def get_produtos_sem_categoria(limite):
    with Session() as session:
        produtos = session.query(Produto.id, Produto.link).filter(Produto.categoria.is_(None)).limit(limite).all()
        return {produto.link: produto.id for produto in produtos}
