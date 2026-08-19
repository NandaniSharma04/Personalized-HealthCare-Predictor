import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(path: str | None = None):
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)
    if path:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            fh = RotatingFileHandler(str(p), maxBytes=10_000_000, backupCount=5)
            fh.setFormatter(fmt)
            root.addHandler(fh)
        except Exception as e:
            root.warning(f"Could not setup file logging at {path}: {e}")

