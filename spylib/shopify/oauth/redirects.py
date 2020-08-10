from typing import List, Optional
from starlette.responses import RedirectResponse

from utils import get_unique_id, conf as global_conf
from auth import JWTBaseModel

from .tokens import OAuthJWT
from ..config import conf
from ..utils import domain_to_storename


def oauth_init_url(domain: str, requested_scopes: List[str], is_login: bool) -> str:
    """
    Create the URL and the parameters needed to start the oauth process to install an app or to log
    a user in.

    Parameters
    ----------
    domain: Domain of the shopify store in the format "{storesubdomain}.myshopify.com"
    requested_scopes: List of scopes accessible to the app once installed.
        See https://shopify.dev/docs/admin-api/access-scopes
    is_login: Specify if the oauth is to install the app or a user logging in

    Returns
    -------
    URL with all needed parameters to trigger the oauth process
    """
    scopes = ','.join(requested_scopes)
    redirect_uri = f'https://{global_conf.public_domain}/callback'
    oauthjwt = OAuthJWT(
        is_login=is_login, storename=domain_to_storename(domain), nonce=get_unique_id()
    )
    oauth = oauthjwt.encode()
    access_mode = 'per-user' if is_login else ''

    return (
        f'https://{domain}.myshopify.com/admin/oauth/authorize?client_id={conf.api_key}&'
        f'scope={scopes}&redirect_uri={redirect_uri}&state={oauth.token}&'
        f'grant_options[]={access_mode}'
    )


def app_redirect(store_domain: str, jwtoken: Optional[JWTBaseModel]) -> RedirectResponse:
    jwtarg, signature = jwtoken.encode_hp_s()
    app_handle = conf.handle
    redir = RedirectResponse(f'https://{store_domain}/admin/apps/{app_handle}?jwt={jwtarg}')

    # TODO set 'expires'
    redir.set_cookie(
        key=jwtoken.cookie_key,
        value=signature,
        domain=global_conf.public_domain,
        httponly=True,
        secure=True,
    )

    return redir
