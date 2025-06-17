import logging
import time

import requests

from scraper.config.request_config import HEADERS
from scraper.utils.selenium_helpers import calculate_delay

logger = logging.getLogger(__name__)


def fetch(url, cookies=None, pbar=None, max_retries=8):
    delay = calculate_delay(1)
    for attempt in range(1, max_retries):
        try:
            with requests.get(url, headers=HEADERS, cookies=cookies) as response:
                if response.status_code == 200:
                    if pbar:
                        pbar.update(1)
                    return response.content

                if attempt < max_retries:
                    delay = calculate_delay(attempt)
                    logger.warning(f"Status {response.status_code} recebido. Aguardando {delay} segundos.")

                    time.sleep(delay)
        except requests.RequestException:  # noqa: PERF203
            if pbar:
                pbar.update(1)
            logger.exception(f"Erro ao fazer requisição para {url}")
            time.sleep(delay)

    logger.error(f"Falha após {max_retries} tentativas para {url}")
    return None
