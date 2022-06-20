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

"""Logic to translate responses to HTTP calls to python exceptions."""

from typing import Optional

import requests

from httpyexpect.client.mapping import ExceptionMapping


class ResponseTranslator:
    """Translates a specific response to an HTTP call using an ExceptionMapping to
    python exceptions (in case of an error code)."""

    def __init__(self, response: requests.Response, *, exception_map: ExceptionMapping):
        """Initialize the translator.

        Args:
            response:
                A response to an HTTP call performed with the `requests` library.
            exception_map:
                An exception mapping specifying translations between status codes plus
                exception IDs and python exceptions.
        """

        self._response = response
        self._exception_map = exception_map

    def _validate_response(self, response: requests.Response):
        """Validates a response according to the"""
        print(response)
        return response

    def get_error(self, *, response: requests.Response) -> Optional[Exception]:
        """In case the provided response corresponds to an error, it will translated
        and returnd as a python exception according to the mapping.
        Please note, this function will only return exceptions but not raise them.

        Args:
            response:
                A response obtained from an http call using the `requests` library.

        Returns:
            A python exception in case of an HTTP error, `None` otherwise.
        """
        print(response)
        return response
