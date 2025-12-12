import os
import time
from pathlib import Path

import requests


def load_env():
    if Path(".env").exists():
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


load_env()

SERVICE_ROLE = os.getenv("SERVICE_ROLE")
PROJECT = os.getenv("PROJECT")
URL = f"https://{PROJECT}.supabase.co/functions/v1/processar-metricas"

headers = {"Authorization": f"Bearer {SERVICE_ROLE}"}
total_dias = 0

print("Iniciando processamento do backlog...")

while True:
    try:
        response = requests.get(URL, headers=headers, timeout=180)
        data = response.json()

        dias = data.get("diasProcessados", 0)
        total_dias += dias

        print(f"Processados: {dias} dias | Total acumulado: {total_dias} dias")

        if dias == 0:
            print(f"\nProcessamento completo! Total: {total_dias} dias processados.")
            break

        time.sleep(2)

    except Exception as e:
        print(f"Erro: {e}")
        print("Tentando novamente em 5 segundos...")
        time.sleep(5)

