from typing import List, Callable
from dataclasses import dataclass
from inspect import isawaitable
from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from auth import JWTBaseModel

from .redirects import oauth_init_url, app_redirect
from .tokens import OAuthJWT, OfflineToken, OnlineToken
from .validations import validate_callback, validate_oauthjwt


@dataclass
class Callback:
    code: str = Query(...)
    hmac: str = Query(...)
    timestamp: int = Query(...)
    state: str = Query(...)
    shop: str = Query(...)


async def do_nothing():
    pass


def init_oauth_router(
    user_scopes: List[str],
    post_install: Callable[[str, OfflineToken], JWTBaseModel] = do_nothing,
    post_login: Callable[[str, OnlineToken], None] = do_nothing,
) -> APIRouter:
    oauth_router = APIRouter()

    @oauth_router.get('/callback', include_in_schema=False)
    async def shopify_callback(request: Request, args: Callback = Depends(Callback)):
        """ REST endpoint called by Shopify during the OAuth process for installation and login """
        try:
            validate_callback(
                shop=args.shop,
                timestamp=args.timestamp,
                query_string=request.scope['query_string'],
            )
            oauthjwt: OAuthJWT = validate_oauthjwt(token=args.state, shop=args.shop)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f'Validation failed: {e}')

        # === If login ===
        if oauthjwt.is_login:
            # Get the online token from Shopify
            online_token = await OfflineToken.get(domain=args.shop, code=args.code)

            if isawaitable(post_login):
                jwtoken = await post_login(storename=oauthjwt.storename, online_token=online_token)
            else:
                jwtoken = post_login(storename=oauthjwt.storename, online_token=online_token)

            # Redirect to the app in Shopify admin
            return app_redirect(store_domain=args.shop, jwtoken=jwtoken)

        # === If installation ===
        # Setup the login obj and redirect to oauth_redirect
        try:
            # Get the offline token from Shopify
            offline_token = await OfflineToken.get(domain=args.shop, code=args.code)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        if isawaitable(post_install):
            await post_install(storename=oauthjwt.storename, offline_token=offline_token)
        else:
            post_install(storename=oauthjwt.storename, offline_token=offline_token)

        redirect_url = oauth_init_url(
            domain=f'https://{oauthjwt.storename}.myshopify.com',
            is_login=True,
            requested_scopes=user_scopes,
        )
        return RedirectResponse(redirect_url)
