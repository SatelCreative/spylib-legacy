from typing import Optional
from typing import List
from pydantic import BaseModel, validator
from loguru import logger

from spylib.utils import HTTPClient
from spylib.auth import JWTBaseModel

from .config import conf


class OAuthJWT(JWTBaseModel):
    is_login: bool
    storename: str
    nonce: Optional[str] = None


async def _get_token(domain: str, code: str) -> dict:
    url = f'https://{domain}/admin/oauth/access_token'

    httpclient = HTTPClient()

    jsondata = ({'client_id': conf.api_key, 'client_secret': conf.secret_key, 'code': code},)
    response = await httpclient.request(
        method='post',
        url=url,
        json=jsondata,
    )
    if response.status_code != 200:
        message = f'Problem retrieving access token. Status code: {response.status_code}'
        logger.error(message)
        raise ValueError(message)

    jresp = response.json()

    return jresp


class OfflineToken(BaseModel):
    access_token: str
    scope: List[str]

    @classmethod
    async def get(cls, domain: str, code: str):
        logger.debug(f'Retrieve {cls.__name__} for shop {domain}')
        jsontoken = await _get_token(domain=domain, code=code)
        return cls(**jsontoken)

    @validator('scope', pre=True, always=True)
    def set_id(cls, fld):
        return fld.split(',')


class AssociatedUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    email_verified: bool
    account_owner: bool
    locale: str
    collaborator: bool


class OnlineToken(OfflineToken):
    expires_in: int
    associated_user_scope: List[str]
    associated_user: AssociatedUser

    @validator('associated_user_scope', pre=True, always=True)
    def set_id(cls, fld):
        return fld.split(',')
