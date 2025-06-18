import logging
import os

import requests

logger = logging.getLogger(__name__)


def get_machine_id():
    """Obtém o ID da máquina atual via metadados da Fly."""
    try:
        # A Fly.io disponibiliza metadados via HTTP
        response = requests.get("http://169.254.169.254/metadata/v1/machine", timeout=5)
        if response.status_code == 200:
            return response.json().get("id")
    except Exception as e:
        logger.warning(f"Não foi possível obter machine ID via metadados: {e}")

    # Fallback para variável de ambiente
    return os.environ.get("FLY_MACHINE_ID")


def stop_fly_machine():
    """Para a máquina atual usando a API do Fly."""
    try:
        machine_id = get_machine_id()
        app_name = os.environ.get("FLY_APP_NAME")
        fly_api_token = os.environ.get("FLY_API_TOKEN")

        if not all([machine_id, app_name, fly_api_token]):
            logger.warning("Informações necessárias para parar a máquina não estão disponíveis.")
            return

        url = f"https://api.machines.dev/v1/apps/{app_name}/machines/{machine_id}/stop"
        headers = {"Authorization": f"Bearer {fly_api_token}"}

        resp = requests.post(url, headers=headers, timeout=10)
        logger.info(f"Parando máquina: {resp.status_code} {resp.text}")

        if resp.status_code == 200:
            logger.info("Máquina parada com sucesso!")
        else:
            logger.error(f"Erro ao parar máquina: {resp.status_code} - {resp.text}")

    except Exception:
        logger.exception("Erro ao parar máquina: ")
