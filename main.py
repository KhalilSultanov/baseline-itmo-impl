from fastapi import FastAPI, HTTPException, Request
from schemas.request import PredictionResponse, PredictionRequest
from services.llm_service import ask_assistant, init_http_client, close_http_client
from utils.logger import setup_logger


async def lifespan(app: FastAPI):
    """Настройка логгера и HTTP клиента перед запуском."""
    global logger
    logger = await setup_logger()
    await init_http_client()
    yield
    await close_http_client()
    await logger.shutdown()


app = FastAPI(lifespan=lifespan, openapi_url="/openapi.json", docs_url="/docs", redoc_url="/redoc")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирует входящие запросы и ответы."""
    body = await request.body()
    await logger.info(f"Incoming request: {request.method} {request.url} - Body: {body.decode()}")

    response = await call_next(request)

    await logger.info(f"Response status: {response.status_code}")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Логирует неожиданные ошибки."""
    await logger.error(f"Unhandled error: {str(exc)}")
    return HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    """Обработка запроса и возврат ответа от OpenAI."""
    try:
        await logger.info(f"Processing request with id: {body.id}")

        gpt_response = await ask_assistant(body.query)

        response = PredictionResponse(
            id=body.id,
            answer=gpt_response.get("answer"),
            reasoning=gpt_response.get("reasoning", "Ответ не найден."),
            sources=gpt_response.get("sources", [])
        )

        await logger.info(f"Successfully processed request {body.id}")
        return response

    except Exception as e:
        await logger.error(f"Internal error processing request {body.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
