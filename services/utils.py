import yaml
import tomli # Cần cài thư viện này để đọc file toml: pip install tomli

def load_config(config_path="config/config.yaml"): # Đổi tên thành config.yaml cho khớp
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_credentials(secrets_path="config/secrets.toml"):
    with open(secrets_path, "rb") as f:
        secrets = tomli.load(f)
        return secrets["auth"]