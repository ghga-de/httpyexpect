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

"""Test the base exception for servers."""

import pytest

from httpyexpect.models import HTTPExceptionBody
from httpyexpect.server import HTTPException
from httpyexpect.validation import ValidationError


def test_httpexception():
    """Tests the interface and behavior of HTTPException instances."""

    # example params for an http exception
    status_code = 400
    body = HTTPExceptionBody(
        exceptionId="testException",
        description="This is a test exception.",
        data={"test": "test"},
    )

    # create an exception:
    exception = HTTPException(
        status_code=status_code,
        exception_id=body.exceptionId,
        description=body.description,
        data=body.data,
    )

    # check public attributes:
    assert exception.body == body
    assert exception.status_code == status_code

    # check error message:
    assert str(exception) == body.description


@pytest.mark.parametrize(
    "status_code, exception_id, description, data",
    [
        # invalid status codes:
        (200, "myValidExceptionID", "A valid description", {"valid": "data"}),
        (600, "myValidExceptionID", "A valid description", {"valid": "data"}),
        # invalid exception id:
        (400, "123myInvalidExceptionID", "A valid description", {"valid": "data"}),
        (400, "myInvalidExcßeptionID", "A valid description", {"valid": "data"}),
        # invalid data:
        (400, "myValidExceptionID", "A valid description", 123),
    ],
)
def test_httpexception_invalid_params(
    status_code: object, exception_id: object, description: object, data: object
):
    """Tests creating an HTTPException with invalid params."""

    with pytest.raises(ValidationError):
        HTTPException(
            status_code=status_code,  # type: ignore
            exception_id=exception_id,  # type: ignore
            description=description,  # type: ignore
            data=data,  # type: ignore
        )
