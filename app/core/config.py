from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    traffic_provider: str = "mock"
    mock_traffic_count: int = 500
    log_level: str = "INFO"
    cors_origins: str = "*"
    pcap_encryption_key: str = ""
    pcap_encryption_key: str = ""
    real_rpc_url: str = ""
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
