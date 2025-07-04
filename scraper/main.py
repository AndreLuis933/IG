import logging
import threading

from flask import Flask

from scraper.config.logging_config import setup_logger
from scraper.network.stop_machine import stop_fly_machine
from scraper.site_downloader import download_site

logger = setup_logger(log_level=logging.INFO)
app = Flask(__name__)
script_lock = threading.Lock()


def executar_script_background():
    """Executa o script em background."""
    if script_lock.acquire(blocking=False):
        try:
            logger.info("Iniciando execução do script em background")
            download_site()
            logger.info("Script executado com sucesso!")
        except Exception:
            logger.exception("Erro na execução do script: ")
        finally:
            script_lock.release()
            stop_fly_machine()
    else:
        logger.info("Script já está em execução, ignorando nova requisição.")


@app.route("/")
@app.route("/health")
def health_check():
    return {"status": "ok", "message": "Scraper service is running"}, 200


@app.route("/run")
def run_script():
    if script_lock.locked():
        return {"message": "Script já está em execução"}, 409

    try:
        thread = threading.Thread(target=executar_script_background)
        thread.daemon = True
        thread.start()
        return {"message": "Script iniciado em background!"}, 202
    except Exception:
        logger.exception("Erro ao iniciar thread ")
        return {"error": "Falha ao iniciar script"}, 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
