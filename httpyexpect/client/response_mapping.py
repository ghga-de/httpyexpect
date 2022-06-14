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

"""This module provides functionality for working with response mappings.
A response mapping is a datastructure that maps a non-2xx HTTP response to a python
exception.
"""

from typing import Any, Callable, Mapping, Union

from httpyexpect.base_exception import HttpyExpectError

# Defining a type alias for dict-based represenations of mappings.:
ResponseMappingSpec = Mapping[
    int,  # Corresponds to HTTP status codes.
    Mapping[
        str,  # Corresponds to exceptionIds (as per the httpyexpect schema)
        Union[
            # An exception class that takes a message as its only argument:
            type[Exception],
            # Or a Callable without arguments that returns an exception instance:
            Callable[[], Exception],
            # Or a Callable that takes data (as per the httpyexpect schema) as arguments
            # and returns an exception instance:
            Callable[[dict[str, Any]], Exception],
            # Or a Callable that takes an exceptionId, a description, and data
            # (as per the httpyexpect schema) as arguments and returns an exception
            # instance:
            Callable[[str, str, dict[str, Any]], Exception],
        ],
    ],
]


class ValidationError(HttpyExpectError):
    """Thrown when a response mapping spec failed validation."""


class ResponseMapping:
    """
    A datastructure that maps a non-2xx HTTP response to a python exception.
    It will except a dict-based specification defining the mapping as input.
    This spec will be validated and translated into a set of public attributes and
    methods that helps to interact with this response mapping.
    """

    def __init__(self, spec: ResponseMappingSpec):
        """
        Initialize with a dict-based specification of a response mappings.
        """
        self.spec = spec

    @staticmethod
    def _validate(spec: ResponseMappingSpec):
        """
        Validates a dict-based specification of a response mappings.

        Raises:
            ValidationError: if validation fails.
        """
        for status_code, exc_id_mapping in spec.items():
            # Check that the top level key is a valid status code:
            if not isinstance(status_code, int) or not 100 <= status_code < 600:
                raise ValidationError(
                    "Invalid status code detected, must be an integer >= 100 and < 600:"
                    + str(status_code)
                )

            # check that status code corresponds to an exception (non-2xx):
            if 200 <= status_code < 300:
                raise ValidationError(
                    "The provided status code corresponds to a success response but"
                    + f" expected a non-2xx error response: {status_code}"
                )

            if not isinstance(exc_id_mapping, Mapping):
                raise ValidationError(
                    f"The value provided for the {status_code} status code was not a"
                    + " dict (or python Mapping-compatible)."
                )

            for exc_id, exc_factory in exc_id_mapping.items():
                # check if the exc_id is valid
                print(exc_id)
                print(exc_factory)
