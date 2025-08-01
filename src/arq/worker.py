from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from tortoise import Tortoise

from arq import cron
from arq.connections import RedisSettings
from arq.typing import WorkerSettingsBase
from arq.worker import Function
from src.config import config

from .functions.mailing import cv_mailing, vacancy_mailing
from .functions.time_expired import (check_user_time_expired,
                                     check_vacancy_time_expired)

REDIS_SETTINGS = RedisSettings(
	host=config.redis.host,
	port=config.redis.port,
	username=config.redis.username,
	password=config.redis.password.get_secret_value()
)

async def startup(ctx):
	print("Startup")

	ctx['bot'] = Bot(
		config.bot_token.get_secret_value(),
		default=DefaultBotProperties(parse_mode=ParseMode.HTML)
	)

	await Tortoise.init(
		db_url=config.db_url.get_secret_value(),
		modules={'models': ['src.models.models']}
	)
	print("Successfully")

async def shutdown(ctx):
	await Tortoise.close_connections()
	await ctx["bot"].session.close()
	print("Shutdown")

class WorkerSettings(WorkerSettingsBase):
	functions = [
		Function(
			name="time_expired_subscriptions",
			coroutine=check_user_time_expired,
			timeout_s=10.0,
			keep_result_s=0, 
			keep_result_forever=False,
			max_tries=1,
		),
		Function(
			name="time_expired_vacancies",
			coroutine=check_vacancy_time_expired,
			timeout_s=10.0,
			keep_result_s=0, 
			keep_result_forever=False,
			max_tries=1,
		),
		Function(
			name="cv_mailing",
			coroutine=cv_mailing,
			timeout_s=10.0,
			keep_result_s=0, 
			keep_result_forever=False,
			max_tries=1,
		),
		Function(
			name="vacancy_mailing",
			coroutine=vacancy_mailing,
			timeout_s=10.0,
			keep_result_s=0, 
			keep_result_forever=False,
			max_tries=1,
		)
	]
	on_startup = startup
	on_shutdown = shutdown
	redis_settings = REDIS_SETTINGS

	cron_jobs = [
		cron(check_user_time_expired, hour=8, minute=0, second=0, unique=True),
		cron(check_vacancy_time_expired, hour=8, minute=3, second=0, unique=True),
		cron(cv_mailing, hour=set(range(9, 24)), minute=0, second=0, unique=True),
		cron(vacancy_mailing, hour=set(range(9, 24)), minute=0, second=0, unique=True)
	]

if __name__ == "__main__":
	from arq.worker import run_worker
	run_worker(WorkerSettings)
