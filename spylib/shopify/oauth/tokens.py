from typing import Optional
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

from utils import HTTPClient
from auth import JWToken, JWTBaseModel

from ..config import conf


class OAuthJWT(JWTBaseModel):
    is_login: bool
    storename: str
    nonce: Optional[str] = None

    def encode(self) -> JWToken:
        data = {
            'is_login': self.is_login,
            'storename': self.storename,
            'nonce': self.nonce,
            'exp': (datetime.now() + timedelta(seconds=900)),
        }

        return JWToken.load(data=data)


async def _get_token(domain: str, code: str) -> dict:
    url = f'https://{domain}/admin/oauth/access_token'

    httpclient = HTTPClient()
    response = await httpclient.request(
        method='post',
        url=url,
        json={'client_id': conf.api_key, 'client_secret': conf.secret_key, 'code': code},
    )
    if response.status_code != 200:
        raise RuntimeError('Couldn\'t get access token')

    jresp = response.json()

    return jresp


class OfflineToken(BaseModel):
    access_token: str
    scope: List[str]

    @classmethod
    async def get(cls, domain: str, code: str):
        jsontoken = await _get_token(domain=domain, code=code)
        return cls(**jsontoken)


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
