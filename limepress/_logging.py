import logging
import sys

from loguru import logger


# both classes are taken from the loguru documentation
# https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
class PropagateHandler(logging.Handler):
    def emit(self, record):
        logging.getLogger(record.name).handle(record)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, record.getMessage())


def setup_propagate_handler():
    logger.remove(0)  # disable stderr
    logger.add(PropagateHandler(), format="{message}")


def setup_intercept_handler():
    kwargs = {
        'handlers': [InterceptHandler()],
        'level': 0,
    }

    if sys.version_info >= (3, 8):
        kwargs['force'] = True

    logging.basicConfig(**kwargs)
