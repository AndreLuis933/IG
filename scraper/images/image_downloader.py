import asyncio

import aiohttp
from tqdm import tqdm

from database import get_image_links, save_images
from network.request_async import fetch_async


async def baixar_imagem(linhas=20000):
    """Processa requisições assíncronas e salva imagens no banco de dados.

    :param linhas: Numero maximo de urls a serem baixadas
    """
    total_requests = get_image_links()[:linhas]
    if not total_requests:
        return
    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(total_requests), desc="Progresso") as pbar:
            tasks = [fetch_async(session, url, pbar=pbar, tipo="imagens") for url in total_requests]
            results = await asyncio.gather(*tasks)

    save_images([(content, url) for url, content in results])
