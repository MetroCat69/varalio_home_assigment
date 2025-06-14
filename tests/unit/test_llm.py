import pytest
from unittest.mock import patch, Mock
from llm import get_llm, call_llm, call_llm_structured
from pydantic import BaseModel


class TestModel(BaseModel):
    response: str


def test_get_llm_with_api_key():
    """Test LLM creation with valid API key"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        llm = get_llm()
        assert llm is not None


def test_get_llm_missing_api_key():
    """Test LLM creation fails without API key"""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY is missing"):
            get_llm()


def test_call_llm_string_output(mock_llm, mock_logger):
    """Test LLM call returning string"""
    result = call_llm("test prompt", mock_llm, mock_logger)

    assert result == "Mock LLM response"
    mock_llm.invoke.assert_called_once_with("test prompt")


def test_call_llm_structured_output(mock_llm, mock_logger, mock_structured_response):
    """Test LLM call with structured output"""
    mock_llm.with_structured_output.return_value.invoke.return_value = (
        mock_structured_response
    )

    result = call_llm("test prompt", mock_llm, mock_logger, TestModel)

    assert result == mock_structured_response
    mock_llm.with_structured_output.assert_called_once_with(TestModel)


def test_call_llm_structured_convenience(
    mock_llm, mock_logger, mock_structured_response
):
    """Test convenience wrapper for structured calls"""
    mock_llm.with_structured_output.return_value.invoke.return_value = (
        mock_structured_response
    )

    result = call_llm_structured("test prompt", TestModel, mock_llm, mock_logger)

    assert result == mock_structured_response


def test_call_llm_error_handling(mock_llm, mock_logger):
    """Test LLM call error handling"""
    mock_llm.invoke.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        call_llm("test prompt", mock_llm, mock_logger)
