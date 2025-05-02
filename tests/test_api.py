import sys
import os

# Garante que o diretório pai esteja no path para importações locais funcionarem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from httpx import AsyncClient, ASGITransport
from automation.app import app
from builder.pool import start_pool, add_task, shutdown_pool


@pytest.mark.asyncio
async def test_submit_task_and_get_result():
    """
    Teste de integração para o endpoint POST /tasks.

    Objetivo:
    - Enviar uma tarefa de scraping com a categoria 'Electronics'.
    - Verificar se a API responde com status 200 e com a mensagem esperada.

    Fluxo:
    1. Cria um cliente HTTP assíncrono usando ASGITransport.
    2. Envia uma requisição POST para /tasks com a categoria desejada.
    3. Valida o código de resposta e o corpo retornado.
    """
    # Configura o transporte ASGI para chamadas internas na app FastAPI
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Envia uma tarefa para o endpoint '/tasks'
        response = await ac.post("/tasks", json={"category": "Electronics"})

        # Valida o status de resposta
        assert response.status_code == 200, "Esperado status 200 ao enviar tarefa"

        # Valida o corpo da resposta
        assert response.json() == {
            "message": "Tarefa recebida",
            "task": {"category": "Electronics"},
        }, "Resposta inesperada ao enviar tarefa"


@pytest.mark.asyncio
async def test_too_many_requests():
    """
    Teste de limitação do pool de tarefas (limite de workers ativos).

    Objetivo:
    - Simular a situação onde todos os workers estão ocupados.
    - Enviar uma nova requisição e garantir que o sistema retorna HTTP 429 (Too Many Requests).

    Fluxo:
    1. Inicia o pool de workers (threads).
    2. Preenche o pool com o número máximo de tarefas (assumido como 4).
    3. Tenta adicionar uma nova tarefa via endpoint '/scrape/Electronics'.
    4. Verifica se a resposta é 429 com a mensagem correta.
    5. Encerra o pool após o teste.
    """
    # Inicia o pool de threads
    threads = start_pool()

    # Envia tarefas até atingir o limite do pool (assumindo MAX_WORKERS = 4)
    for _ in range(4):
        add_task("Electronics")

    # Configura o transporte para chamadas internas à API
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Tenta enviar uma nova tarefa enquanto o pool está cheio
        response = await ac.post("/scrape/Electronics")
        print(f"Response Body: {response.json()}")  # Debug opcional

    # Verifica se o status retornado é 429 (Too Many Requests)
    assert response.status_code == 429, "Esperado status 429 para excesso de tarefas"
    assert (
        response.json()["detail"] == "No worker available"
    ), "Mensagem de erro incorreta"

    # Finaliza o pool ao fim do teste
    shutdown_pool(threads)
