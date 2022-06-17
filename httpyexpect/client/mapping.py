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

"""This module provides functionality for working with exception mappings.
A exception mapping is a datastructure that maps an HTTP error response (4xx or 5xx)
to a python exception.
"""

import inspect
import re
from typing import Callable, Mapping, Optional

from httpyexpect.client.exceptions import UnexpectedError, ValidationError
from httpyexpect.models import EXCEPTION_ID_PATTERN

EXCEPTION_FACTORY_PARAMS = ("status_code", "exception_id", "description", "data")

# Defining a type aliases for describing an exception mapping spec:
StatusCode = int
ExceptionId = str
ExceptionFactory = Callable[..., Exception]
ExceptionMappingSpec = Mapping[StatusCode, Mapping[ExceptionId, ExceptionFactory]]


class ExceptionMapping:
    """
    A datastructure that maps an HTTP response (4xx or 5xx) to a python exception.
    It will except a dict-based specification defining the mapping as input.
    This spec will be validated and translated into a set of public attributes and
    methods that helps to interact with this exception mapping.
    """

    def __init__(
        self,
        spec: ExceptionMappingSpec,
        *,
        fallback_factory: ExceptionFactory = UnexpectedError,
    ):
        """
        Initialize with a dict-based specification of a exception mappings.
        """

        self._spec = spec
        self._fallback_factory = fallback_factory

        self._validate(self._spec)
        try:
            self._check_exception_factory(fallback_factory)
        except ValidationError as error:
            raise ValidationError("Invalid fallback factory.") from error

    @staticmethod
    def _check_status_code(status_code: object) -> None:
        """Check that the provided status code corresponds to a valid error code."""
        if not isinstance(status_code, int) or not 400 <= status_code < 600:
            raise ValidationError(
                "The status codes must correspond to HTTP exception (4xx or 5xx),"
                + f" obtained: {status_code}"
            )

    @staticmethod
    def _check_exception_id_mapping(
        exc_id_mapping: object,
        *,
        status_code: int,
    ) -> None:
        """Check that exception id mapping provided per status code is a valid python
        Mapping."""
        if not isinstance(exc_id_mapping, Mapping):
            raise ValidationError(
                f"The value provided for the {status_code} status code was not a"
                + " dict (or python Mapping-compatible)."
            )

    @staticmethod
    def _check_exception_id(
        exception_id: object,
        *,
        status_code: int,
    ) -> None:
        """Check the format of an exception id."""
        if not isinstance(exception_id, str) or not re.match(
            EXCEPTION_ID_PATTERN, exception_id
        ):
            raise ValidationError(
                "The exception ID must be a string formatted according to the regex"
                + f"{EXCEPTION_ID_PATTERN}, however, for the status code {status_code},"
                + f" the following was obtained: {exception_id}"
            )

    @staticmethod
    def _check_exception_factory(
        exception_factory: object,
        *,
        exception_id: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        """Check the signature of an exception factory."""

        error_intro = (
            (
                "The exception factory provided for the exception id"
                + f" {exception_id} within the status code {status_code}"
            )
            if exception_id and status_code
            else "The provided exception factory"
        )

        if not callable(exception_factory):
            raise ValidationError(f"{error_intro} was not callable.")

        try:
            factory_signature = inspect.signature(exception_factory)
        except ValueError:
            factory_signature = inspect.signature(exception_factory.__call__)

        # check for the expected paramters:
        for param in factory_signature.parameters.values():
            if param.kind in {
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            }:
                # ignoring variadic argument or keyword arguments (e.g. *args
                # or **kwargs)
                raise ValidationError(
                    f"{error_intro} had variadic argument or keyword arguments (e.g. *args or"
                    + " **kwargs) which are not allowed."
                )

            if param.name not in EXCEPTION_FACTORY_PARAMS:
                raise ValidationError(
                    f"{error_intro} has an unexpected parameter (expected one or"
                    + f" multiple of [{','.join(EXCEPTION_FACTORY_PARAMS)}] in that"
                    + f" order):{param.name}"
                )

        # check parameter order:
        observed_params = list(factory_signature.parameters.keys())
        filtered_expected_params = [
            param for param in EXCEPTION_FACTORY_PARAMS if param in observed_params
        ]
        if observed_params != filtered_expected_params:
            raise ValidationError(
                f"{error_intro} had the wrong order, expected"
                + f" [{','.join(filtered_expected_params)}], but obtained:"
                + f"[{','.join(observed_params)}]"
            )

    @classmethod
    def _validate(cls, spec: ExceptionMappingSpec):
        """
        Validates a dict-based specification of a exception mappings.

        Raises:
            ValidationError: if validation fails.
        """
        for status_code, exc_id_mapping in spec.items():
            cls._check_status_code(status_code)
            cls._check_exception_id_mapping(exc_id_mapping, status_code=status_code)

            for exception_id, exception_factory in exc_id_mapping.items():
                cls._check_exception_id(exception_id, status_code=status_code)
                cls._check_exception_factory(
                    exception_factory,
                    exception_id=exception_id,
                    status_code=status_code,
                )
