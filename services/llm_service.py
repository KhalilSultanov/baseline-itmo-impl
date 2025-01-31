import logging
import json
import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "OpenAI-Beta": "assistants=v2"
}

client: httpx.AsyncClient | None = None


async def init_http_client():
    """Создаёт глобальный HTTP-клиент один раз при запуске"""
    global client
    if client is None:
        client = httpx.AsyncClient(headers=HEADERS, timeout=10.0)


async def close_http_client():
    """Закрывает HTTP-клиент при завершении работы"""
    global client
    if client:
        await client.aclose()
        client = None


async def wait_for_completion(chat_id, run_id, max_retries=20, initial_delay=1.0):
    """
    Асинхронно ждет завершения выполнения задачи OpenAI через ProxyAPI с экспоненциальной задержкой.
    """
    try:
        delay = initial_delay
        for attempt in range(max_retries):
            response = await client.get(f"{API_URL}/threads/{chat_id}/runs/{run_id}")
            if response.status_code != 200:
                logger.error(f"Ошибка получения статуса: {response.text}")
                return None

            run_status = response.json().get("status")
            logger.debug(f"Run {run_id} status: {run_status}")

            if run_status == "completed":
                return run_status

            await asyncio.sleep(delay)
            delay *= 2

        logger.error(f"Превышено максимальное количество попыток ожидания завершения задачи {run_id}")
        return None

    except Exception as e:
        logger.error(f"Ошибка ожидания завершения: {e}")
        return None


async def ask_assistant(question: str) -> dict:
    """Отправляет запрос в OpenAI через ProxyAPI и получает ответ."""
    global client
    if client is None:
        await init_http_client()

    try:
        # Заменяем asyncio.timeout() на asyncio.wait_for()
        thread_response = await asyncio.wait_for(
            client.post(f"{API_URL}/threads"), timeout=15
        )

        if thread_response.status_code != 200:
            logger.error(f"Ошибка создания треда: {thread_response.text}")
            return {"reasoning": "Ошибка создания треда", "answer": None, "sources": []}

        chat_id = thread_response.json().get('id')

        message_response = await asyncio.wait_for(
            client.post(
                f"{API_URL}/threads/{chat_id}/messages",
                json={"role": "user", "content": question}
            ), timeout=15
        )
        if message_response.status_code != 200:
            logger.error(f"Ошибка отправки сообщения: {message_response.text}")
            return {"reasoning": "Ошибка отправки сообщения", "answer": None, "sources": []}

        run_response = await asyncio.wait_for(
            client.post(
                f"{API_URL}/threads/{chat_id}/runs",
                json={"assistant_id": ASSISTANT_ID}
            ), timeout=15
        )
        if run_response.status_code != 200:
            logger.error(f"Ошибка запуска ассистента: {run_response.text}")
            return {"reasoning": "Ошибка запуска ассистента", "answer": None, "sources": []}

        run_id = run_response.json().get('id')

        run_status = await wait_for_completion(chat_id, run_id)
        if not run_status:
            return {"reasoning": "AI request timeout", "answer": None, "sources": []}

        messages_response = await asyncio.wait_for(
            client.get(f"{API_URL}/threads/{chat_id}/messages"), timeout=15
        )
        if messages_response.status_code != 200:
            logger.error(f"Ошибка получения ответа: {messages_response.text}")
            return {"reasoning": "Ошибка получения ответа", "answer": None, "sources": []}

        latest_message = next(
            (msg['content'][0]['text']['value'] for msg in messages_response.json().get('data', [])
             if msg['role'] == 'assistant'),
            None
        )

        if latest_message is None:
            logger.error("Ответ от ассистента не найден.")
            return {"reasoning": "Ответ от ассистента не найден", "answer": None, "sources": []}

        logger.info(f"Ответ от AI: {latest_message}")

        try:
            gpt_response = json.loads(latest_message)
        except json.JSONDecodeError:
            gpt_response = {"reasoning": latest_message, "answer": None, "sources": []}
            logger.warning("Некорректный JSON-ответ, возвращаем текст.")

        return gpt_response

    except asyncio.TimeoutError:
        logger.error("Превышен лимит времени ожидания запроса к AI")
        return {"reasoning": "AI request timeout", "answer": None, "sources": []}

    except Exception as e:
        logger.error(f"Ошибка взаимодействия с ProxyAPI: {e}")
        return {"reasoning": "Ошибка при обращении к AI", "answer": None, "sources": []}
