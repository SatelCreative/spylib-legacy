import hashlib
import hmac
import base64

from urllib.parse import parse_qsl
from utils import now_epoch
from typing import Any

from ..config import conf
from ..utils import domain_to_storename
from .tokens import OAuthJWT


def validate_hmac(sent_hmac: str, message: bytes, is_webhook: bool = False):

    if sent_hmac is None:
        raise ValueError('Security header missing')

    secret = conf.secret_key
    hmac_hash = hmac.new(secret.encode('utf-8'), message, hashlib.sha256)
    if is_webhook:
        # TODO fix bytes / str union issue
        hmac_calculated: str = base64.b64encode(hmac_hash.digest())  # type: ignore
        sent_hmac: str = sent_hmac.encode('utf-8')  # type: ignore
    else:
        hmac_calculated = hmac_hash.hexdigest()

    if not hmac.compare_digest(sent_hmac, hmac_calculated):
        raise ValueError('HMAC verification failed')


def validate_callback(shop: str, timestamp: int, query_string: Any) -> None:
    q_str = query_string.decode('utf-8')
    # 1) Check that the shop is a valid Shopify URL
    domain_to_storename(shop)

    # 2) Check the timestamp. Must not be more than 5min old
    if now_epoch() - timestamp > 300:
        raise ValueError('Timestamp is too old')

    # 3) Check the hmac
    # Extract HMAC
    args = parse_qsl(q_str)
    # We assume here that the arguments were validated prior to calling
    # this function.
    hmac_arg = [arg[1] for arg in args if arg[0] == 'hmac'][0]
    args_nohmac = '&'.join([f'{arg[0]}={arg[1]}' for arg in args if arg[0] != 'hmac'])
    # Check HMAC
    message = args_nohmac.encode('utf-8')
    validate_hmac(sent_hmac=hmac_arg, message=message)

    return


def validate_oauthjwt(token: str, shop: str) -> OAuthJWT:
    oauthjwt = OAuthJWT.decode_token(token=token)

    storename = domain_to_storename(shop)
    if oauthjwt.storename != storename:
        raise ValueError('Token storename and query shop don\'t match')

    return oauthjwt
