import logging
import os
from typing import Optional

def setup_logging(log_level: Optional[str] = None) -> None:
    """Setup logging configuration.
    Call this once in main(). Other modules just use logging.getLogger(__name__).
    """
    log_level = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - pid=%(process)d - thread=%(threadName)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    for noisy in (
            "APILogger",  # your API dump logger
           # "WebsocketLogger",  # your WS status logger
            "socketio",  # python-socketio root (covers children)
            "engineio",  # python-engineio root (covers children)
    ):
        lg = logging.getLogger(noisy)
        lg.setLevel(logging.WARNING)  # was DEBUG -> only WARN/ERROR now
        lg.propagate = False  # don't bubble to root handlers