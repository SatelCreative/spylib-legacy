from typing import Any, Dict
from httpx import AsyncClient
from time import monotonic
from asyncio import sleep
from loguru import logger
from tenacity import retry
from tenacity.wait import wait_random
from tenacity.stop import stop_after_attempt
from tenacity.retry import retry_if_exception

from .exceptions import ShopifyError, ShopifyCallInvalidError, not_our_fault


API_VERSION: str = '2020-04'
FETCH_TIMEOUT = 10
# Default assumes Shopify Plus rate
RATE = 4
MAX_TOKENS = 80


class Store:
    _instances: dict = {}

    def __init__(self, store_id: str, name: str, access_token: str):
        self.id = store_id
        self.name = name
        self.url = f'https://{name}.myshopify.com/admin/api/{API_VERSION}'

        self.client = AsyncClient()
        self.updated_at = monotonic()

        self.reset_access_token(access_token=access_token)

    @classmethod
    def load(cls, store_id, name, access_token):
        """ Load the store from memory to reuse the tokens

        WARNING: the name will not be changed here after the first initialization
        """
        if store_id not in Store._instances:
            Store._instances[store_id] = Store(
                store_id=store_id, name=name, access_token=access_token
            )
        else:
            # Verify if the access token has changed
            if Store._instances[store_id].access_token != access_token:
                Store._instances[store_id].reset_access_token(access_token)
        return Store._instances[store_id]

    def reset_access_token(self, access_token: str):
        """ Use this function to initialize a new access token for this store"""
        self.access_token = access_token
        self.access_token_invalid = False
        self.tokens = MAX_TOKENS
        self.max_tokens = MAX_TOKENS
        self.rate = RATE

    async def __wait_for_token(self):
        while self.tokens <= 1:
            self.__add_new_tokens()
            await sleep(1)
        self.tokens -= 1

    def __add_new_tokens(self):
        now = monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.rate
        if new_tokens > 1:
            self.tokens = min(self.tokens + new_tokens, self.max_tokens)  # type: ignore
            self.updated_at = now

    async def __handle_error(self, debug: str, endpoint: str, response):
        """ Handle any error that occured when calling Shopify

        If the response has a valid json then return it too.
        """
        msg = (
            f'ERROR in store {self.name}: {debug}\n'
            f'API response code: {response.status}\n'
            f'API endpoint: {endpoint}\n'
        )
        try:
            jresp = await response.json()
        except Exception:
            pass
        else:
            msg += f'API response json: {jresp}\n'

        if 400 <= response.status < 500:
            # This appears to be our fault
            raise ShopifyCallInvalidError(msg)

        raise ShopifyError(msg)

    @retry(
        wait=wait_random(min=1, max=2),
        stop=stop_after_attempt(5),
        retry=retry_if_exception(not_our_fault),
    )
    async def shoprequest(self, goodstatus, debug, endpoint, **kwargs) -> Dict[str, Any]:
        while True:
            await self.__wait_for_token()
            kwargs['url'] = f'{self.url}{endpoint}'
            kwargs['headers'] = {'X-Shopify-Access-Token': self.access_token}
            kwargs.setdefault('timeout', FETCH_TIMEOUT)

            response = await self.client.request(**kwargs)
            if response.status_code == 429:
                # We hit the limit, we are out of tokens
                self.tokens = 0
                continue
            elif 400 <= response.status_code or response.status_code != goodstatus:
                # All errors are handled here
                await self.__handle_error(
                    debug=debug, endpoint=endpoint, response=response
                )
            else:
                jresp = response.json()
                # Recalculate the rate to be sure we have the right one.
                calllimit = response.headers['X-Shopify-Shop-Api-Call-Limit']
                self.max_tokens = int(calllimit.split('/')[1])
                # In Shopify the bucket is emptied after 20 seconds
                # regardless of the bucket size.
                self.rate = int(self.max_tokens / 20)

            return jresp

    async def execute_gql(self, query: str, variables: Dict[str, Any] = {}) -> Dict[str, Any]:
        """ Simple graphql query executor because python has no decent graphql client """

        url = f'{self.url}/graphql.json'
        headers = {
            "Content-type": "application/json",
            'X-Shopify-Access-Token': self.access_token,
        }
        resp = await self.client.post(
            url=url, json={'query': query, 'variables': variables}, headers=headers
        )
        jsondata = resp.json()
        if type(jsondata) is not dict:
            raise ValueError('JSON data is not a dictionary')

        if 'Invalid API key or access token' in jsondata.get('errors', {}):  # type: ignore
            # Typing seems to not take into account the type check above
            self.access_token_invalid = True
            logger.warning(
                f'Store {self.name}: The Shopify API token is invalid. '
                'Flag the access token as invalid.'
            )
            raise ConnectionRefusedError
        return jsondata


class UniqueStore(Store):
    __instance = None

    def __new__(cls):
        if UniqueStore.__instance is None:
            raise ValueError('The unique store was not initialized')
        return UniqueStore.__instance

    @staticmethod
    def init(store_id, name, access_token):
        UniqueStore.__instance = Store(store_id, name, access_token)
