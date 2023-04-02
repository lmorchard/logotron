from logotron.config import config
from logotron.logging import logger
from logotron.bot import Bot


def main():
    bot = Bot(config=config)
    # bot.poll_notifications()
    bot.run_streaming()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logger.exception("Uncaught exception")
        raise
