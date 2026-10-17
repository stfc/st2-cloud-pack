from pathlib import Path
import yaml

def read_config_file(key=None):
    # .parents[0] = utils/
    # .parents[1] = apis/
    # .parents[2] = lib/
    BASE_DIR = Path(__file__).resolve().parents[2]
    conf_path = BASE_DIR / "workflows" / "etc" / "config"

    with open(conf_path) as f:
        data = yaml.safe_load(f)

    # If no argument is passed (or None), return the entire dictionary
    if key is None:
        return data

    # If a key is passed, check for it and raise a KeyError if missing
    if key in data:
        return data[key]
    else:
        raise KeyError(f"Configuration key '{key}' not found in '{conf_path}'.")
