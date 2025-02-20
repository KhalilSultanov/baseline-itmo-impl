from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    assistant_id: str

    class Config:
        env_file = ".env"


settings = Settings()
