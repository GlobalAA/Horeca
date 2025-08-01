from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "vacancies" ALTER COLUMN "issuance_salary" TYPE VARCHAR(255) USING "issuance_salary"::VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "vacancies" ALTER COLUMN "issuance_salary" TYPE INT USING "issuance_salary"::INT;"""
