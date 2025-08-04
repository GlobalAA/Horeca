from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cvs" DROP CONSTRAINT IF EXISTS "fk_cvs_experien_9a45a98a";
        ALTER TABLE "cvs" DROP COLUMN "experience_id";
        ALTER TABLE "experiencevacancy" ADD "cv_id" INT NOT NULL;
        ALTER TABLE "experiencevacancy" ADD CONSTRAINT "fk_experien_cvs_9b6a4e7b" FOREIGN KEY ("cv_id") REFERENCES "cvs" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "experiencevacancy" DROP CONSTRAINT IF EXISTS "fk_experien_cvs_9b6a4e7b";
        ALTER TABLE "cvs" ADD "experience_id" INT NOT NULL;
        ALTER TABLE "experiencevacancy" DROP COLUMN "cv_id";
        ALTER TABLE "cvs" ADD CONSTRAINT "fk_cvs_experien_9a45a98a" FOREIGN KEY ("experience_id") REFERENCES "experiencevacancy" ("id") ON DELETE CASCADE;"""
