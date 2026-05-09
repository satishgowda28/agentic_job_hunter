from typing import Type, TypeVar

from anthropic.types import Message
from pydantic import BaseModel

from utils import core

T = TypeVar("T", bound=BaseModel)


def extract_and_validate(message: Message, model: Type[T]) -> T | None:
    for block in message.content:
        if block.type == "text":
            raw_json = core.extract_json(block.text)
            if raw_json:
                return model.model_validate(raw_json)
    return None
