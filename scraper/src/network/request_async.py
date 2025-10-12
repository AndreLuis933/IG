import asyncio
import logging

import aiohttp

from config.request_config import HEADERS
import random

logger = logging.getLogger(__name__)


def calculate_delay(attempt, base_delay=5, increment=5, max_delay=60, jitter_factor=0.1):
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

MAX_CONCURRENT_REQUESTS = 5
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


async def fetch_async(session, url, cookies=None, pbar=None, tipo="produtos", max_retries=25):
    if cookies is None:
        cookies = {}
    delay = calculate_delay(1)
    async with semaphore:
        for attempt in range(1, max_retries + 1):
            try:
                async with session.get(url, headers=HEADERS, cookies=cookies) as response:
                    if response.status == 200:
                        if pbar:
                            pbar.update(1)
                        if tipo == "imagens":
                            content = await response.read()
                            return url, content
                        return await response.json()
                    if response.status == 503 and tipo == "imagens":
                        if pbar:
                            pbar.update(1)
                        logger.warning(f"Status {response.status} nao fazer mais requesicoes para {url}")
                        return (None, None)
                    if attempt < max_retries:
                        delay = calculate_delay(attempt)
                        logger.warning(f"Status {response.status} recebido. Aguardando {delay:.2f} segundos.")

                        await asyncio.sleep(delay)
            except aiohttp.ClientError:  # noqa: PERF203
                logger.exception(f"Erro ao fazer requisição para {url}")
                await asyncio.sleep(delay)

        logger.error(f"Falha após {max_retries} tentativas para {url}")
        if pbar:
            pbar.update(1)
            return (None, None)
        return None
