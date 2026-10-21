# pylint: disable=no-else-return
from pathlib import Path
import yaml


def read_config_file(key=None):
    """
    returns the content of the configuration file
    The path of the file is assumed to be
        lib/workflows/etc/config

    * If not argument is passed, the entire file is returned
    * If a key is passed as argument, then only the corresponding
      value from the configuration is returned

    NOTE: the keys are expected to be upper case in the config file
    """
    # To read the configuration file we need first to
    # resolve its relative path:
    #   The path to this file is
    #         lib/apis/utils/
    #   while the configuration file to read is
    #         lib/workflows/etc/config
    #   so the relative path of the configuration file
    #   from here is:
    #         ../../../lib/workflows/etc/config
    # .parents[0] = ".."
    # .parents[1] = "../.."
    # .parents[2] = "../../.."
    base_dir = Path(__file__).resolve().parents[2]
    conf_path = base_dir / "workflows" / "etc" / "config"

    with open(conf_path, "r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file)

    # If no argument is passed (or None), return the entire dictionary
    if key is None:
        return data

    # If a key is passed, check for it and raise a KeyError if missing
    key = key.upper()  # the keys are always upper case in the config file
    if key in data:
        return data[key]
    else:
        raise KeyError(f"Configuration key '{key}' not found in '{conf_path}'.")
