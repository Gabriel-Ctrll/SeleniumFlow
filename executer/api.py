from builder.pool import task_queue, MAX_WORKERS
from executer.service import scrape_products_by_category
from fastapi import HTTPException, APIRouter
from models import ScrapeResponse

router = APIRouter()


@router.get("/scrape", response_model=ScrapeResponse)
def scrape(category: str):
    """
    Endpoint que realiza o scraping dos produtos para uma categoria específica.

    Valida se há workers disponíveis para realizar o scraping e, em caso afirmativo,
    executa a função `scrape_products_by_category` para obter os produtos dessa categoria.

    Args:
        category (str): Categoria de produtos a ser raspada.

    Raises:
        HTTPException: Se não houver workers disponíveis, retorna status 429 (Too Many Requests).

    Returns:
        ScrapeResponse: Resposta com a lista de produtos raspados da categoria.
    """

    # Verifica se há workers disponíveis
    if task_queue.qsize() >= MAX_WORKERS:
        raise HTTPException(status_code=429, detail="No worker available")

    # Realiza o scraping da categoria e retorna os resultados
    return scrape_products_by_category(category)
