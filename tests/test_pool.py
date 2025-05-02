import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import time
import pytest
from builder.pool import start_pool, add_task, get_results, shutdown_pool, task_queue


# Teste de integração do scraper com o pool de tarefas
@pytest.mark.integration
def test_scraper_pool_integration():
    """
    Testa a integração do scraper com o pool de tarefas, garantindo que os produtos extraídos
    para múltiplas categorias sejam retornados corretamente e possuam os atributos esperados.

    Passos do teste:
    1. Inicia o pool de threads para o scraper.
    2. Adiciona categorias para serem processadas.
    3. Espera até que todas as tarefas sejam concluídas ou o tempo de espera expire.
    4. Obtém os resultados e valida:
        - Se o retorno de cada categoria é uma lista.
        - Se todos os produtos possuem os atributos obrigatórios ('title', 'price', 'category').
        - Se os valores desses atributos têm os tipos corretos.
    """
    # Inicia o pool de threads
    threads = start_pool()

    # Define as categorias a serem processadas
    categories = ["Electronics", "Home Goods", "Apparel", "Cosmetics"]

    # Adiciona uma tarefa para cada categoria
    for category in categories:
        add_task(category)

    # Define o tempo máximo de espera para as tarefas
    start_time = time.time()
    timeout = 60  # Tempo limite em segundos para aguardar as tarefas

    # Espera até que todas as tarefas sejam concluídas ou o tempo limite seja atingido
    while task_queue.unfinished_tasks > 0:
        if time.time() - start_time > timeout:
            break
        time.sleep(1)  # Aguarda 1 segundo entre as verificações

    # Obtém os resultados das categorias processadas
    results = get_results()

    # Valida os resultados para cada categoria
    for i, products in enumerate(results):
        # Verifica se o resultado é uma lista
        assert isinstance(
            products, list
        ), f"Resultado da categoria '{categories[i]}' não é uma lista"

        # Valida cada produto extraído para garantir que possua os atributos corretos
        for product in products:
            # Verifica se o produto possui o atributo 'title'
            assert hasattr(
                product, "title"
            ), f"Produto sem atributo 'title' em '{categories[i]}'"

            # Verifica se o produto possui o atributo 'price'
            assert hasattr(
                product, "price"
            ), f"Produto sem atributo 'price' em '{categories[i]}'"

            # Verifica se o produto possui o atributo 'category'
            assert hasattr(
                product, "category"
            ), f"Produto sem atributo 'category' em '{categories[i]}'"

            # Verifica se 'title' é uma string
            assert isinstance(
                product.title, str
            ), f"Título inválido em '{categories[i]}'"

            # Verifica se 'price' é numérico (int ou float)
            assert isinstance(
                product.price, (int, float)
            ), f"Preço inválido em '{categories[i]}'"

    # Finaliza o pool de threads após a execução
    shutdown_pool(threads)
