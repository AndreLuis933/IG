import logging
from datetime import timedelta
from functools import wraps

import sqlalchemy
from sqlalchemy import desc, tuple_

from database.connection import Session
from database.models import LogExecucao
from utils.data import get_current_date

logger = logging.getLogger(__name__)


def gerenciador_transacao(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with Session() as session:
                result = func(session, *args, **kwargs)
                session.commit()
                return result
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            logger.exception(f"Erro de integridade ao executar {func.__name__}: ")
            return None
        except sqlalchemy.exc.SQLAlchemyError:
            session.rollback()
            logger.exception(f"Erro de banco de dados ao executar {func.__name__}: ")
            return None
        except ValueError:
            session.rollback()
            logger.exception(f"Erro de validação em {func.__name__}: ")
            return None
        except Exception:
            session.rollback()
            logger.exception(f"Erro inesperado em {func.__name__}: ")
            raise

    return wrapper


def inserir_com_conflito(session, tabela, valores, indices_conflito):
    if not valores:
        logger.info("Nenhum valor para inserir.")
        return 0

    dialect = session.bind.dialect.name

    if dialect == "postgresql":
        from sqlalchemy.dialects.postgresql import insert

        stmt = insert(tabela).values(valores)
        stmt = stmt.on_conflict_do_nothing(index_elements=indices_conflito)
        result = session.execute(stmt)
        return result.rowcount

    table = tabela.__table__
    count = 0
    for valor in valores:
        stmt = table.insert().prefix_with("OR IGNORE").values(valor)
        session.execute(stmt)
        count += 1
    return count


def obter_mapeamento_id(session, modelo, campo_chave, valores):
    """Mapeia valores para IDs no banco de dados."""
    return {
        getattr(item, campo_chave): item.id
        for item in session.query(modelo.id, getattr(modelo, campo_chave))
        .filter(getattr(modelo, campo_chave).in_(valores))
        .all()
    }


@gerenciador_transacao
def last_execution(session):
    ultima_data = session.query(LogExecucao.data_execucao).order_by(desc(LogExecucao.data_execucao)).first()
    if ultima_data:
        return ultima_data[0]
    return None


def atualizar_em_lotes(session, pares, tabela, tamanho_lote=500):
    hoje = get_current_date()
    ontem = hoje - timedelta(days=1)
    atualizacoes = 0
    for i in range(0, len(pares), tamanho_lote):
        lote_atual = pares[i : i + tamanho_lote]
        rows = (
            session.query(tabela)
            .filter(
                tuple_(tabela.produto_id, tabela.cidade_id).in_(lote_atual),
                tabela.data_fim.is_(None),
            )
            .update({"data_fim": ontem}, synchronize_session=False)
        )
        atualizacoes += rows
    return atualizacoes
