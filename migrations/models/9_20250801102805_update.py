from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "cvs"."vocation" IS 'BARMAN: Бармен
MANAGER: Менеджер
WAITER: Офіціант
HOSTESS: Хостес
CASHIER: Касир
PURCHASER: Закупник
HOOKAH: Кальянник
COOK: Кухар
PORTO: Порто
CLEANER: Прибиральниця
SECURITY: Охорона
ACCOUNTANT: Бухгалтер';
        COMMENT ON COLUMN "vacancies"."vocation" IS 'BARMAN: Бармен
MANAGER: Менеджер
WAITER: Офіціант
HOSTESS: Хостес
CASHIER: Касир
PURCHASER: Закупник
HOOKAH: Кальянник
COOK: Кухар
PORTO: Порто
CLEANER: Прибиральниця
SECURITY: Охорона
ACCOUNTANT: Бухгалтер';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "cvs"."vocation" IS 'BARMAN: Бармен
MANAGER: Менеджер
WAITER: Офіціант
HOSTESS: Хостес
CASHIER: Касир
PURCHASER: Закупник
DISHWASHER: Мийник посуду
CLEANER: Прибиральниця
SECURITY: Охоронець
ACCOUNTANT: Бухгалтер';
        COMMENT ON COLUMN "vacancies"."vocation" IS 'BARMAN: Бармен
MANAGER: Менеджер
WAITER: Офіціант
HOSTESS: Хостес
CASHIER: Касир
PURCHASER: Закупник
DISHWASHER: Мийник посуду
CLEANER: Прибиральниця
SECURITY: Охоронець
ACCOUNTANT: Бухгалтер';"""
