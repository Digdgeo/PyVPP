# pyvpp/config.py
import os
from pathlib import Path

try:
    import tomllib  # py>=3.11
except ModuleNotFoundError:
    import tomli as tomllib


def load_cdse_credentials(user=None, password=None):

    # 1. Argumentos explícitos
    if user and password:
        return user, password

    # 2. Variables de entorno
    env_user = os.getenv("CDSE_USER")
    env_pass = os.getenv("CDSE_PASSWORD")
    if env_user and env_pass:
        return env_user, env_pass

    # 3. Archivo config local
    cfg = Path.home() / ".pyvpp" / "config.toml"
    if cfg.exists():
        with open(cfg, "rb") as f:
            data = tomllib.load(f)
        return data["cdse"]["user"], data["cdse"]["password"]

    raise RuntimeError(
        "CDSE credentials not found.\n"
        "Set CDSE_USER/CDSE_PASSWORD or ~/.pyvpp/config.toml"
    )

