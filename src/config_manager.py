import json
import os
from typing import Optional
from models import ConversationHealthConfig


class ConversationHealthConfigManager:
    def __init__(self, config_file_path: str = "config.json"):
        self.config_file_path = config_file_path
        self._loaded_config: Optional[ConversationHealthConfig] = None

    def load_configuration(self) -> ConversationHealthConfig:
        if self._loaded_config is not None:
            return self._loaded_config

        if not os.path.exists(self.config_file_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file_path}"
            )

        with open(self.config_file_path, "r") as f:
            raw_config_data = json.load(f)

        self._loaded_config = ConversationHealthConfig.model_validate(raw_config_data)
        return self._loaded_config

    def get_configuration(self) -> ConversationHealthConfig:
        if self._loaded_config is None:
            return self.load_configuration()
        return self._loaded_config


def create_config_manager(
    config_file_path: str = "config.json",
) -> ConversationHealthConfigManager:
    return ConversationHealthConfigManager(config_file_path)
