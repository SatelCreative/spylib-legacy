import jwt
from typing import Optional, Tuple
from abc import ABC
from datetime import datetime, timedelta
from pydantic import BaseModel, validator

from utils import conf as global_conf


class JWTBaseModel(BaseModel, ABC):
    """ Base class to manage JWT

    The pydantic model fields are the data content of the JWT.
    The default expiration (exp) is set to 900 seconds. Overwrite the ClassVar exp to change the
    expiration time.
    """
    exp: int = None  # type: ignore

    @validator('exp', pre=True, always=True)
    def set_id(cls, exp):
        return exp or (datetime.now() + timedelta(seconds=900))

    @classmethod
    def decode_token(cls, token: str, verify: bool = True):
        """ Decode the token and load the data content into an instance of this class

        Parameters
        ----------
        verify: If true, verify the signature is valid, otherwise skip. Default is True

        Returns
        -------
        Class instance
        """
        key = global_conf.private_key
        data = jwt.decode(token, key, algorithms='HS256', verify=verify)
        # Enforce conversion to satisfy typing
        data = dict(data)
        return cls(**data)

    @classmethod
    def decode_hp_s(cls, header_payload: str, signature: Optional[str] = None):
        """ Decode the token provided in the format "header.payload" and signature

        Parameters
        ----------
        signature: If provided, verify the authenticity of the token.

        Returns
        -------
        Class instance
        """
        sig = signature if signature is not None else 'DUMMYSIGNATURE'
        token = header_payload + '.' + sig
        return cls.decode_token(token=token, verify=(signature is not None))

    def encode_token(self) -> str:
        """ Encode the class data into a JWT and return a string

        Returns
        -------
        The JWT as a string
        """
        data = self.dict()
        data['exp'] = self.exp
        token_bytes = jwt.encode(data, global_conf.private_key, algorithm='HS256')
        return token_bytes.decode('utf-8')

    def encode_hp_s(self) -> Tuple[str, str]:
        """ Encode the class data into a JWT

        Returns
        -------
        The JWT in the format "header.payload" and the signature
        """
        token = self.encode_token()

        header, payload, signature = token.split('.')
        return f'{header}.{payload}', signature

    @property
    def cookie_key(self) -> str:
        """ Define the key of the cookie used to store the JWT """
        raise NotImplementedError
