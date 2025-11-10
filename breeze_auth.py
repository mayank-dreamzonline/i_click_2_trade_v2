# breeze_auth.py
import os
from typing import Optional
from breeze_connect import BreezeConnect

# Optional: load .env if python-dotenv is installed (local dev convenience)
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except Exception:
    pass

ENV_API_KEY = "ICICI_API_KEY"
ENV_SECRET  = "ICICI_SECRET_KEY"
ENV_SESSION = "ICICI_API_SESSION"

def _get_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it in your shell or a .env file (never commit secrets)."
        )
    return val

class BreezeAuth:
    """
    Factory for an authenticated BreezeConnect client using environment variables:
      - ICICI_API_KEY
      - ICICI_SECRET_KEY
      - ICICI_API_SESSION

    Optionally allow explicit injection (for tests/CI or secret managers).
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        session_token: Optional[str] = None,
    ):
        api_key = api_key or _get_env(ENV_API_KEY)
        api_secret = api_secret or _get_env(ENV_SECRET)
        session_token = session_token or _get_env(ENV_SESSION)

        self._breeze = BreezeConnect(api_key=api_key)
        self._breeze.generate_session(
            api_secret=api_secret,
            session_token=session_token,
        )

    def get_client(self) -> BreezeConnect:
        return self._breeze
