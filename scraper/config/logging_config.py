import logging
import os
from pathlib import Path

from utils.data import get_current_date


# Configuração básica de logging
def setup_logger(log_level=logging.INFO, log_dir="logs"):
    # Criar diretório de logs se não existir
    # if not Path(log_dir).exists():
    #     os.makedirs(log_dir)

    # Definir nome do arquivo de log com data
    # log_filename = f"{get_current_date()}.log"
    # log_filepath = os.path.join(log_dir, log_filename)

    # Configurar o logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Limpar handlers existentes
    if logger.handlers:
        logger.handlers.clear()

    # Criar handler para arquivo
    # file_handler = logging.FileHandler(log_filepath)
    file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # file_handler.setFormatter(file_format)

    # Criar handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(file_format)

    # Adicionar handlers ao logger
    # logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger
