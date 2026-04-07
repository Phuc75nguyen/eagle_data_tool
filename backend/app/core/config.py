import os
import yaml
try:
    import tomli as toml # python 3.10 and below
except ImportError:
    import toml # if native toml is installed, though 3.11 has tomllib

def get_config_path(filename: str) -> str:
    # __file__ is backend/app/core/config.py
    # os.path.dirname(__file__) is backend/app/core
    # Để ra đến thư mục gốc eagle_dataTool (cùng cấp với backend), ta lùi 3 bước:
    # /core -> /app -> /backend -> eagle_dataTool/config/
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    return os.path.join(root_dir, "config", filename)

def load_config():
    config_path = get_config_path("config.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Không tìm thấy file config tại: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_credentials():
    secrets_path = get_config_path("secrets.toml")
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Không tìm thấy file secrets tại: {secrets_path}")
    with open(secrets_path, "rb") as f:
        secrets = toml.load(f)
        return secrets.get("auth", {})
