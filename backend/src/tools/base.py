from pydantic.json_schema import model_json_schema
from pathlib import Path
from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, ValidationError
from .tool_types import ToolKind, ToolResult, ToolConfirmation, ToolInvocation

class Tool(ABC):
    name: str = "base_tool"
    description: str = "Base tool"
    kind: ToolKind = ToolKind.READ

    def __init__(self) -> None:
        pass

    @property
    def schema(self) -> dict[str, Any] | type["BaseModel"]:
        raise NotImplementedError("Tool must define schema property or class attribute")

    @abstractmethod
    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        pass

    def validate_params(self, params: dict[str, Any]) -> list[str]:
        schema = self.schema

        # check if schema is of type BaseModel (not MCP in this context)
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            try: 
                BaseModel(**params)
            except ValidationError as e:
                errors = []
                for error in e.errors():
                    field = ".".join(str(x) for x in error.get("loc", []))
                    msg = error.get("msg", "Validation error")
                    errors.append(f"Parameter '{field}': {msg}")
                
                return errors
            
            except Exception as e:
                return [str(e)]

        return []

    def is_mutating(self, params: dict[str, Any]) -> bool:
        return self.kind in {
            ToolKind.WRITE,
            ToolKind.NETWORK,
            ToolKind.MEMORY,
        }

    async def get_confirmation(self, invocation: ToolInvocation) -> ToolInvocation | None:
        if not self.is_mutating(invocation.params):
            return None
        
        return ToolConfirmation(
            tool_name=self.name,
            params=invocation.params,
            description=f"Execute {self.name}",
        )

    def to_openai_schema(self) -> dict[str, Any]:
        schema = self.schema
        #
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            json_schema = model_json_schema(schema, mode="serialization")

            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": 'object',
                    "properties": json_schema.get("properties", {}),
                    "required": json_schema.get("requried", [])
                }
            }
        
        if isinstance(schema, dict):
            result = {
                "name": self.name,
                "description": self.description
            }

            if "paramters" in schema:
                result["parameters"] = schema["parameters"]
            else:
                result["parameters"] = schema
            
            return result

        raise ValueError(f'Invalid schema type for tool {self.name}" {type(schema)}')