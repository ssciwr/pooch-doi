from typing import List, Optional
import dataclasses
import enum


class LicenseIdentifierScheme(enum.Enum):
    SPDX = "spdx"
    URL = "url"
    OTHER = "other"


@dataclasses.dataclass
class LicenseIdentifier:
    scheme: LicenseIdentifierScheme
    value: str


class LicenseReferenceRole(enum.Enum):
    ICON = "icon"
    TEXT = "text"
    HOMEPAGE = "homepage"


@dataclasses.dataclass
class LicenseReference:
    role: LicenseReferenceRole
    uri: str


@dataclasses.dataclass
class License:
    name: str
    description: Optional[str] = None
    identifiers: List[LicenseIdentifier] = dataclasses.field(default_factory=list)
    references: List[LicenseReference] = dataclasses.field(default_factory=list)
