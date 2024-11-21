import base64
import os
from typing import List, Union, ClassVar
from goodconf import GoodConf, Field
from pydantic import validator


class AppConfig(GoodConf):
    class Config:
        default_files = ["/etc/audiobot/config.yaml", "config.yaml"]
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra='allow'  # or 'forbid' / 'ignore'

    "Configuration for backend"

    "App configuration"
    APP_NAME: str = Field(default="project", description="App name for project")
    DJANGO_SETTINGS_MODULE: str = Field(default="config.settings.local", description="settings module")

    "Debug and log configuration"
    ENV: str = Field(default="DEV", description="Environment")
    # LOG_LEVEL: str = Field(initial="INFO", description="Log level for project")

    PROJECT_URL: str = Field(description="Proejct url for email and csrf module")
    "CORS and Allowed hosts"
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ALLOWED_ORIGINS: List[str] = ["*"]

    # App version and acceptable version
    LATEST_VERSION: ClassVar[int] = 1
    ACCEPTABLE_VERSION: ClassVar[int] = 1


    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    "Auth configuration"
    JWT_TOKEN_TTL_IN_MINUTES: int = Field(
        description="Token TTL in minutes",
    )
    JWT_SECRET_KEY: str = Field(
        default=lambda: base64.b64encode(os.urandom(32)).decode(),
        description="JWT secret key for signing tokens"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for signing JWT tokens (e.g., HS256, RS256)"
    )

    SECRET_KEY: str = Field(
        initial=lambda: base64.b64encode(os.urandom(60)).decode(),
        description="Used for cryptographic signing. https://docs.djangoproject.com/en/2.0/ref/settings/#secret-key",
    )

    "Admin config"
    ADMIN_URL: str = Field(default="admin/", description="Environment")

    "Database configuration"
    PG_DB_HOST: str = Field(description="Postgres port")
    PG_DB_PORT: int = Field(initial=5432, description="Postgres port")
    PG_DB_USER: str = Field(description="Postgres port")
    PG_DB_PASS: str = Field(description="Postgres port")
    PG_DB_NAME: str = Field(description="Postgres port")


    "Email configuration"
    EMAIL_USE_TLS: bool = Field(
        default=True, description="Whether to use tls port or not"
    )
    EMAIL_PORT: int = Field(default=587, description="Outgoing smtp port")
    EMAIL_HOST: str = Field(description="SMTP host name")
    EMAIL_HOST_USER: str = Field(description="SMTP username")
    EMAIL_HOST_PASSWORD: str = Field(description="SMTP password")
    EMAIL_FROM: str = Field(description="From email address")

    "Openai configuration"
    OPENAI_API_KEY: str = Field(
        description="openai api key for access openai api"
    )
    OPENAI_GPT_MODEL_KEY: str = Field(
    description="openai gpt model api key"
    )
    OPENAI_WHISPER_MODEL_KEY: str = Field(
        description="openai whisper model api key"
    )
    OPENAI_TTS_MODEL_KEY: str = Field(
        description="openai tts model api key"
    )

    OPENAI_ASSISTANT_KEY: str = Field(
        description="openai tts model api key"
    )

    @property
    def DEBUG(self):
        try:
            return self.ENV == "DEV"
        except:
            pass
        return False


app_config = AppConfig()
app_config.load()
