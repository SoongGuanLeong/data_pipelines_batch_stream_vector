import yaml
from pathlib import Path


def load_config(folder="../configs"):
    config = {}
    folder_path = Path(folder)
    for file in folder_path.glob("*.yaml"):
        with open(file, "r") as f:
            config[file.stem] = yaml.safe_load(f)
    return config
