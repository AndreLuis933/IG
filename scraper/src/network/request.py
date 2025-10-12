import logging
import time

import requests
from config.request_config import HEADERS
import random

logger = logging.getLogger(__name__)


def calculate_delay(attempt, base_delay=60, increment=30, max_delay=600, jitter_factor=0.1):
    """Calcula um atraso exponencial com jitter para retentativas.

    Args:
        attempt: Número da tentativa atual
        base_delay: Atraso base em segundos
        increment: Incremento por tentativa em segundos
        max_delay: Atraso máximo em segundos
        jitter_factor: Fator de aleatoriedade (0.0 a 1.0)

    Returns:
        float: Tempo de atraso em segundos

    """
    delay = min(base_delay + (attempt * increment), max_delay)
    jitter = random.uniform(0, delay * jitter_factor)
    return delay + jitter


def fetch(url, cookies=None, pbar=None, max_retries=8):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                cookies=cookies,
                timeout=(10, 30),
            )

            if response.status_code == 200:
                if pbar:
                    pbar.update(1)
                return response

            # Status não é 200
            if attempt < max_retries:
                delay = calculate_delay(attempt)
                logger.warning(
                    f"Status {response.status_code} recebido. Tentativa {attempt}/{max_retries}. Aguardando {delay:.2f}s.",
                )
                time.sleep(delay)

        except requests.exceptions.Timeout:  # noqa: PERF203
            logger.warning(f"Timeout na tentativa {attempt}/{max_retries} para {url}")
            if attempt < max_retries:
                delay = calculate_delay(attempt)
                time.sleep(delay)

        except requests.RequestException as e:
            logger.warning(f"Erro na tentativa {attempt}/{max_retries} para {url}: {e}")
            if attempt < max_retries:
                delay = calculate_delay(attempt)
                time.sleep(delay)

    if pbar:
        pbar.update(1)

    logger.error(f"Falha após {max_retries} tentativas para {url}")
    return None
