import logging
import os

import requests

logger = logging.getLogger(__name__)


def stop_fly_machine():
    """Para a máquina atual usando a API do Fly."""
    machine_id = os.environ.get("FLY_MACHINE_ID")
    app_name = os.environ.get("FLY_APP_NAME")
    fly_api_token = os.environ.get("FLY_API_TOKEN")

    if not all([machine_id, app_name, fly_api_token]):
        logger.warning("Informações necessárias para parar a máquina não estão disponíveis.")
        return

    url = f"https://api.machines.dev/v1/apps/{app_name}/machines/{machine_id}/stop"
    headers = {"Authorization": f"Bearer {fly_api_token}"}

    resp = requests.post(url, headers=headers, timeout=10)

    if resp.status_code == 200:
        logger.info("Máquina parada com sucesso!")
        return

    logger.error(f"Erro ao parar máquina: {resp.status_code} - {resp.text}")
