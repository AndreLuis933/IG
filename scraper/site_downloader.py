import logging
import os
import time
from contextlib import nullcontext

from bs4 import BeautifulSoup
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


def extract_data(soup):
    name_link = [
        i.find("a")
        for i in soup.find_all(class_="h-[72px] text-ellipsis overflow-hidden cursor-pointer mt-2 text-center")
    ]
    name = [name.text.strip() for name in name_link if name]
    link = ["https://www.irmaosgoncalves.com.br" + link.get("href") for link in name_link if link and link.get("href")]

    price = [a.text.strip() for a in soup.find_all("div", class_="text-xl text-secondary font-semibold h-7")]

    return name, price, link


def verify_sizes(name, price, link):
    if name != price != link:
        msg = f"Name={name}, Price={price}, Link={link}"
        raise ValueError(msg)


def process_url(url, cookies, category, city, pbar):
    content = fetch(url, cookies, pbar)
    if not content:
        return [], [], city

    soup = BeautifulSoup(content, "html.parser")
    product_name, price, link = extract_data(soup)

    verify_sizes(len(product_name), len(price), len(link))

    products = [(n, l, category) for n, l in zip(product_name, link)]
    prices = [(l, float(p.replace("R$", "").replace(".", "").replace(",", ".").strip())) for p, l in zip(price, link)]

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
    urls = leaf_urls

    logger.info(f"Products without category: {len(get_null_product_category())}")
    if len(get_null_product_category()) < 10000:
        urls = root_urls
        categories = len(urls) * [None]

    show_progress = os.getenv("SHOW_PROGRESS", "true").lower() == "true"

    progress_bar = tqdm(total=len(urls) * len(cookies), desc="Progress") if show_progress else nullcontext()

    with progress_bar as pbar:
        raw_results = [
            process_url(url, cookie, category, city, pbar)
            for url, category in zip(urls, categories)
            for city, cookie in cookies
        ]

    close_gap()
    processed_data = process_raw_data(raw_results)

    save_product(processed_data.products)

    save_price(processed_data.uniform_prices, processed_data.variable_prices)

    save_availability(processed_data.availabilities)

    log_execution()

    logger.info(f"Available products: {len(processed_data.availabilities)}")

    end_time = time.time()
    logger.info(f"Total execution time: {(end_time - start_time) / 60:.2f} minutes.")
