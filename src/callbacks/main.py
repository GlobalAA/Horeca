
from typing import cast

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callbacks.types import RatingCvData
from keyboards.cabinet_keyboards import cabinet_keyboard
from keyboards.city_district_keyboard import city_keyboard
from keyboards.cv_keyboard import rating_cv_keyboard
from models.enums import PriceOptionEnum
from models.models import ExperienceVacancy, Subscriptions, User, Vacancies
from utils import get_min_price, push_state
from utils.cabinet_text import get_cabinet_text, send_vocation

from .states import CVState, VocationState

router = Router()

@router.callback_query(StateFilter(None), F.data == "search_work")
async def search_work_callback(callback: CallbackQuery, state: FSMContext):
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("cvs")

	if not user:
		callback.answer()
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	if len(user.cvs) > 0: #type: ignore
		callback.answer()
		return await callback.message.answer("🔴 В вас вже є створене резюме, ви можете оновити його через особистий кабінет")

	await callback.message.answer('Оберіть місто', reply_markup=city_keyboard(callback.from_user.id))
	await callback.answer()
	await push_state(state, CVState.choosing_city)

@router.callback_query(StateFilter(None), F.data == "search_employer")
async def search_employer_callback(callback: CallbackQuery, state: FSMContext):
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("vacancies", "subscriptions")

	if not user:
		callback.answer()
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	subscriptions: list[PriceOptionEnum] = [sub.status for sub in user.subscriptions] # type: ignore

	bad_balance = get_min_price() > user.balance

	if bad_balance:
		callback.answer()
		return await callback.message.answer("🔴 На жаль, на вашому балансі недостатньо коштів. Поповніть баланс для створення вакансій!")

	if user.on_week <= 0 and bad_balance and PriceOptionEnum.VIP in subscriptions:
		callback.answer()
		return await callback.message.answer("🔴 Ви вже витратили усі свої можливості на створення вакансій. Чекайте оновлення наступного місяця")

	await callback.message.answer('Оберіть місто', reply_markup=city_keyboard(callback.from_user.id))
	await callback.answer()
	await push_state(state, VocationState.choosing_city) #type: ignore

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery, state: FSMContext):
	current_state = await state.get_state()

	if current_state:
		await state.clear()

	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("cvs", "vacancies", "subscriptions")

	if not user:
		return await callback.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")

	len_cv = len(user.cvs) #type: ignore
	len_vacancies = len(user.vacancies) #type: ignore

	len_published_cv = len([cv for cv in user.cvs if cv.published]) #type: ignore

	subscriptions: list[Subscriptions] = [sub for sub in user.subscriptions] #type: ignore
	
	text = get_cabinet_text(callback, user, len_cv, len_published_cv, len_vacancies, subscriptions)

	message = cast(Message, callback.message)
	await message.delete() 
	await message.answer(text, reply_markup=cabinet_keyboard())

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
	current_state = await state.get_state()
	
	if current_state is None:
		return await message.answer("⚠️ Немає активного процесу для скасування.")
	
	await state.clear()
	await message.answer("❌ Створення резюме або вакансії скасовано\n<b>Всі дані очищено</b>")

@router.callback_query(F.data.startswith("slider_next_vacancies"))
@router.callback_query(F.data.startswith("slider_prev_vacancies"))
async def slider_navigate(callback: CallbackQuery, state: FSMContext):
	data = await state.get_data()
	index = data.get("index", 0)

	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("vacancies")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")

	vacancies = []
	view_all = callback.data.split(':')[-1] == "True"

	for v in data['vacancies']:
		if (data := await Vacancies.get_or_none(id=int(v))) != None:
			vacancies.append(data)

	current_vacancy: Vacancies = vacancies[index]

	if not vacancies:
		await callback.message.answer("Немає записів.")
		return

	if callback.data.startswith("slider_next_vacancies") and index < len(vacancies) - 1:
		index += 1
	elif callback.data.startswith("slider_prev_vacancies") and index > 0:
		index -= 1
	else:
		return await callback.answer("Далі немає записів", show_alert=False)

	message = cast(Message, callback.message)

	await state.update_data(index=index)
	await message.delete()
	text, markup = send_vocation(callback.from_user.full_name, vacancies, index, len(vacancies), view_all)

	if current_vacancy.photo_id:
		return await message.answer_photo(current_vacancy.photo_id, caption=text, reply_markup=markup)
	
	await message.answer(text=text, reply_markup=markup)

@router.callback_query(RatingCvData.filter(F.stars == 0))
async def rating_callback(callback: CallbackQuery, callback_data: RatingCvData):
	experience = await ExperienceVacancy.get_or_none(id=callback_data.exp_id)

	message = cast(Message, callback.message)

	if not experience:
		await callback.answer()
		return await message.answer("🔴 Сталася помилка, зверніться до адміністратора")
	
	await callback.answer()
	await message.reply("⭐️ Оцініть роботу колишнього робітника", reply_markup=rating_cv_keyboard(callback_data.exp_id))

@router.callback_query(RatingCvData.filter(F.stars > 0))
async def rating_set_callback(callback: CallbackQuery, callback_data: RatingCvData):
	experience = await ExperienceVacancy.get_or_none(id=callback_data.exp_id)

	message = cast(Message, callback.message)

	if not experience:
		await callback.answer()
		return await message.answer("🔴 Сталася помилка, зверніться до адміністратора")
	
	stars = callback_data.stars

	try:
		experience.rating = stars
		await experience.save()

		await callback.answer()
		await message.edit_text("⭐️ Дякуємо за вашу оцінку!")
	except Exception as e:
		print(e)
		return await message.answer("🔴 Сталася помилка, зверніться до адміністратора")