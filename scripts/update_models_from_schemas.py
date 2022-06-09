#!/usr/bin/env python3

# Copyright 2021 - 2022 Universität Tübingen, DKFZ and EMBL
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
Updates pydantic models located in the MODELS_DIR generated from JSON schemas located in
the SCHEMAS_DIR.
"""

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import typer

REPO_ROOT_DIR = Path(__file__).parent.parent.resolve()
SCHEMAS_DIR = REPO_ROOT_DIR / "json_schemas"
MODELS_DIR = REPO_ROOT_DIR / "httpyexpect" / "models"


class ValidationError(RuntimeError):
    """Thrown when the models don't match the JSON schemas."""

    def __init__(self):
        """Initializes the exception with a description."""
        message = "The provided models are not up to date with the JSON schemas."
        super().__init__(message)


def updates_models(schemas_dir: Path = SCHEMAS_DIR, models_dir: Path = MODELS_DIR):
    """Updates pydantic models generated from JSON schemas.

    Args:
        schemas_dir:
            Directory containing the source JSON schemas.
        models_dir:
            Directory to which the generated pydantic models will be dumped as a python
            package.
    """
    with subprocess.Popen(
        args=[
            "datamodel-codegen",
            "--use-schema-description",
            "--disable-timestamp",
            "--input",
            schemas_dir,
            "--output",
            models_dir,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) as process:
        exit_code = process.wait()
        assert exit_code == 0


def check_models(schemas_dir: Path = SCHEMAS_DIR, models_dir: Path = MODELS_DIR):
    """Checks whether pydantic models generated from JSON schemas are up to date.

    Args:
        schemas_dir:
            Directory containing the source JSON schemas.
        models_dir:
            Directory containing the pydantic models to check.

    Raises:
        ValidationError: If the check fails.
    """
    with TemporaryDirectory() as ref_dir:

        # create reference models:
        updates_models(schemas_dir=schemas_dir, models_dir=Path(ref_dir))

        # check wether the models_dir matches the reference:

        with subprocess.Popen(
            args=["diff", models_dir, ref_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) as process:
            exit_code = process.wait()
            if exit_code != 0:
                raise ValidationError()


def cli(
    schemas_dir: Path = typer.Argument(
        SCHEMAS_DIR, help="Directory containing the source JSON schemas."
    ),
    models_dir: Path = typer.Argument(
        MODELS_DIR, help="Directory containing the target pydantic models."
    ),
    check: bool = typer.Option(
        False, help="Only checks if the specified models are up to date."
    ),
):
    """
    Updates or check pydantic models to match the content of provided JSON schemas.
    """

    if check:
        check_models(schemas_dir=schemas_dir, models_dir=models_dir)
        typer.secho("The pydantic models are up to date.", fg=typer.colors.GREEN)
    else:
        updates_models(schemas_dir=schemas_dir, models_dir=models_dir)
        typer.secho("Successfully updated the pydantic models.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    typer.run(cli)
