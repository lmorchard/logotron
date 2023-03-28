import logging
import logging.handlers
import isodate
import datetime
import os

import mastodon

from logotron.config import config

logging.basicConfig(
    handlers=[logging.handlers.RotatingFileHandler('bot.log', maxBytes=100000, backupCount=10),
              logging.StreamHandler()],
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%dT%H:%M:%S')

LOGGER = logging.getLogger(__name__)


def main():
    print(f"HELLO WORLD, {config}")

    client = mastodon.Mastodon(
        user_agent=config.user_agent,
        api_base_url=config.api_base_url,
        client_id=config.client_key,
        client_secret=config.client_secret,
        access_token=config.access_token,
        debug_requests=config.debug,
    )

    client.status_post(
        status=f"hello there, it is {datetime.datetime.now().isoformat()}")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        LOGGER.exception("Uncaught exception")
        raise
