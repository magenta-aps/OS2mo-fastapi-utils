# SPDX-FileCopyrightText: 2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Optional
from typing import Set
from uuid import UUID

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Extra


class RealmAccess(BaseModel):
    roles: Set[str] = set()


class Token(BaseModel):
    azp: str
    email: Optional[EmailStr]
    preferred_username: Optional[str]
    realm_access: RealmAccess = RealmAccess(roles=set())
    uuid: Optional[UUID]

    class Config:
        extra = Extra.ignore
