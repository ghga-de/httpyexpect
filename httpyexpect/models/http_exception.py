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

################################################################################
###  PLEASE NOTE: This file was autogenerated. Please do not edit manually.  ###
################################################################################

# Ignore this autogenerated files from linting:
# pylint: skip-file
# flake8: noqa
# type: ignore

# generated by datamodel-codegen:
#   filename:  http_exception.json

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Extra, Field, constr


class HttpException(BaseModel):
    """
    An opinionated schema for the response shipped with HTTP exception (non 2xx status codes).
    """

    class Config:
        extra = Extra.forbid

    description: str = Field(
        ...,
        description="A human readable message to the client explaining the cause of the exception.",
    )
    data: Dict[str, Any] = Field(
        ...,
        description="An object containing further details on the exception cause in a machine readable way. Even though this general exception schema does not specify the internal shape of the details object, all exceptions with the same exceptionId should use the same set of properties. This object may be empty (in case no details are required)",
    )
    exceptionId: constr(regex=r"^[a-z][a-zA-Z0-9]{2,39}$") = Field(
        ...,
        description="A itendifier used to distinguish between different exception causes in a preferably fine-grained fashion. The distinction between causes should be made from the perspective of the server/service raising the exception (an not from the client perspective). Needs to be camel case formatted and 3-40 character in length.",
    )
