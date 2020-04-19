from typing import NamedTuple


class ProfileTuple(NamedTuple):
    name: str
    region: str
    role_arn: str = None
    source_profile: str = None
    is_default: bool = False
    aws_access_key_id: str = None
    aws_secret_access_key: str = None

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}('
                f'{self.name!r}, {self.region!r}, {self.role_arn!r}, {self.source_profile!r}, {self.is_default!r}, {self.aws_access_key_id!r}, {self.aws_secret_access_key!r})')


class CredentialTuple(NamedTuple):
    name: str
    aws_access_key_id: str = None
    aws_secret_access_key: str = None

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}('
                f'{self.name!r}, {self.aws_access_key_id!r}, {self.aws_secret_access_key!r})')
