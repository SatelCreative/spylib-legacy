from urllib.parse import urlparse, parse_qs, ParseResult
from fastapi import FastAPI
from fastapi.testclient import TestClient
from box import Box

from spylib.shopify.oauth import init_oauth_router


def test_oauth():
    test_store = 'test.myshopify.com'
    test_data = Box(
        dict(
            app_scopes=['write_products', 'read_customers'],
            user_scopes=['write_orders', 'read_products'],
            public_domain='test.testing.com',
            private_key='TESTPRIVATEKEY',
            api_key='APIKEY',
        )
    )

    app = FastAPI()

    oauth_router = init_oauth_router(**test_data)

    app.include_router(oauth_router)
    client = TestClient(app)

    # --------- Test the initialization endpoint -----------

    # Missing shop argument
    response = client.get('/shopify/auth')
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {'loc': ['query', 'shop'], 'msg': 'field required', 'type': 'value_error.missing'}
        ],
    }

    # Happy path
    response = client.get('/shopify/auth', params=dict(shop=test_store), allow_redirects=False)
    assert response.status_code == 307

    parsed_url = urlparse(client.get_redirect_target(response))

    expected_parsed_url = ParseResult(
        scheme='https',
        netloc=test_store,
        path='/admin/oauth/authorize',
        query=parsed_url.query,  # We check that separately
        params='',
        fragment='',
    )
    assert parsed_url == expected_parsed_url

    parsed_query = parse_qs(parsed_url.query)
    state = parsed_query.pop('state')
    assert parsed_query == dict(
        client_id=[test_data.api_key],
        redirect_uri=[f'https://{test_data.public_domain}/callback'],
        scope=[','.join(test_data.app_scopes)],
    )

    # --------- Test the callback endpoint -----------

    response = client.get(
        '/callback', params=dict(shop=test_store, state=state), allow_redirects=False
    )
    assert response.status_code == 307
