from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "Useful information";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
