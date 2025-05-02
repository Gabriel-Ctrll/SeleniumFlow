import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from builder.scraper import scrape_category
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from models import Product


# Fixture para configurar o driver do Selenium em modo headless
@pytest.fixture(scope="module")
def driver():
    """
    Configura e inicializa o driver do Selenium com as opções necessárias para rodar o navegador
    em modo headless, sem a interface gráfica. A fixture será executada uma vez por módulo de teste.
    """
    # Configurações do Chrome para rodar em headless
    options = Options()
    options.add_argument("--headless=new")  # Modo headless (sem interface gráfica)
    options.add_argument(
        "--no-sandbox"
    )  # Desabilita o sandbox (necessário para alguns ambientes)
    options.add_argument("--disable-dev-shm-usage")  # Previne falhas no Docker

    # Inicializa o driver do Chrome com as configurações acima
    driver = webdriver.Chrome(options=options)

    # Garante que o driver seja finalizado após os testes
    yield driver
    driver.quit()


def test_scrape_existing_category(driver):
    """
    Testa a função 'scrape_category' para garantir que a extração de produtos de uma categoria
    existente (no caso 'Apparel') esteja funcionando corretamente.

    - Verifica se os produtos extraídos são uma lista.
    - Verifica se ao menos um produto foi extraído.
    - Garante que todos os produtos extraídos sejam instâncias da classe Product.
    - Valida se os produtos possuem os atributos obrigatórios ('title', 'price', 'category').
    - Verifica se os atributos 'title' e 'category' são do tipo string e 'price' é numérico.
    """
    # Testa a categoria 'Apparel' (pode ser alterada conforme necessário)
    products = scrape_category("Apparel")

    # Verifica se a função retorna uma lista
    assert isinstance(
        products, list
    ), "Os produtos não estão sendo retornados como uma lista"

    # Verifica se há pelo menos um produto extraído
    assert len(products) > 0, "Nenhum produto foi extraído"

    # Verifica se todos os itens na lista são instâncias da classe Product
    assert all(
        isinstance(p, Product) for p in products
    ), "Nem todos os produtos são instâncias da classe 'Product'"

    # Validação adicional: Verifica se cada produto possui atributos obrigatórios
    for product in products:
        # Verifica se o produto possui os atributos necessários
        assert hasattr(
            product, "title"
        ), f"Produto {product} não tem o atributo 'title'"
        assert hasattr(
            product, "price"
        ), f"Produto {product} não tem o atributo 'price'"
        assert hasattr(
            product, "category"
        ), f"Produto {product} não tem o atributo 'category'"

        # Verifica se os atributos têm os tipos corretos
        assert isinstance(
            product.title, str
        ), f"O título do produto {product} não é uma string"
        assert isinstance(
            product.price, (int, float)
        ), f"O preço do produto {product} não é numérico"
        assert isinstance(
            product.category, str
        ), f"A categoria do produto {product} não é uma string"
