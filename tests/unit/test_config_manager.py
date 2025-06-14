import pytest
from unittest.mock import patch, mock_open
from config_manager import ConversationHealthConfigManager


def test_valid_config_loading(valid_config_json):
    """Test loading valid JSON config"""
    with patch("builtins.open", mock_open(read_data=valid_config_json)):
        with patch("os.path.exists", return_value=True):  # Mock file exists
            manager = ConversationHealthConfigManager("test_config.json")
            config = manager.get_configuration()

            assert config is not None
            assert "sentiment" in config.evaluation_criteria


def test_invalid_json_handling(invalid_config_json):
    """Test handling of invalid JSON"""
    with patch("builtins.open", mock_open(read_data=invalid_config_json)):
        with patch("os.path.exists", return_value=True):
            with pytest.raises(Exception):  # Should raise JSON decode error
                manager = ConversationHealthConfigManager("test_config.json")
                manager.get_configuration()
