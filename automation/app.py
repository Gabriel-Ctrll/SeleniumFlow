from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from executer.api import router
from executer.service import scrape_products_by_category
from builder.pool import task_queue, MAX_WORKERS, add_task, start_pool
from models import Product, ScrapeResponse
from contextlib import asynccontextmanager

# Criação da aplicação FastAPI
app = FastAPI()

# Inclui o roteador da API
app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] Iniciando pool de scraping...")
    start_pool()  # Inicia o pool de scraping


# Endpoint para realizar scraping de produtos de uma categoria
@router.get("/scrape", response_model=ScrapeResponse)
async def fetch_products(category: str):
    """
    Realiza o scraping de produtos para uma categoria específica.
    A função utiliza scraping assíncrono e retorna uma lista de produtos.

    :param category: Nome da categoria de produtos a ser raspada.
    :return: ScrapeResponse contendo os produtos raspados.
    """
    try:
        # Obter os produtos brutos utilizando o método de scraping assíncrono
        raw_products = await run_in_threadpool(scrape_products_by_category, category)

        # Caso os produtos sejam retornados em uma lista de listas, achata a estrutura
        if raw_products and isinstance(raw_products[0], list):
            raw_products = [item for sublist in raw_products for item in sublist]

        # Verifica se não há produtos retornados
        if not raw_products:
            return ScrapeResponse(products=[])

        # Verifica a estrutura de cada produto antes de converter
        for item in raw_products:
            print(f"Produto recebido: {item}")

        # Converte os dados dos produtos para instâncias da classe Product
        products = []
        for prod in raw_products:
            try:
                # Se já for um objeto Product, adiciona diretamente
                if isinstance(prod, Product):
                    products.append(prod)
                # Se for um dicionário, cria um objeto Product com os dados
                elif isinstance(prod, dict):
                    products.append(Product(**prod))

            except Exception as e:
                # Captura e exibe erros ao processar produtos individuais
                print(f"Erro ao processar produto: {prod} - Erro: {str(e)}")

        # Retorna os produtos convertidos no formato esperado
        return ScrapeResponse(products=products)

    except Exception as e:
        # Exceção genérica para erros no processo de scraping
        print(f"Erro ao processar a requisição: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Erro ao fazer scraping da categoria"
        )


# Endpoint para iniciar o scraping de uma categoria com base em uma requisição POST
@app.post("/scrape/{category}")
async def scrape_category(category: str):
    """
    Inicia o processo de scraping para a categoria fornecida. Verifica se há workers disponíveis no pool.

    :param category: Nome da categoria de produtos a ser raspada.
    :return: Mensagem de sucesso ou erro.
    """
    # Verifica se o número de tarefas no pool atingiu o limite máximo de workers
    if task_queue.qsize() >= MAX_WORKERS:
        raise HTTPException(status_code=429, detail="No worker available")

    # Adiciona a tarefa ao pool de scraping
    add_task(category)

    return {"message": f"Scraping started for category '{category}'"}


# Endpoint para receber tarefas para processamento
@app.post("/tasks")
async def submit_task(task: dict):
    """
    Endpoint para enviar uma nova tarefa para processamento.

    :param task: Dados da tarefa a ser processada.
    :return: Confirmação de recebimento da tarefa.
    """
    return {"message": "Tarefa recebida", "task": task}
