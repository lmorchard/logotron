import os
from dataclasses import dataclass, fields
from dotenv import dotenv_values


@dataclass
class Config:
    api_base_url: str = ""
    client_key: str = ""
    client_secret: str = ""
    access_token: str = ""
    user_agent: str = "LogoTron 1.0"
    debug_requests: bool = False
    debug: bool = False
    log_level: str = "DEBUG"
    log_filename: str = "log/bot.log"
    log_maxbytes: int = 100000
    log_backup_count: int = 10
    logo_runner_image: str = "lmorchard/ucblogo-runner"
    logo_runner_mem_limit: str = "512m"
    data_base_dir: str = "data"

    def __init__(self, raw_config={}):
        for field in fields(Config):
            env_name = f"LOGOTRON_{field.name.upper()}"
            if env_name in raw_config:
                setattr(self, field.name, raw_config[env_name])


config = Config({
    **dotenv_values(".env"),
    **os.environ
})
