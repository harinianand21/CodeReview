import os
from typing import List, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings and environment variables.
    """
    APP_NAME: str = "CodeInsight AI"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # CORS Configuration
    ALLOWED_HOSTS: List[str] = ["*"]

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
