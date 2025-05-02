from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models import Product
from builder.driver_factory import get_driver


def visit_site(driver):
    """
    Acessa o site de scraping.

    Args:
        driver: Instância do Selenium WebDriver.

    Returns:
        None
    """
    driver.get("https://selenium-html-test.replit.app/")


def wait_for_dropdown(driver):
    """
    Espera até que o dropdown de categorias esteja clicável e clica nele.

    Args:
        driver: Instância do Selenium WebDriver.

    Returns:
        None
    """
    dropdown_xpath = "category-filter"  # ID do dropdown de categorias
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, dropdown_xpath)))
    dropdown_element = driver.find_element(By.ID, dropdown_xpath)
    dropdown_element.click()


def select_category(driver, category):
    """
    Espera até que a categoria esteja visível no dropdown e a seleciona.

    Args:
        driver: Instância do Selenium WebDriver.
        category: Nome da categoria a ser selecionada.

    Returns:
        None
    """
    category_xpath = (
        f"//span[normalize-space()='{category}']"  # XPath dinâmico para a categoria
    )
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, category_xpath))
    )
    category_element = driver.find_element(By.XPATH, category_xpath)
    category_element.click()


def extract_product_data(row):
    """
    Extrai os dados de um produto a partir de uma linha da tabela.

    Args:
        row: A linha da tabela contendo os dados do produto.

    Returns:
        Product: Um objeto Product com os dados extraídos da linha.
    """
    try:
        # Extrai o ID do produto
        product_id = row.get_attribute("id").replace("product-", "")
        # Extrai o nome, categoria e preço do produto
        name = row.find_element(By.XPATH, ".//td[2]").text
        category = row.find_element(By.XPATH, ".//td[3]").text
        price = row.find_element(By.XPATH, ".//td[4]").text
        stock = row.find_element(By.XPATH, ".//td[5]").text

        # Cria e retorna um objeto Product com os dados extraídos
        return Product(
            title=name.strip(),
            category=category.strip(),
            price=float(
                price.strip().replace("$", "").replace(",", "")
            ),  # Converte preço para float
            rating=0.0,  # Rating fixo como 0, pois não está visível no HTML
            id=product_id.strip(),  # Link do produto com espaços removidos
            stock=stock.strip(),  # Estoque do produto
        )
    except Exception as e:
        print(f"Erro ao processar linha {row.get_attribute('id')}: {str(e)[:100]}...")
        return None


def scrape_category(category: str) -> list:
    """
    Realiza o scraping dos produtos para uma categoria específica no site.

    Args:
        category: Nome da categoria a ser raspada.

    Returns:
        list: Lista de objetos Product com os dados dos produtos.
    """
    driver = get_driver()
    try:
        # Acessa o site
        visit_site(driver)

        # Espera o dropdown estar clicável e clica nele
        wait_for_dropdown(driver)

        # Espera a categoria estar visível e seleciona
        select_category(driver, category)

        # Lista para armazenar os produtos encontrados
        products = []

        # Encontra todas as linhas de produtos na tabela
        rows = driver.find_elements(By.XPATH, "//table//tr[contains(@id, 'product-')]")

        # Extrai os dados de cada linha e adiciona à lista de produtos
        for row in rows:
            product = extract_product_data(row)
            if product:
                products.append(product)

        return products
    finally:
        # Fecha o driver do Selenium após o scraping
        driver.quit()
