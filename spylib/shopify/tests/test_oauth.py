from fastapi import FastAPI
from fastapi.testclient import TestClient

from spylib.shopify.oauth import init_oauth_router


def test_oauth():
    app = FastAPI()

    oauth_router = init_oauth_router(
        app_scopes=['write_products'],
        user_scopes=['write_orders'],
        public_domain='test.testing.com',
        api_key='APIKEY',
    )

    app.include_router(oauth_router)
    client = TestClient(app)

    response = client.get("/shopify/auth")
