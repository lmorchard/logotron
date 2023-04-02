import logging
import logging.handlers

from io import StringIO

from logotron.config import config


named_log_levels = dict(
    CRITICAL=logging.CRITICAL,
    ERROR=logging.ERROR,
    WARNING=logging.WARNING,
    INFO=logging.INFO,
    DEBUG=logging.DEBUG,
)


def build_logger(config, name=__name__):
    logging.basicConfig(
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                config.log_filename,
                maxBytes=config.log_maxbytes,
                backupCount=config.log_backup_count
            ),
        ],
        level=named_log_levels.get(config.log_level, "INFO"),
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    return logging.getLogger(name)


logger = build_logger(config)
