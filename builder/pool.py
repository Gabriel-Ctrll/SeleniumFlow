import threading
from queue import Queue
from builder.scraper import scrape_category
import logging

# Configuração do logger para registrar eventos e erros durante o processo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Número máximo de workers (threads) que o pool pode ter (neste caso, 4)
MAX_WORKERS = 4

# Fila para armazenar as tarefas que serão processadas pelas threads
task_queue = Queue()

# Resultado compartilhado entre as threads para armazenar os produtos raspados
result = []
# Lock para garantir acesso exclusivo ao resultado quando múltiplas threads estiverem modificando o resultado
result_lock = threading.Lock()


def worker():
    """
    Função que cada thread do pool executa.

    A função pega uma tarefa (categoria) da fila, executa o scraping da categoria utilizando a função
    `scrape_category` e armazena os resultados. A execução ocorre de forma contínua enquanto houver
    tarefas na fila.

    O acesso à lista `result` é protegido por um Lock para evitar problemas de concorrência.
    Quando uma tarefa for concluída, a função `task_done` é chamada para sinalizar que a tarefa foi
    processada e o pool pode seguir para a próxima.

    Exceções são tratadas para garantir que a execução da thread continue mesmo que ocorra um erro durante o scraping.
    """
    while True:
        # Pega uma tarefa da fila
        category = task_queue.get()

        # Se a tarefa for None, encerra a thread
        if category is None:
            task_queue.task_done()
            break

        logger.info(
            f"Thread {threading.current_thread().name} - Começando scraping da categoria: {category}"
        )
        driver = None
        try:
            # Realiza o scraping da categoria
            products = scrape_category(category)

            # Protege o acesso ao resultado compartilhado com o Lock
            with result_lock:
                result.append(products)

            logger.info(
                f"Thread {threading.current_thread().name} - Scraping concluído para {category}"
            )
        except Exception as e:
            # Registra o erro caso ocorra
            logger.error(f"Erro ao raspar categoria {category}: {e}")
        finally:
            # Marca a tarefa como concluída
            task_queue.task_done()

            # Se o driver foi criado, fecha ele
            if driver:
                driver.quit()


def start_pool():
    """
    Inicia o pool de threads.

    Cria as threads que irão executar a função `worker` e as inicia. Cada thread vai processar
    as tarefas da fila de scraping. O número de threads é determinado pela constante `MAX_WORKERS`.

    As threads são iniciadas como daemons para que possam ser finalizadas automaticamente quando o
    processo principal terminar.

    :return: Lista de threads iniciadas.
    """
    threads = []

    # Inicia as threads como daemon
    for i in range(MAX_WORKERS):
        thread = threading.Thread(target=worker, name=f"Worker-{i+1}", daemon=True)
        threads.append(thread)
        thread.start()

    return threads


def add_task(category: str):
    """
    Adiciona uma nova tarefa de scraping na fila.

    A tarefa corresponde a uma categoria que será processada pelas threads do pool. O nome da categoria
    é colocado na fila de tarefas, que será processada pelas threads.

    :param category: Nome da categoria a ser raspada.
    """
    task_queue.put(category)
    logger.info(f"Tarefa de scraping para a categoria '{category}' adicionada à fila.")


def get_results():
    """
    Obtém os resultados do scraping.

    Espera até que todas as tarefas na fila sejam processadas (todas as threads terminem) antes de retornar
    os resultados acumulados.

    :return: A lista `result` com os dados raspados.
    """
    # Aguarda todas as tarefas serem concluídas
    task_queue.join()
    return result


def shutdown_pool(threads):
    """
    Encerra as threads do pool de maneira segura.

    Coloca o valor `None` na fila de tarefas para sinalizar para cada thread que ela deve encerrar sua execução.
    Depois, a função aguarda todas as threads finalizarem com `thread.join()`.

    :param threads: Lista de threads que foram iniciadas no pool.
    """
    # Envia o sinal de parada para todas as threads
    for _ in threads:
        task_queue.put(None)

    # Aguarda todas as threads finalizarem
    for thread in threads:
        thread.join()
