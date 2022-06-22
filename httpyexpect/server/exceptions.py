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

"""Exception Base models used across all servers."""

import pydantic

from httpyexpect.base_exception import HttpyExpectError
from httpyexpect.models import HTTPExceptionBody
from httpyexpect.validation import ValidationError, assert_error_code


class HTTPException(HttpyExpectError):
    """A generic exception model that can be translated into an HTTP response according
    to the httpyexpect exception schema.
    """

    def __init__(
        self, *, status_code: int, exception_id: str, description: str, data: dict
    ):
        """Initialize the error with the required metadata.

        Args:
            status_code:
                The response code of the HTTP response to send.
            exception_id:
                An identifier used to distinguish between different exception causes in
                a preferably fine-grained fashion. The distinction between causes should
                be made from the perspective of the server/service raising the exception
                (and not from the client perspective). Needs to be camel case formatted
                and 3-40 character in length.
            description:
                A human readable message to the client explaining the cause of the
                exception.
            data:
                An object containing further details on the exception cause in a machine
                readable way.  All exceptions with the same exceptionId should use the
                same set of properties here. This object may be empty (in case no data
                is required)"
        """

        assert_error_code(status_code)
        self.status_code = status_code

        # prepare a body that is validated against the httpyexpect schema:
        try:
            self.body = HTTPExceptionBody(
                exceptionId=exception_id, description=description, data=data
            )
        except pydantic.ValidationError as error:
            raise ValidationError from error

        super().__init__(description)
