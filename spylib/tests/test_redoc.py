import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..redoc import make_docs_router


@pytest.mark.asyncio
async def test_oauth(mocker):

    app = FastAPI()

    oauth_router = make_docs_router(
        title='test',
        description='Unit test',
        logo_url='https://fillmurray.com/200/300',
        logo_alt_text='Fill Murray',
        tags_and_models=[],
    )

    app.include_router(oauth_router)
    client = TestClient(app)

    response = client.get('/openapi.json')
    assert response.status_code == 200
