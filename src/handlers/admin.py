from datetime import datetime, time

from aiogram import F, Router
from aiogram.filters import BaseFilter, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from callbacks.states import AdminInfoState
from models.enums import PriceOptionEnum
from models.models import UsefulInformation, User, UserRoleEnum, Vacancies


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

@admin_router.message(Command("change_info"), StateFilter(None), RoleFilter(UserRoleEnum.ADMIN))
async def admin_info(message: Message, state: FSMContext):
	await message.answer("Вітаю, для того, щоб оновити корисну інформацію для користувачів (роботодавців), надішліть мені файл")

	await state.set_state(AdminInfoState.send_document)

@admin_router.message(StateFilter(AdminInfoState.send_document), RoleFilter(UserRoleEnum.ADMIN), F.document)
async def admin_info_document(message: Message, state: FSMContext):
	if not message.document:
		await message.answer("Надішліть мені файл")
		return

	user = await User.get_or_none(user_id=message.from_user.id)

	if not user:
		return await message.answer("🔴 Сталася помилка, користувача не знайдено")

	file_id = message.document.file_id

	try:
		first = await UsefulInformation.first()
		if first:
			await first.delete()

		new_information = UsefulInformation(
			file_id=file_id,
			user=user
		)

		await new_information.save()

		await message.answer("Файл збережено, та меню /info оновлено")
	except Exception as e:
		print(f"{e}: AdminInfoState.save_document")
		return await message.answer("🔴 Сталася помилка")
