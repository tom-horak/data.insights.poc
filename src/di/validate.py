"""Validace vstupních dat proti JSON schématu agenta."""

from __future__ import annotations

import jsonschema


def validate_input(data: dict, schema: dict | None) -> None:
    if schema is None:
        return
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        raise ValueError(f"Neplatný vstup na '{path}': {e.message}") from e
