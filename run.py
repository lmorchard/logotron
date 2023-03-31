from logotron.config import config
from logotron.logging import logger
from logotron.bot import Bot


def main():
    bot = Bot(config=config, logger=logger)
    bot.run_streaming()
    # bot.poll_notifications()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logger.exception("Uncaught exception")
        raise
