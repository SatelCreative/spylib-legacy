from hashlib import sha256
from hmac import new, compare_digest
from base64 import b64encode


def validate_hmac(secret: str, sent_hmac: str, message: bytes, is_base64: bool = False):

    if sent_hmac is None:
        raise ValueError('Security header missing')

    hmac_hash = new(secret.encode('utf-8'), message, sha256)
    if is_base64:
        # TODO fix bytes / str union issue
        hmac_calculated: str = b64encode(hmac_hash.digest())  # type: ignore
        sent_hmac: str = sent_hmac.encode('utf-8')  # type: ignore
    else:
        hmac_calculated = hmac_hash.hexdigest()

    if not compare_digest(sent_hmac, hmac_calculated):
        raise ValueError('HMAC verification failed')
