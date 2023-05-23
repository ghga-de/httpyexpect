#!/usr/bin/env python3

# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Updates the HTTP Exception JSON schema from the corresponding pydantic model.
"""

import json
import os
import sys
from pathlib import Path
from typing import Mapping, Sequence

import typer
from pydantic import BaseModel

from httpyexpect.models import HttpExceptionBody

REPO_ROOT_DIR = Path(__file__).parent.parent.resolve()
JSON_SCHEMA_PATH = REPO_ROOT_DIR / "json_schemas" / "http_exception.json"


def pretty_format_json(
    contents: str,
    indent: int = 2,
    ensure_ascii: bool = True,
    sort_keys: bool = True,
    top_keys: Sequence[str] = (),
) -> str:
    """This has been copied from the pre-commit-hooks library:
    https://github.com/pre-commit/pre-commit-hooks/blob/8f6152921e65fe1a82bc475cafb721bd525ba5df/pre_commit_hooks/pretty_format_json.py#L11-L30
    """

    def pairs_first(pairs: Sequence[tuple[str, str]]) -> Mapping[str, str]:
        before = [pair for pair in pairs if pair[0] in top_keys]
        before = sorted(before, key=lambda x: top_keys.index(x[0]))
        after = [pair for pair in pairs if pair[0] not in top_keys]
        if sort_keys:
            after.sort()
        return dict(before + after)

    json_pretty = json.dumps(
        json.loads(contents, object_pairs_hook=pairs_first),
        indent=indent,
        ensure_ascii=ensure_ascii,
    )
    return f"{json_pretty}\n"


class ValidationError(RuntimeError):
    """Thrown when the JSON schema doesn't match the pydantic model."""

    def __init__(self):
        """Initializes the exception with a description."""
        message = "The JSON schema is not up to date with the provided model."
        super().__init__(message)


def json_schema_from_model(model: type[BaseModel]) -> str:
    """Generate a JSON schema object from pydantic model.

    Args:
        model:
            Pydantic model to derive the JSON schema from.

    Returns:
        A JSON schema object.
    """
    raw_json = model.schema_json(indent=2)
    return pretty_format_json(raw_json)


def updates_json_schema(schema_path: Path, model: type[BaseModel]):
    """Updates a JSON schema file generated from pydantic model.

    Args:
        schema_path:
            Path to the file containing the JSON schema.
        model:
            Pydantic model to derive the JSON schema from.
    """
    json_schema = json_schema_from_model(model)

    if os.path.exists(schema_path):
        os.remove(schema_path)

    with open(schema_path, "w", encoding="utf8") as file:
        file.write(json_schema)


def check_json_schema(schema_path: Path, model: type[BaseModel]):
    """Checks if the provided JSON schema is up to date with the pydantic model.

    Args:
        schema_path:
            Path to the file containing the JSON schema.
        model:
            Pydantic model to derive the JSON schema from.

    Raises:
        ValidationError: If the check fails.
    """
    expected_schema = json_schema_from_model(model)

    with open(schema_path, "r", encoding="utf8") as file:
        observed_schema = file.read()

    if not expected_schema == observed_schema:
        raise ValidationError()


def main(
    check: bool = typer.Option(
        False, help="Only checks if the JSON schema is up to date."
    ),
):
    """
    Updates the HTTP Exception JSON schema from the corresponding pydantic model.
    """

    if check:
        try:
            check_json_schema(schema_path=JSON_SCHEMA_PATH, model=HttpExceptionBody)
        except ValidationError as error:
            typer.secho(str(error), fg=typer.colors.RED)
            sys.exit(1)
        typer.secho("The JSON schema is up to date.", fg=typer.colors.GREEN)
    else:
        updates_json_schema(schema_path=JSON_SCHEMA_PATH, model=HttpExceptionBody)
        typer.secho("Successfully updated the JSON schema.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(main)
