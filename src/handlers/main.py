from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message

from keyboards import start_keyboard
from keyboards.cabinet_keyboards import cabinet_keyboard
from models.models import PriceOptionEnum, Subscriptions, User, UserRoleEnum
from utils.cabinet_text import get_cabinet_text

router = Router()

@router.message(StateFilter(None), CommandStart())
async def start_message(message: Message):
	await message.answer(f"Вітаємо, {message.from_user.first_name}!\nЗа допомогою даного боту Ви можете швидко й зручно знайти співробітника для свого закладу або бажану роботу.", reply_markup=start_keyboard())

	username = message.from_user.username
	full_name = message.from_user.full_name

	if not username:
		username = "Не визначено"
	
	user, _ = await User.get_or_create(
		user_id=message.from_user.id,
		username=username,
		full_name=full_name,
		defaults={
			"role": UserRoleEnum.USER,
			"referrer_id": message.from_user.id,
			"balance": 0,
			"last_msg_id": 0,
			"date_sub": None
		}
	)

	await Subscriptions.get_or_create(
		status=PriceOptionEnum.FREE,
		user=user
	)

@router.message(Command("cabinet"))
async def cabinet(message: Message):
	user = await User.get_or_none(user_id=message.from_user.id).prefetch_related("cvs", "vacancies", "subscriptions")

	if not user:
		return await message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	len_cv = len(user.cvs) #type: ignore
	len_vacancies = len(user.vacancies) #type: ignore

	len_published_cv = len([cv for cv in user.cvs if cv.published]) #type: ignore

	subscriptions: list[Subscriptions] = [sub for sub in user.subscriptions] #type: ignore
	
	text = text = get_cabinet_text(message, user, len_cv, len_published_cv, len_vacancies, subscriptions)


	await message.answer(text, reply_markup=cabinet_keyboard())