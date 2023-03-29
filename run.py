import logging
import logging.handlers

from logotron.config import config
from logotron.bot import Bot
from logotron.logo_runner import LogoRunner

import docker

logging.basicConfig(
    handlers=[logging.handlers.RotatingFileHandler('bot.log', maxBytes=100000, backupCount=10),
              logging.StreamHandler()],
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%dT%H:%M:%S')

LOGGER = logging.getLogger(__name__)


def main():
    base_paths = [
        "/home/lmorchard/workspace/logotron/data/001",
        "/home/lmorchard/workspace/logotron/data/002",
        "/home/lmorchard/workspace/logotron/data/003",
    ]
    for base_path in base_paths:
        runner = LogoRunner(base_path=base_path, config=config, logger=LOGGER)
        runner.run()

    #bot = Bot(config=config, logger=LOGGER)
    # bot.run_streaming()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        LOGGER.exception("Uncaught exception")
        raise
