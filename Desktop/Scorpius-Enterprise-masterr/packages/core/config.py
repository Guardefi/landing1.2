"""Core configuration module"""


class Config:
    """Basic configuration class"""

    def __init__(self):
        self.values = {}

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value


def get_config():
    """Get default configuration"""
    return Config()
