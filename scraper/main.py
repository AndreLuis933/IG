import logging

from config.logging_config import setup_logger
from network.stop_machine import stop_fly_machine
from site_downloader import download_site

logger = setup_logger(log_level=logging.INFO)


def executar_script_background():
    """Executa o script em background."""
    try:
        logger.info("Iniciando execução do script em background")
        download_site()
        logger.info("Script executado com sucesso!")
    except Exception:
        logger.exception("Erro na execução do script: ")
    finally:
        stop_fly_machine()


if __name__ == "__main__":
    executar_script_background()
