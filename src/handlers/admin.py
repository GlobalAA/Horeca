from datetime import datetime, time

from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message

from models.enums import PriceOptionEnum
from models.models import User, UserRoleEnum, Vacancies


class RoleFilter(BaseFilter):
	def __init__(self, role: UserRoleEnum):
		self.role = role

	async def __call__(self, message: Message) -> bool:
		user = await User.get_or_none(user_id=message.from_user.id)
		return user.role == self.role

admin_router = Router()

@admin_router.message(Command("statistic"), RoleFilter(UserRoleEnum.ADMIN))
async def admin(message: Message):
	today_start = datetime.combine(datetime.today(), time.min)
	
	user_count = await User.all().count()
	user_today_count = await User.filter(created_at__gte=today_start).count()

	user_with_subscriptions_count = await User.filter(
		subscriptions__isnull=False, 
		subscriptions__status__not=PriceOptionEnum.FREE
	).distinct().count()

	user_with_cvs_count = await User.filter(cvs__isnull=False).distinct().count()

	vacancies_count = await Vacancies.all().count()

	text = "\n".join([
		"📊 Статистика",
		"",
		f"👤 Усього зареєстровано користувачів: {user_count}",
		f"👤 Сьогодні зареєстровано користувачів: {user_today_count}",
		"➖➖➖➖➖",
		f"💰 Усього активних підписок: {user_with_subscriptions_count}",
		f"📰 Кількість резюме: {user_with_cvs_count}",
		"➖➖➖➖➖",
		f"👨‍⚕️ Усього вакансій: {vacancies_count}"
	])

	await message.answer(text)

@admin_router.message(Command("information"))
async def admin_info(message: Message):
	await message.answer("Скоро...")
