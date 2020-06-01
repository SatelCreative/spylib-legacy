try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
except ImportError as e:
    print('ERROR: Could not import the library motor required to use spylib.mongo')
    raise e

from .config import conf


class MongoDB(AsyncIOMotorDatabase):
    __instance = None

    def __new__(cls):
        if MongoDB.__instance is None:
            client = AsyncIOMotorClient(
                host=[conf.host],
                port=conf.port,
                ssl=conf.ssl,
                tlsCAFile=conf.ssl_ca_cert,
                username=conf.username,
                password=conf.password,
                authSource=conf.dbname,
            )

            MongoDB.__instance = client[conf.dbname]
        return MongoDB.__instance
