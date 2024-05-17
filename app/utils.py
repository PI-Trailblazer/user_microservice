from pathlib import Path
from pydantic import model_validator
import json
from typing import Any

# DO NOT MOVE THIS FILE
ROOT_DIR = Path(__file__).resolve().parents[1]


class ValidateFromJson:
    """Validates schemas that are stringified.

    This is useful to validate requests with a form data containing an image
    file and a schema stringified.
    """

    @model_validator(mode="before")
    @classmethod
    def load_from_json(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data
        return json.loads(data)
