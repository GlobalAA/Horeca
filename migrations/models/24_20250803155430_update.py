from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "last_vacancy_name" VARCHAR(255);
        ALTER TABLE "user" DROP COLUMN "last_msg_id";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "last_msg_id" INT NOT NULL DEFAULT 0;
        ALTER TABLE "user" DROP COLUMN "last_vacancy_name";"""
