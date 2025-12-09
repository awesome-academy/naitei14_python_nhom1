import os
import json


def load_config():
    """Load configuration from a JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(
            f"Configuration file '{config_path}' not found.\n"
            "Please create a 'config.json' file in the PitchManager directory with the required settings, e.g.:\n"
            '{\n    "gmail_user": "your_email@gmail.com",\n    "app_password": "your_app_password"\n}')
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Malformed JSON in configuration file '{config_path}': {e}\n"
            "Please ensure 'config.json' contains valid JSON. Example:\n"
            '{\n    "gmail_user": "your_email@gmail.com",\n    "app_password": "your_app_password"\n}')


config = load_config()
EMAIL_HOST_USER_CONFIG = config['gmail_user']
EMAIL_HOST_PASSWORD_CONFIG = config['app_password']
