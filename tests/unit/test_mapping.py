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

"""Test the mapping module."""

from contextlib import nullcontext

import pytest

from httpyexpect.client.custom_types import (
    ExceptionFactory,
    ExceptionFactoryParam,
    ExceptionMappingSpec,
)
from httpyexpect.client.mapping import ExceptionMapping, ValidationError


class TestException(RuntimeError):
    """A exception return or thrown as part of a test."""

    def __init__(self):
        """Initialize without args."""
        super().__init__()


class TestExceptionWithArgs(RuntimeError):
    """A exception return or thrown as part of a test."""

    def __init__(
        self, status_code: int, exception_id: str, description: str, data: dict
    ):
        """Initialize the error with the required metadata."""
        super().__init__()


@pytest.mark.parametrize(
    "spec, is_valid",
    [
        # a spec containing multiple valid scenarios:
        (
            {
                400: {
                    "myTestException0": lambda status_code, exception_id, description, data: TestException(),
                    "myTestException1": lambda exception_id, description, data: TestException(),
                    "myTestException2": lambda status_code, data: TestException(),
                },
                403: {
                    "myTestException3": lambda exception_id, description: TestException(),
                    "myTestException4": lambda exception_id, data: TestException(),
                },
                404: {
                    "myTestException5": lambda description, data: TestException(),
                    "myTestException6": lambda exception_id: TestException(),
                },
                427: {
                    "myTestException7": lambda description: TestException(),
                    "myTestException8": lambda data: TestException(),
                    "myTestException9": lambda status_code: TestException(),
                },
                500: {
                    "myTestException10": lambda: TestException(),
                    "myTestException11": TestException,
                    "myTestException12": TestExceptionWithArgs,
                },
            },
            True,
        ),
        # invalid status codes:
        (
            {-100: {"myTestException": lambda exception_id: TestException()}},
            False,
        ),
        (
            {100: {"myTestException": lambda exception_id: TestException()}},
            False,
        ),
        (
            {200: {"myTestException": lambda exception_id: TestException()}},
            False,
        ),
        (
            {300: {"myTestException": lambda exception_id: TestException()}},
            False,
        ),
        (
            {600: {"myTestException": lambda exception_id: TestException()}},
            False,
        ),
        # invalid exception ids:
        (
            {400: {"myTeßtException": lambda exception_id: TestException()}},
            False,
        ),
        (
            {400: {"1myTestException": lambda exception_id: TestException()}},
            False,
        ),
        (
            {400: {"mt": lambda exception_id: TestException()}},
            False,
        ),
        # invalid exception factories:
        (
            {400: {"myTestException": TestException()}},
            False,
        ),
        (
            {400: {"myTestException": 123}},
            False,
        ),
        # spec is not a mapping:
        (
            {400: lambda exception_id: TestException()},
            False,
        ),
        # exception factory has unexpected parameters:
        (
            {400: {"myTestException": lambda foo: TestException()}},
            False,
        ),
        (
            {400: {"myTestException": lambda exception_id, foo: TestException()}},
            False,
        ),
        (
            {400: {"myTestException": lambda exception_id, foo="foo": TestException()}},
            False,
        ),
        # exception factory uses variadic args/kwargs (e.g. *arg **kwargs):
        (
            {400: {"myTestException": lambda exception_id, *foo: TestException()}},
            False,
        ),
        (
            {400: {"myTestException": lambda exception_id, **bar: TestException()}},
            False,
        ),
        (
            {400: {"myTestException": RuntimeError}},
            False,
        ),
        # exception factory with wrong parameter orders:
        (
            {
                400: {
                    "myTestException": lambda exception_id, status_code: TestException()
                }
            },
            False,
        ),
        (
            {400: {"myTestException": lambda data, description: TestException()}},
            False,
        ),
    ],
)
def test_exception_mapping_validation(spec: ExceptionMappingSpec, is_valid: bool):
    """Test the ExceptionMappingSpec validation behavior of the ExceptionMapping
    class."""

    with nullcontext() if is_valid else pytest.raises(ValidationError):  # type: ignore
        ExceptionMapping(spec)


@pytest.mark.parametrize(
    "fallback_factory, is_valid",
    [
        (lambda status_code, exception_id, description, data: TestException(), True),
        (lambda status_code, data: TestException(), True),
        (TestExceptionWithArgs, True),
        (123, False),
        (lambda foo: TestException(), False),
        (lambda data, description: TestException(), False),
    ],
)
def test_fallback_factory_validation(fallback_factory: object, is_valid: bool):
    """Test the ExceptionMappingSpec behavior for validating fallback factories."""

    with nullcontext() if is_valid else pytest.raises(ValidationError):  # type: ignore
        ExceptionMapping({}, fallback_factory=fallback_factory)  # type: ignore


@pytest.mark.parametrize(
    "factory, expected_params",
    [
        (
            lambda status_code, exception_id, description, data: TestException(),
            ["status_code", "exception_id", "description", "data"],
        ),
        (lambda status_code, data: TestException(), ["status_code", "data"]),
        (lambda: TestException(), []),
    ],
)
def test_get_factory_kit(
    factory: ExceptionFactory, expected_params: list[ExceptionFactoryParam]
):
    """Test the `get_factory_kit` method of the `ExceptionMapping` class."""

    # build a spec around the provided factory:
    status_code = 400
    exception_id = "myTestException"
    spec = {status_code: {exception_id: factory}}

    # create an ExceptionMapping and get a factory kit:
    mapping = ExceptionMapping(spec)
    factory_kit = mapping.get_factory_kit(
        status_code=status_code, exception_id=exception_id
    )

    # check the returned FactoryKit:
    assert factory_kit.factory == factory
    assert factory_kit.required_params == expected_params


def test_get_factory_kit_not_existent():
    """Test the `get_factory_kit` method of the `ExceptionMapping` class
    when called with parameters that don't resolve to a mapping."""
    fallback_factory = lambda status_code, data: TestException()
    expected_params = ["status_code", "data"]

    # create an ExceptionMapping and get a factory kit:
    mapping = ExceptionMapping(spec={}, fallback_factory=fallback_factory)
    factory_kit = mapping.get_factory_kit(
        status_code=400, exception_id="myTestException"
    )

    # check the returned FactoryKit:
    assert factory_kit.factory == fallback_factory
    assert factory_kit.required_params == expected_params
