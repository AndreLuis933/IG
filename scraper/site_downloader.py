import logging
import os
import time
from contextlib import nullcontext

from cookies.load_cookies import load_cookie
from database import (
    close_gap,
    get_null_product_category,
    last_execution,
    log_execution,
    process_raw_data,
    save_availability,
    save_price,
    save_product,
    set_cities,
)
from network.request import fetch
from tqdm import tqdm
from utils.categories import get_categories
from utils.data import get_current_date

logger = logging.getLogger(__name__)


def extract_data(content):
    produtos = content.get("produtos")
    name = [produto.get("nome") for produto in produtos]
    price = [produto.get("valor") for produto in produtos]
    link = ["https://www.irmaosgoncalves.com.br" + produto.get("url") for produto in produtos]
    return name, price, link


def verify_sizes(name, price, link):
    if name != price != link:
        msg = f"Name={name}, Price={price}, Link={link}"
        raise ValueError(msg)


def process_url(url, cookies, category, city, pbar):
    content = fetch(url, cookies, pbar)
    if not content:
        return [], [], city

    product_name, price, link = extract_data(content.json())

    verify_sizes(len(product_name), len(price), len(link))

    products = [(n, l, category) for n, l in zip(product_name, link)]
    prices = list(zip(link, price))

    return products, prices, city


def download_site():
    execution = last_execution()
    if execution == get_current_date():
        logger.info(f"Already executed today: {execution}")
        return

    start_time = time.time()
    cookies = load_cookie("requests")
    set_cities([city for city, _ in cookies])

    base_url = "https://www.irmaosgoncalves.com.br"
    leaf_urls, root_urls, categories = get_categories(base_url)
    urls = root_urls

    show_progress = os.getenv("SHOW_PROGRESS", "true").lower() == "true"

    progress_bar = tqdm(total=len(urls) * len(cookies), desc="Progress") if show_progress else nullcontext()

    with progress_bar as pbar:
        raw_results = [
            process_url(url, cookie, category, city, pbar)
            for url, category in zip(urls, categories)
            for city, cookie in cookies
        ]
    logger.info("Salvnado os dados no banco")
    close_gap()
    processed_data = process_raw_data(raw_results)

    save_product(processed_data.products)
    logger.info(f"{len(processed_data.products)} produtos atualizados ou inseridos com sucesso.")

    alteracoes = save_price(processed_data.uniform_prices, processed_data.variable_prices)
    logger.info(f"Total de alterações de preço: {alteracoes}")

    save_availability(processed_data.availabilities)

    logger.info(f"Available products: {len(processed_data.availabilities)}")
    log_execution()

    end_time = time.time()
    logger.info(f"Total execution time: {(end_time - start_time) / 60:.2f} minutes.")
