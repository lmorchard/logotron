import os
from dataclasses import dataclass, fields
from dotenv import dotenv_values


@dataclass
class Config:
    user_agent: str = "LogoTron 1.0"
    api_base_url: str = ""
    client_key: str = ""
    client_secret: str = ""
    access_token: str = ""
    debug_requests: bool = False
    debug: bool = False

    def __init__(self, raw_config={}):
        for field in fields(Config):
            env_name = f"LOGOTRON_{field.name.upper()}"
            if env_name in raw_config:
                setattr(self, field.name, raw_config[env_name])


config = Config({
    **dotenv_values(".env"),
    **os.environ
})
