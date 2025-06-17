import logging
import threading

from flask import Flask

from scraper.config.logging_config import setup_logger
from scraper.site_downloader import baixar_site

logger = setup_logger(log_level=logging.INFO)
app = Flask(__name__)

script_lock = threading.Lock()  # Lock para controlar a execução


def executar_script_background():
    """Executa o script em background."""
    if script_lock.acquire(blocking=False):  # Tenta adquirir o lock sem bloquear
        try:
            logger.info("Iniciando execução do script em background")
            baixar_site()
            logger.info("Script executado com sucesso!")
        except Exception:
            logger.exception("Erro na execução do script: ")
        finally:
            script_lock.release()  # Libera o lock após a execução
    else:
        logger.info("Script já está em execução, ignorando nova requisição.")


@app.route("/run")
def run_script():
    # Executa o script em uma thread separada
    thread = threading.Thread(target=executar_script_background)
    thread.daemon = True  # Thread será finalizada quando o programa principal terminar
    thread.start()

    return {"message": "Script iniciado em background!"}, 202
    # get_images() # conseguir a maior contidade de links de imagens
    # extrair_link_categoria_restante() # pega o restante dos links das imagens
    # await baixar_imagem(20000) # faz o download das imagens

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)

