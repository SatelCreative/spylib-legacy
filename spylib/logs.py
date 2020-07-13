from loguru import logger
import logging


class InterceptHandler(logging.Handler):
    """ Logging handler intercepting existing handlers to redirect them to loguru """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_webapp_logging(logfilename: str):
    """ Catch and redirect the loggers already defined in uvicorn towards loguru """
    logging.getLogger('uvicorn.access').handlers = [InterceptHandler()]
    logging.getLogger('fastapi').handlers = [InterceptHandler()]
    logging.getLogger().handlers = [InterceptHandler()]

    logger.add(f'/python/logs/{logfilename}.log', rotation='10 MB', retention="14 days")