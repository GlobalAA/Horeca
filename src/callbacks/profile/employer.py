from datetime import datetime, timedelta
from typing import cast

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardMarkup, Message,
                           PhotoSize)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.states import VocationState
from callbacks.types import (AgeGroupData, BackData, CityData,
                             CommunicationMethodData, DistrictData,
                             ExperienceData, FinalDataVocation, ImageData,
                             RateTypeData, ResetData, SubvocationData,
                             VacancyNameSkip, VocationData)
from keyboards import (age_group_keyboard, append_back_button, city_keyboard,
                       communication_method_keyboard, district_keyboard,
                       experience_keyboard, last_name_keyboard,
                       rate_type_keyboard, reset_keyboard,
                       subvocation_keyboard, vocation_keyboard,
                       vocation_keyboard_price)
from models.enums import (CommunicationMethodEnum, PriceOptionEnum,
                          RateTypeEnum, UserRoleEnum, VocationEnum)
from models.models import User, Vacancies
from utils import validate_phone_number
from utils.state import push_state
from utils.validate import percent_validate, validate_telegram_username

router_employer = Router()

@router_employer.callback_query(ResetData.filter(F.type == UserRoleEnum.EMPLOYER))
async def reset_handler(callback: CallbackQuery, state: FSMContext):
	await state.clear()
	
	message = cast(Message, callback.message)

	try:
		await message.edit_text("🔄 Починаємо спочатку")
	except TelegramBadRequest:
		await message.answer("🔄 Починаємо спочатку")
		
	await message.answer('Оберіть місто', reply_markup=city_keyboard(callback.from_user.id))
	await callback.answer()
	await push_state(state, VocationState.choosing_city)

@router_employer.callback_query(BackData.filter(F.type == UserRoleEnum.EMPLOYER), BackData.filter(F.edit == False))
async def back_handler(callback: CallbackQuery, state: FSMContext):
	data = await state.get_data()
	history: list[str] = data.get("history", [])

	if len(history) <= 1:
		print(history)
		return await callback.answer("🔴 Немає куди повертатись")

	history.pop()
	previous_state_str = history.pop()
	state_name = previous_state_str.split(':')[-1]

	target_state = getattr(VocationState, state_name, None)
	if not target_state:
		print(target_state, state_name)
		return await callback.answer("🔴 Неможливо повернутись назад")

	await state.update_data(history=history)
	await push_state(state, target_state)

	text_map = {
    "choosing_city": "Оберіть місто",
    "choosing_district": "Оберіть район",
    "choosing_vocation": "Виберіть сферу діяльності",
    "choosing_subvocation": "Виберіть підвакансію",
    "choosing_name": "Вкажіть назву закладу\n\nПишіть правильно, щоб в подальшому облегшити пошук",
    "choosing_address": "Вкажіть адресу закладу",
    "choosing_work_schedule": "Вкажіть графік роботи\n\nПриклад: з 11:00 до 22:00 і 2/2 або 2/4",
    "choosing_age_group": "Оберіть вікову групу",
    "choosing_experience": "Вкажіть досвід роботи",
    "choosing_salary": "Вкажіть заробітну плату",
    "choosing_rate_type": "Виберіть тип ставки в день",
    "choosing_rate": "Введіть ставку",
    "choosing_issuance_salary": "Вкажіть формати видачі заробітної плати\n\nПриклад: раз в місяць, раз в день",
    "choosing_communications": "Виберіть метод комунікації",
    "choosing_phone_number": "Вкажіть номер телефону",
    "choosing_telegram_link": "Надішліть посилання на телеграм, або тег",
    "choosing_photo_id": "Бажаєте додати зображення до вакансії? Надішліть або натисніть кнопку",
}

	keyboard_map = {
    "choosing_city": lambda uid, _: city_keyboard(uid),
    "choosing_district": lambda uid, d: district_keyboard(uid, d["city"]),
    "choosing_vocation": lambda uid, _: vocation_keyboard(uid),
    "choosing_subvocation": lambda uid, d: subvocation_keyboard(uid, d["vocation"]),
    "choosing_age_group": lambda uid, _: age_group_keyboard(uid),
    "choosing_experience": lambda uid, _: experience_keyboard(uid),
    "choosing_rate_type": lambda uid, _: rate_type_keyboard(uid),
    "choosing_communications": lambda uid, _: communication_method_keyboard(uid),
    "choosing_name": lambda *_: None,
    "choosing_address": lambda *_: None,
    "choosing_work_schedule": lambda *_: None,
    "choosing_salary": lambda *_: None,
    "choosing_rate": lambda uid, _: None,
    "choosing_issuance_salary": lambda *_: None,
    "choosing_phone_number": lambda *_: None,
    "choosing_telegram_link": lambda *_: None,
    "choosing_photo_id": lambda uid, _: None,
	}

	text = text_map.get(state_name, "⬅️ Повернення")
	uid = callback.from_user.id
	message = cast(Message, callback.message)

	if state_name in keyboard_map:
		keyboard = keyboard_map[state_name](uid, data)
		await message.edit_text(
			text,
			reply_markup=append_back_button(keyboard, state_name, UserRoleEnum.EMPLOYER)
		)
		return await callback.answer()

	await message.edit_text(text)
	await callback.answer()


@router_employer.callback_query(VocationState.choosing_city, CityData.filter())
async def choosing_city(callback: CallbackQuery, callback_data: CityData, state: FSMContext):
	await state.update_data(city=callback_data.city)

	message = cast(Message, callback.message)

	await message.edit_text(
		"Оберіть район",
		reply_markup=append_back_button(district_keyboard(callback.from_user.id, callback_data.city), "choosing_city", UserRoleEnum.EMPLOYER)
	)

	await callback.answer()
	await push_state(state, VocationState.choosing_district)

@router_employer.callback_query(VocationState.choosing_district, DistrictData.filter())
async def choosing_district_callback(callback: CallbackQuery, callback_data: DistrictData, state: FSMContext):
	await state.update_data(district=callback_data.district)

	message = cast(Message, callback.message)

	await message.edit_text(
		"Виберіть сферу діяльності",
		reply_markup=append_back_button(vocation_keyboard(callback.from_user.id), "choosing_district", UserRoleEnum.EMPLOYER)
	)

	await callback.answer()
	await push_state(state, VocationState.choosing_vocation)

@router_employer.callback_query(VocationState.choosing_vocation, VocationData.filter())
async def choosing_vocation_callback(callback: CallbackQuery, callback_data: VocationData, state: FSMContext):
	await state.update_data(vocation=callback_data.vocation)

	message = cast(Message, callback.message)
	
	if callback_data.vocation in (VocationEnum.HOSTESS, VocationEnum.CASHIER, VocationEnum.PURCHASER, VocationEnum.CLEANER, VocationEnum.SECURITY, VocationEnum.ACCOUNTANT, VocationEnum.HOOKAH):
		await message.answer("Вкажіть назву закладу\n\nПишіть правильно, щоб в подальшому облегшити пошук", reply_markup=append_back_button(await last_name_keyboard(user_id=callback.from_user.id), "choosing_name", UserRoleEnum.EMPLOYER))

		await callback.answer()
		return await push_state(state, VocationState.choosing_name)

	await message.edit_text(
		"Виберіть підвакансію",
		reply_markup=append_back_button(subvocation_keyboard(callback.from_user.id, callback_data.vocation), "choosing_vocation", UserRoleEnum.EMPLOYER)
	)

	await callback.answer()
	await push_state(state, VocationState.choosing_subvocation)

@router_employer.callback_query(VocationState.choosing_subvocation, SubvocationData.filter())
async def choosing_subvocation_callback(callback: CallbackQuery, callback_data: SubvocationData, state: FSMContext):
	await state.update_data(subvocation=callback_data.subvocation)

	message = cast(Message, callback.message)
	
	await message.edit_text("Вкажіть назву закладу\n\nПишіть правильно, щоб в подальшому облегшити пошук", reply_markup=append_back_button(await last_name_keyboard(user_id=callback.from_user.id), "choosing_subvocation", UserRoleEnum.EMPLOYER)) 

	await callback.answer()
	await push_state(state, VocationState.choosing_name)

@router_employer.message(VocationState.choosing_name)
async def choosing_name(message: Message, state: FSMContext):
	await state.update_data(name=message.text)

	await message.answer("Вкажіть адресу закладу", reply_markup=append_back_button(None, "choosing_name", UserRoleEnum.EMPLOYER))
	await push_state(state, VocationState.choosing_address)

@router_employer.callback_query(VocationState.choosing_name, VacancyNameSkip.filter())
async def choosing_name_callback(callback: CallbackQuery, callback_data: VacancyNameSkip, state: FSMContext):
	message = cast(Message, callback.message)
	await state.update_data(name=callback_data.last_name)

	await message.edit_text(text="Вибрано останню назву закладу")

	await message.answer("Вкажіть адресу закладу", reply_markup=append_back_button(None, "choosing_name", UserRoleEnum.EMPLOYER))
	await push_state(state, VocationState.choosing_address)

@router_employer.message(VocationState.choosing_address)
async def choosing_address(message: Message, state: FSMContext):
	await state.update_data(address=message.text)
	
	await message.answer("Вкажіть графік роботи\n\nПриклад: з 11:00 до 22:00 і 2/2 або 2/4", reply_markup=append_back_button(None, "choosing_address", UserRoleEnum.EMPLOYER))  

	await push_state(state, VocationState.choosing_work_schedule)

@router_employer.message(VocationState.choosing_work_schedule)
async def choosing_work_schedule(message: Message, state: FSMContext):
	await state.update_data(work_schedule=message.text)

	await message.answer(
		"Оберіть вікову групу",
		reply_markup=append_back_button(age_group_keyboard(message.from_user.id), "choosing_work_schedule", UserRoleEnum.EMPLOYER)
	)  

	await push_state(state, VocationState.choosing_age_group)


@router_employer.callback_query(VocationState.choosing_age_group, AgeGroupData.filter())
async def choosing_age_group_callback(callback: CallbackQuery, callback_data: AgeGroupData, state: FSMContext):
	await state.update_data(age_group=callback_data.age_group)

	message = cast(Message, callback.message)
	
	await message.edit_text(
		"Вкажіть досвід роботи",
		reply_markup=append_back_button(experience_keyboard(callback.from_user.id), "choosing_age_group", UserRoleEnum.EMPLOYER)
	)

	await callback.answer()
	await push_state(state, VocationState.choosing_experience)

@router_employer.callback_query(VocationState.choosing_experience, ExperienceData.filter())
async def choosing_experience(callback: CallbackQuery, callback_data: ExperienceData, state: FSMContext):
	await state.update_data(experience=callback_data.experience)

	message = cast(Message, callback.message)

	await message.edit_text("Вкажіть заробітну плату", reply_markup=append_back_button(None, "choosing_experience", UserRoleEnum.EMPLOYER))

	await callback.answer()
	await push_state(state, VocationState.choosing_salary)

@router_employer.message(VocationState.choosing_salary)
async def choosing_salary(message: Message, state: FSMContext):
	salary = message.text 

	try:
		salary = int(salary) #type: ignore
	except ValueError:
		return await message.answer("🔴 Будь ласка, введіть число для заробітної плати")

	await state.update_data(salary=salary)

	await message.answer(
		"Виберіть тип ставки в день", 
		reply_markup=append_back_button(rate_type_keyboard(message.from_user.id), "choosing_salary", UserRoleEnum.EMPLOYER)
	)

	await push_state(state, VocationState.choosing_rate_type)

@router_employer.callback_query(VocationState.choosing_rate_type, RateTypeData.filter())
async def choosing_rate_type(callback: CallbackQuery, callback_data: RateTypeData, state: FSMContext):
	await state.update_data(rate_type=callback_data.rate_type)

	await callback.message.answer("Введіть ставку", reply_markup=append_back_button(None, "choosing_rate_type", UserRoleEnum.EMPLOYER))

	await callback.answer()
	await push_state(state, VocationState.choosing_rate)

@router_employer.message(VocationState.choosing_rate)
async def choosing_rate(message: Message, state: FSMContext):
	data = await state.get_data()
	rate_type: RateTypeEnum = data['rate_type']

	if rate_type == RateTypeEnum.PRECENT and not percent_validate(str(message.text)):
		return await message.answer("🔴 Невірний формат ставки.\n\nДоступні формати: 100%, 50%, 10%")
	if rate_type == RateTypeEnum.PRECENT_RATE and not percent_validate(str(message.text), percent_with_rate=True):
		return await message.answer("🔴 Невірний формат ставки + відсоток\n\nДоступні формати: <i>1000 10%</i>, <i>10 15%</i> ")

	await state.update_data(rate=message.text)

	await message.answer("Вкажіть формати видачі заробітної плати\n\nПриклад: раз в місяць, раз в день", reply_markup=append_back_button(None, "choosing_rate", UserRoleEnum.EMPLOYER))

	await push_state(state, VocationState.choosing_issuance_salary)

@router_employer.message(VocationState.choosing_issuance_salary)
async def choosing_issuance_salary(message: Message, state: FSMContext):
	issuance_salary = message.text

	await state.update_data(issuance_salary=issuance_salary)

	await message.answer(
		"Виберіть метод комунікації", 
		reply_markup=append_back_button(communication_method_keyboard(message.from_user.id), "choosing_issuance_salary", UserRoleEnum.EMPLOYER)
	)

	await push_state(state, VocationState.choosing_communications)

@router_employer.callback_query(VocationState.choosing_communications, CommunicationMethodData.filter())
async def choosing_communication_method(callback: CallbackQuery, callback_data: CommunicationMethodData, state: FSMContext):
	await state.update_data(communication_data=callback_data.method)

	message = cast(Message, callback.message)
	
	await callback.answer()

	text = "Вкажіть номер телефону" if callback_data.method == CommunicationMethodEnum.PhoneCommunication else "Надішліть посилання на телеграм, або тег"

	await message.edit_text(text, reply_markup=append_back_button(None, "choosing_communications", UserRoleEnum.EMPLOYER))


	await push_state(state, VocationState.choosing_phone_number if callback_data.method == CommunicationMethodEnum.PhoneCommunication else VocationState.choosing_telegram_link)

@router_employer.message(VocationState.choosing_phone_number)
@router_employer.message(VocationState.choosing_telegram_link)
async def choosing_phone_number(message: Message, state: FSMContext):
	text = message.text

	current_state = await state.get_state()

	is_choosing_phone_number = current_state == VocationState.choosing_phone_number

	if isinstance(text, str):
		if not validate_phone_number(text) and is_choosing_phone_number:
			return await message.answer("🔴 Невірний формат номера телефону.\n\nДоступні формати: +380631234567 0631234567 0 67 123 45 67 +38-067-123-45-67")
		if not validate_telegram_username(text) and not is_choosing_phone_number:
			return await message.answer("🔴 Невірний формат телеграм username\n\nДоступні формати: @user_123 t.me/username https://t.me/user123", disable_web_page_preview=True)
	else:
		return await message.answer("🔴 Будь ласка, введіть коректно текст")

	if is_choosing_phone_number:
		await state.update_data(phone_number=text)
	else:
		await state.update_data(telegram_link=text)

	builder = InlineKeyboardBuilder()

	builder.button(
		text="⏫ Продовжити без зображення",
		callback_data=ImageData(user_id=message.from_user.id, with_image=False, photo_id=None)
	)

	await message.answer(
		"Бажаєте додати зображення до вакансії? Надішліть",
		reply_markup=append_back_button(builder.as_markup(), "choosing_phone_number" if is_choosing_phone_number else "choosing_telegram_link", UserRoleEnum.EMPLOYER)
	)

	await push_state(state, VocationState.choosing_photo_id)

@router_employer.message(VocationState.choosing_photo_id, F.photo, ~ImageData.filter())
async def choosing_photo_id(message: Message, state: FSMContext):
	photo = message.photo[-1] if message.photo else None

	if not photo:
		return await message.answer("🔴 Зображення не знайдено")

	await data_full_get(message, state, message.from_user.id, photo)

@router_employer.callback_query(VocationState.choosing_photo_id, ImageData.filter())
async def choosing_photo_id_callback(callback: CallbackQuery, callback_data: ImageData, state: FSMContext):
	with_img = callback_data.with_image

	if with_img == True:
		return await callback.message.answer("🔴 Сталася помилка")

	message = cast(Message, callback.message)
	
	await callback.answer()
	await data_full_get(message, state, full_name=callback.from_user.full_name, user_id=callback.from_user.id)

async def data_full_get(message: Message, state: FSMContext, user_id: int, photo: PhotoSize | None = None, full_name: str | None = None):
	data = await state.get_data()

	vocation = data['vocation']

	if (subvocation := data.get('subvocation', None)) != None and vocation:
		vocation = subvocation
	else:
		vocation = vocation.value

	user = await User.get_or_none(user_id=user_id).prefetch_related("subscriptions")

	phone_number = data.get('phone_number', None)
	telegram_link = data.get('telegram_link', None)

	communication_text = phone_number if phone_number else telegram_link

	full_data = f"""Заклад <i>{data['name']}</i>
➖➖➖➖➖
📍 Місто: {data["city"].value}
🏠 Район: {data['district']}
♟ {vocation}
⏱️ Графік роботи: {data['work_schedule']}
💰 Заробітна плата: {int(data['salary'])} | Ставка: {data['rate']}
📆 Видається з/п: {data['issuance_salary']}
👨‍🦳 Вік: до {data['age_group']}
💡 Досвід роботи: {data['experience'].value}
📞 Для зв'язку: {communication_text} | {full_name}
📩 Спосіб зв'язку: {data['communication_data'].value}"""

	reset_keyboard_inline = reset_keyboard(role=UserRoleEnum.EMPLOYER).inline_keyboard

	subscriptions: list[PriceOptionEnum] = [sub.status for sub in user.subscriptions] # type: ignore

	is_vip = PriceOptionEnum.VIP in subscriptions

	if is_vip and user.on_week <= 0:
		is_vip = False

	vocation_final_reset = vocation_keyboard_price(balance=user.balance, vip=is_vip).inline_keyboard + reset_keyboard_inline

	vocation_final_reset_markup = InlineKeyboardMarkup(inline_keyboard=vocation_final_reset)

	if not photo:
		await message.answer(full_data, reply_markup=vocation_final_reset_markup, disable_web_page_preview=True)
	else:
		await message.answer_photo(photo.file_id, full_data, reply_markup=vocation_final_reset_markup)

	await state.update_data(photo_id=photo.file_id if photo else None)
	await push_state(state, VocationState.final_state)

@router_employer.callback_query(VocationState.final_state, FinalDataVocation.filter())
async def vocation_final_state(callback: CallbackQuery, callback_data: FinalDataVocation, state: FSMContext):
	data = await state.get_data()

	if not data:
		return await callback.answer("🔴 Дані не знайдено")
	
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("subscriptions")

	message = cast(Message, callback.message)

	if not user:
		await callback.answer()
		return await message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")

	subscriptions: list[PriceOptionEnum] = [sub.status for sub in user.subscriptions] # type: ignore

	is_vip = PriceOptionEnum.VIP in subscriptions and callback_data.price_option == PriceOptionEnum.VIP

	resume_sub_in_subscriptions = PriceOptionEnum.RESUME_SUB in subscriptions

	if is_vip:
		if user.on_week > 0:
			user.on_week -= 1
		else:
			await callback.answer()
			return await message.answer("🔴 З вашим тарифом, це зробити неможливо")
	elif callback_data.price_option == PriceOptionEnum.RESUME_SUB:
		if resume_sub_in_subscriptions:
			data['resume_sub'] = True
		else:
			await callback.answer()
			return await message.answer("🔴 З вашим тарифом, це зробити неможливо")
	else:
		if user.balance <  callback_data.price:
			await callback.answer()
			return await message.answer("🔴 На вашому балансі недостатньо коштів для здійснення операції")
		user.balance -= int(callback_data.price)

	await state.clear()

	delta = timedelta()

	if callback_data.price_option in [PriceOptionEnum.VIP, PriceOptionEnum.ONE_WEEK]:
		delta = timedelta(weeks=1) 
	if callback_data.price_option == PriceOptionEnum.ONE_DAY:
		delta = timedelta(days=1) 
	if callback_data.price_option == PriceOptionEnum.RESUME_SUB:
		delta = timedelta(weeks=4)
	

	new_vocation = Vacancies(
		city=data['city'],
		district=data['district'],
		address = data['address'],
		name=data['name'],
		work_schedule=data['work_schedule'],
		issuance_salary=data['issuance_salary'],
		vocation=data['vocation'],
		subvocation=data.get('subvocation', None),
		age_group=data['age_group'],
		experience=data['experience'],
		salary=int(data['salary']),
		rate=data['rate'],
		rate_type=data['rate_type'],
		phone_number=data.get('phone_number', None),
		telegram_link=data.get('telegram_link', None),
		photo_id=data['photo_id'],
		communications=data['communication_data'],
		user=user,
		published=callback_data.published,
		resume_sub=data.get('resume_sub', False),
		time_expired=datetime.now() + delta
	)	

	user.last_vacancy_name = data['name']	

	await new_vocation.save()
	await user.save()

	await callback.answer()
	await message.reply(f"🟢 Вакансія збережена!")