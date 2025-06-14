# llm.py
import os
from typing import TypeVar, Optional, Union, Type, overload, cast
from logging import Logger

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def get_llm() -> BaseLanguageModel:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise RuntimeError("OPENAI_API_KEY is missing")
    return ChatOpenAI(
        model="o4-mini-2025-04-16",
        temperature=1,
        api_key=api_key,  # type: ignore
    )


@overload
def call_llm(
    prompt: str,
    llm: BaseLanguageModel,
    logger: Logger,
    model_class: None = None,
) -> str: ...


@overload
def call_llm(
    prompt: str,
    llm: BaseLanguageModel,
    logger: Logger,
    model_class: Type[T],
) -> T: ...


def call_llm(
    prompt: str,
    llm: BaseLanguageModel,
    logger: Logger,
    model_class: Optional[Type[T]] = None,
) -> Union[str, T]:
    """
    Call LLM with optional structured output.

    - If `model_class` is None, returns raw string.
    - If `model_class` is provided, returns an instance of that BaseModel.
    """
    try:
        if model_class is not None:
            logger.debug(f"Calling LLM with structured output: {model_class}")
            structured = llm.with_structured_output(model_class)
            result = structured.invoke(prompt)
            logger.debug(f"Structured LLM response: {result}")
            return cast(T, result)
        else:
            logger.debug("Calling LLM for raw string output.")
            response = llm.invoke(prompt)
            logger.debug(f"Raw LLM response: {response.content}")
            return response.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}, prompt: {prompt}, model: {model_class}")
        raise


def call_llm_structured(
    prompt: str,
    model_class: Type[T],
    llm: BaseLanguageModel,
    logger: Logger,
) -> T:
    """
    Convenience wrapper: always structured.
    """
    return call_llm(prompt, llm, logger, model_class)
