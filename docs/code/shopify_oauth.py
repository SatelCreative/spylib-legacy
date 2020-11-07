from asyncio import sleep
from fastapi import FastAPI

from spylib.auth import JWTBaseModel
from spylib.shopify.oauth import init_oauth_router
from spylib.shopify.oauth.tokens import OfflineToken, OnlineToken

FAKEDB_STORE = {}
FAKEDB_STAFF = {}

async def post_install(storename: str, offline_token: OfflineToken):
    FAKEDB_STORE[storename] = {'id': storename, **offline_token.dict()}
    await sleep(0.001)

class WebappJWT(JWTBaseModel):
    store_id: str
    staff_id: str

    @property
    def cookie_key(self):
        return f'_{self.store_id}'

async def post_login(storename: str, online_token: OnlineToken) -> WebappJWT:
    dbstore = FAKEDB_STORE.get(storename)
    if not dbstore:
        raise Exception('No store found')
    FAKEDB_STAFF[online_token.associated_user.id] = online_token.dict()
    await sleep(0.001)
    return WebappJWT(store_id=dbstore['id'],
                     staff_id=online_token.associated_user.id)

oauth_router = init_oauth_router(
    app_scopes=['read_orders', 'write_products'],
    user_scopes=['read_orders', 'read_products'],
    public_domain='myshopify.embedded.app',
    private_key='PRIVATE_KEY_PROVIDED_IN_THE_SHOPIFY_PARTNERS_PORTAL',
    post_install=post_install,
    post_login=post_login,
)

app = FastAPI()
app.include_router(oauth_router)
