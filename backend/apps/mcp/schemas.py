from typing import Any

from pydantic import BaseModel


class ToolDescriptor(BaseModel):
    name: str
    description: str | None
    input_schema: dict[str, Any]
