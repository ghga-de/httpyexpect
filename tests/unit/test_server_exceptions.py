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

from httpyexpect.models.http_exception import HttpExceptionBody  # type: ignore
from httpyexpect.server import HTTPException


def test_httpexception():
    """Tests the interface and behavior of HTTPException instances."""

    # example params for an http exception
    status_code = 400
    body = HttpExceptionBody(
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
