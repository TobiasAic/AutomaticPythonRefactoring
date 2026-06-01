import logging

def setup_logging(level: logging.Level = logging.INFO):
    app_logger = logging.getLogger("refactoring")
    app_logger.setLevel(level)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(levelname)s %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    app_logger.addHandler(handler)
    app_logger.propagate = False
    return app_logger