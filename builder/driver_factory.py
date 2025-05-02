from selenium import webdriver


def get_driver() -> webdriver.Chrome:
    """
    Cria e retorna uma instância do WebDriver do Selenium para o navegador Chrome.

    Este método configura o WebDriver para rodar em modo headless (sem interface gráfica),
    desativa algumas funcionalidades de segurança e otimiza o uso de memória para garantir
    que o scraping ou automação sejam executados de forma eficiente em ambientes de servidores
    ou containers.

    :return: Uma instância do WebDriver do Chrome configurada com opções otimizadas.
    """
    # Criação de um objeto ChromeOptions para configurar o navegador
    options = webdriver.ChromeOptions()

    # Configura o navegador para rodar em modo headless (sem interface gráfica)
    options.add_argument("--headless")

    # Adiciona um argumento para desativar a verificação de sandbox (necessário em alguns ambientes)
    options.add_argument("--no-sandbox")

    # Desativa a utilização de memória compartilhada para melhorar a performance em containers
    options.add_argument("--disable-dev-shm-usage")

    # Retorna uma nova instância do WebDriver configurado com as opções acima
    return webdriver.Chrome(options=options)
