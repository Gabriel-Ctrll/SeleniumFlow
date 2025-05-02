from models import ScrapeResponse
from fastapi import HTTPException
from builder.pool import add_task, get_results, task_queue
from itertools import chain

# Categorias válidas disponíveis no site de teste
VALID_CATEGORIES = {"Apparel", "Electronics", "Cosmetic", "Home Goods"}


def scrape_products_by_category(category: str) -> ScrapeResponse:
    """
    Realiza o scraping dos produtos para uma categoria específica.

    Valida se a categoria é válida e não está vazia, verifica se há workers disponíveis
    para realizar o scraping e, em seguida, retorna a resposta com os produtos raspados.

    Args:
        category (str): Categoria de produtos a ser raspada.

    Raises:
        HTTPException:
            - 400 se a categoria for inválida.
            - 429 se não houver workers disponíveis.
        RuntimeError: Se ocorrer um erro durante o processo de scraping.

    Returns:
        ScrapeResponse: Resposta com a lista de produtos raspados da categoria.
    """

    # Valida a categoria fornecida
    if not category.strip():
        raise ValueError("A categoria não pode estar vazia.")

    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Categoria inválida. Use uma das seguintes: {', '.join(VALID_CATEGORIES)}",
        )

    # Verifica se há workers disponíveis para realizar o scraping
    if task_queue.qsize() >= 4:
        raise HTTPException(status_code=429, detail="No worker available")

    try:
        # Adiciona a tarefa de scraping à fila
        add_task(category)
        print(f"Tarefa de scraping para '{category}' adicionada.")

        # Aguardar a conclusão do scraping e obter os resultados
        products = get_results()

        # Desempacota a lista de produtos (caso seja uma lista de listas)
        flattened_products = list(chain.from_iterable(products))

        # Cria a resposta com os produtos raspados
        response = ScrapeResponse(products=flattened_products)

        return response
    except HTTPException:
        raise

    except Exception as e:
        # Captura e loga o erro, e levanta uma exceção customizada
        print(f"Erro ao processar a requisição de scraping: {str(e)}")
        raise RuntimeError(
            f"Erro ao fazer scraping da categoria '{category}': {str(e)}"
        )
