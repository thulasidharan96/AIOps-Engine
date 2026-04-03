from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App config
    PROJECT_NAME: str = "AIOps Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = Field(default="development")

    
    # Database
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_DB: str = Field(default="aiops")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Observability Clients
    PROMETHEUS_URL: str = Field(default="http://localhost:9090")
    LOKI_URL: str = Field(default="http://localhost:3100")
    
    # LLM Settings
    OPENAI_API_KEY: str = Field(default="sk-mock-key")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo")
    OLLAMA_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="qwen3:4b")
    
    # Remediation safety
    AUTO_EXECUTE_ENABLED: bool = Field(default=False)
    APPROVAL_MODE: bool = Field(default=True)

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
