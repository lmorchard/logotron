import logging
import logging.handlers

from logotron.config import config

named_log_levels = dict(
    CRITICAL=logging.CRITICAL,
    ERROR=logging.ERROR,
    WARNING=logging.WARNING,
    INFO=logging.INFO,
    DEBUG=logging.DEBUG,
)

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

logger = logging.getLogger(__name__)
