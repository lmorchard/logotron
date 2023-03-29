import logging
import logging.handlers

from logotron.config import config
from logotron.bot import Bot

logging.basicConfig(
    handlers=[logging.handlers.RotatingFileHandler('bot.log', maxBytes=100000, backupCount=10),
              logging.StreamHandler()],
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%dT%H:%M:%S')

LOGGER = logging.getLogger(__name__)


def main():
    bot = Bot(config=config, logger=LOGGER)
    bot.run_streaming()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        LOGGER.exception("Uncaught exception")
        raise
