from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" BIGINT NOT NULL UNIQUE,
    "username" VARCHAR(255),
    "full_name" VARCHAR(255) NOT NULL,
    "role" VARCHAR(8) NOT NULL,
    "balance" DOUBLE PRECISION NOT NULL,
    "last_msg_id" INT NOT NULL DEFAULT 0,
    "on_week" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "user"."role" IS 'ADMIN: ADMIN\nEMPLOYER: employer\nSEEKER: seeker\nUSER: USER';
CREATE TABLE IF NOT EXISTS "experiencevacancy" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "experience" VARCHAR(11) NOT NULL,
    "name" VARCHAR(255),
    "city" VARCHAR(6),
    "district" VARCHAR(255),
    "vocation" VARCHAR(13),
    "subvocation" VARCHAR(255),
    "rate" VARCHAR(255),
    "age_group" SMALLINT,
    "salary" INT,
    "phone_number" VARCHAR(255),
    "telegram_link" VARCHAR(255),
    "photo_id" VARCHAR(255),
    "communications" VARCHAR(14),
    "work_schedule" VARCHAR(255),
    "issuance_salary" VARCHAR(255),
    "rating" INT NOT NULL DEFAULT 0,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "experiencevacancy"."experience" IS 'NO_EXPERIENCE: Без досвіду\nUP_TO_1_YEAR: До 1 року\nONE_TO_TWO_YEARS: 1-2 роки\nTWO_TO_THREE_YEARS: 2-3 роки\nTHREE_TO_FIVE_YEARS: 3-5 років';
COMMENT ON COLUMN "experiencevacancy"."city" IS 'ODESA: Одеса\nKYIV: Київ\nLVIV: Львів\nKHARKIV: Харків\nDNIPRO: Дніпро';
COMMENT ON COLUMN "experiencevacancy"."vocation" IS 'BARMAN: Бармен\nMANAGER: Менеджер\nWAITER: Офіціант\nHOSTESS: Хостес\nCASHIER: Касир\nPURCHASER: Закупник\nHOOKAH: Кальянник\nCOOK: Кухар\nPORTO: Порто\nCLEANER: Прибиральниця\nSECURITY: Охорона\nACCOUNTANT: Бухгалтер';
COMMENT ON COLUMN "experiencevacancy"."age_group" IS 'AGE_18: 18\nAGE_25: 25\nAGE_30: 30\nAGE_35: 35\nAGE_40: 40\nAGE_45: 45\nAGE_60: 60';
COMMENT ON COLUMN "experiencevacancy"."communications" IS 'TelegramCommunication: Телеграм\nPhoneCommunication: Номер телефону';
CREATE TABLE IF NOT EXISTS "cvs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "city" VARCHAR(6) NOT NULL,
    "district" VARCHAR(255) NOT NULL,
    "vocation" VARCHAR(13) NOT NULL,
    "subvocation" VARCHAR(255),
    "age_group" SMALLINT NOT NULL,
    "min_salary" INT NOT NULL,
    "desired_salary" INT NOT NULL,
    "phone_number" VARCHAR(255) NOT NULL,
    "photo_id" VARCHAR(255),
    "published" BOOL NOT NULL DEFAULT False,
    "vacancies_ids" INT[] NOT NULL DEFAULT '{}',
    "experience_id" INT NOT NULL REFERENCES "experiencevacancy" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "cvs"."city" IS 'ODESA: Одеса\nKYIV: Київ\nLVIV: Львів\nKHARKIV: Харків\nDNIPRO: Дніпро';
COMMENT ON COLUMN "cvs"."vocation" IS 'BARMAN: Бармен\nMANAGER: Менеджер\nWAITER: Офіціант\nHOSTESS: Хостес\nCASHIER: Касир\nPURCHASER: Закупник\nHOOKAH: Кальянник\nCOOK: Кухар\nPORTO: Порто\nCLEANER: Прибиральниця\nSECURITY: Охорона\nACCOUNTANT: Бухгалтер';
COMMENT ON COLUMN "cvs"."age_group" IS 'AGE_18: 18\nAGE_25: 25\nAGE_30: 30\nAGE_35: 35\nAGE_40: 40\nAGE_45: 45\nAGE_60: 60';
CREATE TABLE IF NOT EXISTS "comment" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "author" VARCHAR(255) NOT NULL,
    "text" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "experience_id" INT NOT NULL REFERENCES "experiencevacancy" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "subscriptions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(13) NOT NULL DEFAULT 'free',
    "time_expired" TIMESTAMPTZ,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "subscriptions"."status" IS 'FREE: free\nONE_DAY: ONE DAY\nONE_WEEK: ONE WEEK\nVIP: VIP\nVIEW_COMMENTS: VIEW_COMMENTS\nRESUME_SUB: RESUME SUB';
CREATE TABLE IF NOT EXISTS "vacancies" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "address" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "work_schedule" VARCHAR(255) NOT NULL,
    "issuance_salary" VARCHAR(255) NOT NULL,
    "vocation" VARCHAR(13) NOT NULL,
    "subvocation" VARCHAR(255),
    "age_group" SMALLINT NOT NULL,
    "experience" VARCHAR(11) NOT NULL,
    "city" VARCHAR(6) NOT NULL,
    "district" VARCHAR(255) NOT NULL,
    "rate" VARCHAR(255) NOT NULL,
    "rate_type" VARCHAR(17) NOT NULL,
    "salary" INT NOT NULL,
    "phone_number" VARCHAR(255),
    "telegram_link" VARCHAR(255),
    "photo_id" VARCHAR(255),
    "communications" VARCHAR(14) NOT NULL,
    "published" BOOL NOT NULL DEFAULT False,
    "resume_sub" BOOL NOT NULL DEFAULT False,
    "cvs_id" INT[] NOT NULL DEFAULT '{}',
    "time_expired" TIMESTAMPTZ,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "vacancies"."vocation" IS 'BARMAN: Бармен\nMANAGER: Менеджер\nWAITER: Офіціант\nHOSTESS: Хостес\nCASHIER: Касир\nPURCHASER: Закупник\nHOOKAH: Кальянник\nCOOK: Кухар\nPORTO: Порто\nCLEANER: Прибиральниця\nSECURITY: Охорона\nACCOUNTANT: Бухгалтер';
COMMENT ON COLUMN "vacancies"."age_group" IS 'AGE_18: 18\nAGE_25: 25\nAGE_30: 30\nAGE_35: 35\nAGE_40: 40\nAGE_45: 45\nAGE_60: 60';
COMMENT ON COLUMN "vacancies"."experience" IS 'NO_EXPERIENCE: Без досвіду\nUP_TO_1_YEAR: До 1 року\nONE_TO_TWO_YEARS: 1-2 роки\nTWO_TO_THREE_YEARS: 2-3 роки\nTHREE_TO_FIVE_YEARS: 3-5 років';
COMMENT ON COLUMN "vacancies"."city" IS 'ODESA: Одеса\nKYIV: Київ\nLVIV: Львів\nKHARKIV: Харків\nDNIPRO: Дніпро';
COMMENT ON COLUMN "vacancies"."rate_type" IS 'PRECENT: Відсоток\nRATE: Ставка\nPRECENT_RATE: Ставка + відсоток';
COMMENT ON COLUMN "vacancies"."communications" IS 'TelegramCommunication: Телеграм\nPhoneCommunication: Номер телефону';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
