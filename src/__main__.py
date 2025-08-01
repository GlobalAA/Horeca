import asyncio
import logging

from tortoise import Tortoise

from callbacks import setup_callbacks
from config import config
from constants import bot, dp
from handlers import setup_router

logging.basicConfig(
	level=logging.INFO
)

async def main():
	await Tortoise.init(
		db_url=config.db_url.get_secret_value(),
		modules={'models': ['models.models']}
	)

	dp.include_router(setup_router())
	dp.include_router(setup_callbacks())

	await bot.delete_webhook(True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		...