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

"""Client-side integration tests."""

from unittest.mock import Mock

import pytest

from httpyexpect.client import ExceptionMapping, ResponseTranslator
from httpyexpect.models import HttpExceptionBody


class ExceptionA(RuntimeError):
    """An Exception."""


class ExceptionB(RuntimeError):
    """Another Exception"""


class ExceptionC(RuntimeError):
    """Yet, another Exception"""


@pytest.mark.parametrize(
    "status_code, body, expected_exception",
    [
        (
            400,
            HttpExceptionBody(
                exception_id="testA", description="test", data={"test": "test"}
            ),
            ExceptionA,
        ),
        (
            400,
            HttpExceptionBody(
                exception_id="testB", description="test", data={"test": "test"}
            ),
            ExceptionB,
        ),
        (
            500,
            HttpExceptionBody(
                exception_id="testC", description="test", data={"test": "test"}
            ),
            ExceptionC,
        ),
    ],
)
def test_typical_client_usage(
    status_code: int, body: HttpExceptionBody, expected_exception: type[Exception]
):
    """Test the typical way how the client may use the `ResponseTranslator` together
    with the `ExceptionMapping` classes."""
    spec = {
        400: {
            "testA": lambda exception_id, description, data: ExceptionA(),
            "testB": lambda data: ExceptionB(),
        },
        500: {"testC": lambda: ExceptionC()},
    }

    # create http response mock:
    response = Mock()
    response.status_code = status_code
    response.json.return_value = body.dict()

    # create a exception mapping:
    exception_map = ExceptionMapping(spec)

    # initialize the ResponseTranslator:
    translator = ResponseTranslator(response, exception_map=exception_map)

    # translate and get the python exception object:
    obtained_exception = translator.get_error()
    assert isinstance(obtained_exception, expected_exception)

    # translate into python exception and raise it:
    with pytest.raises(expected_exception):
        translator.raise_for_error()
