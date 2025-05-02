# SeleniumFlow
# 🕸️ Web Scraper Service – FastAPI, Selenium & Thread Pool

Este projeto foi desenvolvido por **Gabriel Araujo da Silva** . Trata-se de um serviço assíncrono para extração de dados de produtos via web scraping, com controle de concorrência por pool de threads e disponibilização via API REST com FastAPI.

---

## 📌 Visão Geral

A aplicação permite enviar requisições para extrair dados de categorias específicas de produtos. Utiliza Selenium para navegação automatizada em modo headless e gerencia múltiplas requisições simultâneas por meio de um thread pool.

---

## ⚙️ Tecnologias Utilizadas

- **Python 3.10+**
- **FastAPI** – criação de APIs RESTful modernas e rápidas.
- **Selenium (Chrome Headless)** – scraping automatizado.
- **Threading / Queue** – controle concorrente de tarefas.
- **Pytest + HTTPX** – testes assíncronos e de integração.
- **Docker** – isolamento e portabilidade do ambiente.

---

## Como Executar

1. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt

   ### Execute o servidor FastAPI:

```bash
uvicorn automation.app:app --reload
```

### Rode os testes:

```bash
pytest
```

> **Requisitos**: Google Chrome e ChromeDriver compatíveis instalados.  
> Para execução headless, o ambiente deve suportar as flags de sandboxing (Linux recomendado).

---

## 🧪 Estrutura de Testes

| Arquivo         | Descrição                                                                 |
|------------------|---------------------------------------------------------------------------|
| `test_scraper.py` | Valida o retorno do scraper, atributos esperados e tipos dos produtos.    |
| `test_pool.py`    | Testa o fluxo completo com múltiplas tarefas em pool de threads.          |
| `test_api.py`     | Testes de integração dos endpoints FastAPI com resposta e limites de carga.|

> Todos os testes são **automatizados**, com uso de fixtures, `ASGITransport` e validação completa dos atributos dos produtos extraídos.

---

## 📈 Premissas e Decisões Técnicas

- O controle de tarefas é feito **em memória**, utilizando `queue.Queue`.
- Um número fixo de workers (`MAX_WORKERS = 4`) foi definido para simplificar o gerenciamento.
- O scraping assume que o site de destino **não possui bloqueios** contra navegadores headless.
- O sistema retorna `HTTP 429` caso **todas as threads estejam ocupadas**.

---

## Autor
Desenvolvido por **Gabriel Araujo da Silva**  
📧 Email: [araujo.gabrielsilva2@gmail.com] 
---

> Este projeto foi elaborado com foco em clareza arquitetural, qualidade de código e boas práticas de testes automatizados.
