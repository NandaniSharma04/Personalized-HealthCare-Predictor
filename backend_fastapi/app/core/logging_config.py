import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(log_file: str | None = None):
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root.addHandler(sh)

    if log_file:
        p = Path(log_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(str(p), maxBytes=10 * 1024 * 1024, backupCount=5)
        fh.setFormatter(formatter)
        root.addHandler(fh)
