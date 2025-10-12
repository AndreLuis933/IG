import asyncio
import logging

from config.logging_config import setup_logger
from site_downloader import download_site

logger = setup_logger(log_level=logging.INFO)


def handler(__, _):
    """Executa o script em background."""
    try:
        logger.info("Iniciando execução do script em background")
        asyncio.run(download_site())

        logger.info("Script executado com sucesso!")
    except Exception:
        logger.exception("Erro na execução do script: ")
