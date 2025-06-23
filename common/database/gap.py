from datetime import timedelta

from common.utils.data import get_current_date

from .models import DisponibilidadeCidade, HistoricoPreco, LogExecucao
from .operations.utils import gerenciador_transacao, last_execution


@gerenciador_transacao
def close_gap(session):
    ultima_data = last_execution()
    if not ultima_data:
        return

    diff = get_current_date() - ultima_data
    if diff == timedelta(days=1) or diff == timedelta(days=0):
        return

    session.query(DisponibilidadeCidade).filter(DisponibilidadeCidade.data_fim.is_(None)).update(
        {"data_fim": ultima_data},
        synchronize_session=False,
    )

    session.query(HistoricoPreco).filter(HistoricoPreco.data_fim.is_(None)).update(
        {"data_fim": ultima_data},
        synchronize_session=False,
    )

    print(f"✅ Gap explícito criado: {ultima_data + timedelta(days=1)} até {get_current_date() - timedelta(days=1)}")


@gerenciador_transacao
def log_execution(session):
    ultima_data = last_execution()

    if ultima_data and get_current_date() == ultima_data:
        return
    session.add(LogExecucao(data_execucao=get_current_date()))
