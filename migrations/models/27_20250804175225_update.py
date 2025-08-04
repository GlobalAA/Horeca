from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cvs" ADD "experience_enum" VARCHAR(11);
        ALTER TABLE "experiencevacancy" DROP COLUMN "experience";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cvs" DROP COLUMN "experience_enum";
        ALTER TABLE "experiencevacancy" ADD "experience" VARCHAR(11) NOT NULL;"""
