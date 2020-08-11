import nest_asyncio
from pytest import yield_fixture
from asyncio import get_event_loop


nest_asyncio.apply()


@yield_fixture()
def event_loop():
    """ Prevent errors where two coroutines are in different loops by never closing the loop """
    loop = get_event_loop()
    yield loop
