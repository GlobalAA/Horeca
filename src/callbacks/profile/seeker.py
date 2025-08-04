from typing import cast

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardMarkup, Message,
                           PhotoSize)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.states import CVState
from callbacks.types import (AgeGroupData, CityData, DistrictData,
                             ExperienceData, ExperienceTypeData,
                             ExperienceVacancyData, FinalDataCv, ImageData,
                             ResetData, SubvocationData, VocationData)
from constants import bot
from keyboards import (age_group_keyboard, append_back_button, city_keyboard,
                       cv_keyboard, district_keyboard, experience_keyboard,
                       experience_type_keyboard, rating_cv_button,
                       reset_keyboard, subvocation_keyboard, vocation_keyboard)
from models.enums import (DistrictEnum, ExperienceEnum, ExperienceTypeEnum,
                          PriceOptionEnum, UserRoleEnum, VocationEnum)
from models.models import CVs, ExperienceVacancy, User, Vacancies
from utils.cabinet_text import send_vocation
from utils.exect_vacancy_exp import get_exactly_experience_vacancy

router_seeker = Router()

from callbacks.types import BackData
from utils import push_state, validate_phone_number


async def save_experience_and_continue(state: FSMContext, vacancy: Vacancies | None, exp_vacancy: ExperienceVacancy | None, message: Message, id: int, is_name: bool = False):
	data = await state.get_data()
	index = data.get("experience_index", 1)

	if (not vacancy and not exp_vacancy) and not is_name:
		return await message.answer("🔴 Будь ласка, зверніться до адміністратора, сталася помилка!")
	
	if vacancy and not exp_vacancy:
		await state.update_data({
			f"experience_{index}_name": vacancy.name,
			f"experience_{index}_vacancy_id": vacancy.id
		})

	if exp_vacancy:
		await state.update_data({
			f"experience_{index}_name": exp_vacancy.name,
			f"experience_{index}_exp_vacancy_id": exp_vacancy.id,
		})

	if is_name:
		await state.update_data({
			f"experience_name_{index}_set": message.text
		})

	if index < 3:
		await state.update_data(experience_index=index + 1)
		await message.answer(f"Опишіть {index + 1}-е місце роботи", reply_markup=experience_type_keyboard(id))
		await push_state(state, CVState.choosing_experience_type)
	else:
		await message.answer("Вкажіть мінімальну зарплату в місяць", reply_markup=append_back_button(None, "choosing_experience_type"))

		return await push_state(state, CVState.choosing_min_salary)


@router_seeker.callback_query(ResetData.filter(F.type == UserRoleEnum.SEEKER))
async def reset_handler(callback: CallbackQuery, state: FSMContext):
	await state.clear()
	
	message = cast(Message, callback.message)

	try:
		await message.edit_text("🔄 Починаємо спочатку")
	except TelegramBadRequest:
		await message.answer("🔄 Починаємо спочатку")
		
	await message.answer('Оберіть місто', reply_markup=city_keyboard(callback.from_user.id))
	await callback.answer()
	await push_state(state, CVState.choosing_city)

@router_seeker.callback_query(BackData.filter(F.type == UserRoleEnum.SEEKER), BackData.filter(F.edit == False))
async def back_handler(callback: CallbackQuery, callback_data: BackData, state: FSMContext):
	data = await state.get_data()
	history: list[str] = data.get("history", [])

	if len(history) <= 1:
		return await callback.answer("🔴 Немає куди повертатись")

	history.pop() 
	previous_state_str = history.pop()

	state_name = previous_state_str.split(':')[-1]

	if "choosing_experience_vacancy" in state_name:
		state_name = "choosing_experience_type"

	target_state = getattr(CVState, state_name, None)

	if not target_state:
		return await callback.answer("🔴 Неможливо повернутись назад")

	await state.update_data(history=history)
	await push_state(state, target_state)

	index = data.get('experience_index', 1)

	text_map = {
		"choosing_city": "Оберіть місто",
		"choosing_district": "Оберіть район",
		"choosing_vocation": "Виберіть сферу діяльності",
		"choosing_subvocation": "Виберіть підвакансію",
		"choosing_age_group": "Оберіть вікову групу",
		"choosing_experience": "Вкажіть досвід роботи",
		"choosing_experience_type": f"Опишіть досвід роботи ({index}/3)",
		"choosing_experience_name": "Вкажіть назву місця роботи",
		"choosing_experience_vacancy": "Оберіть місце роботи зі списку",
		"choosing_min_salary": "Вкажіть мінімальну зарплату в місяць",
		"choosing_desired_salary": "Вкажіть бажану зарплату",
		"choosing_phone_number": "Вкажіть ваш номер телефону",
		"choosing_photo_id": "Бажаєте додати зображення до резюме? Надішліть",
	}


	keyboard_map = {
		"choosing_city": lambda uid, _: city_keyboard(uid),
		"choosing_district": lambda uid, data: district_keyboard(uid, data["city"]),
		"choosing_vocation": lambda uid, _: vocation_keyboard(uid),
		"choosing_subvocation": lambda uid, data: subvocation_keyboard(uid, data["vocation"]),
		"choosing_age_group": lambda uid, _: age_group_keyboard(uid),
		"choosing_experience": lambda uid, _: experience_keyboard(uid),
		"choosing_experience_type": lambda uid, _: experience_type_keyboard(uid),
		"choosing_experience_name": lambda *_: None,
    "choosing_experience_vacancy": lambda *_: None,
    "choosing_min_salary": lambda *_: None,
    "choosing_desired_salary": lambda *_: None,
    "choosing_phone_number": lambda *_: None,
    "choosing_photo_id": lambda *_: None,
    "final_state": lambda *_: None
	}

	text = text_map.get(state_name, "⬅️ Повернення")
	uid = callback.from_user.id
	message = cast(Message, callback.message)

	if state_name in keyboard_map:
		keyboard = keyboard_map[state_name](uid, data)

		if len(history) > 1 and index <= 1:
			await message.edit_text(text, reply_markup=append_back_button(keyboard, state_name))
			return await callback.answer()
		else:
			await message.edit_text(text, reply_markup=keyboard)
			return await callback.answer()

	await message.edit_text(text)
	await callback.answer()

@router_seeker.callback_query(CVState.choosing_city, CityData.filter())
async def choosing_city_callback(callback: CallbackQuery, callback_data: CityData, state: FSMContext):
	await state.update_data(city=callback_data.city)

	message = cast(Message, callback.message)

	await message.edit_text(
		"Оберіть район",
		reply_markup=append_back_button(district_keyboard(callback.from_user.id, callback_data.city), "choosing_city")
	)

	await callback.answer()
	await push_state(state, CVState.choosing_district)


@router_seeker.callback_query(CVState.choosing_district, DistrictData.filter())
async def choosing_district_callback(callback: CallbackQuery, callback_data: DistrictData, state: FSMContext):
	await state.update_data(district=callback_data.district)

	message = cast(Message, callback.message)

	await message.edit_text(
		"Виберіть сферу діяльності",
		reply_markup=append_back_button(vocation_keyboard(callback.from_user.id), "choosing_district")
	)

	await callback.answer()
	await push_state(state, CVState.choosing_vocation)


@router_seeker.callback_query(CVState.choosing_vocation, VocationData.filter())
async def choosing_vocation_callback(callback: CallbackQuery, callback_data: VocationData, state: FSMContext):
	await state.update_data(vocation=callback_data.vocation)

	message = cast(Message, callback.message)

	if callback_data.vocation in (VocationEnum.HOSTESS, VocationEnum.CASHIER, VocationEnum.PURCHASER, VocationEnum.CLEANER, VocationEnum.SECURITY, VocationEnum.ACCOUNTANT, VocationEnum.HOOKAH):
		await message.edit_text(
			"Оберіть вікову групу",
			reply_markup=append_back_button(age_group_keyboard(callback.from_user.id), "choosing_vocation")
		)

		await callback.answer()
		return await push_state(state, CVState.choosing_age_group)

	await message.edit_text(
		"Виберіть підвакансію",
		reply_markup=append_back_button(subvocation_keyboard(callback.from_user.id, callback_data.vocation), "choosing_vocation")
	)

	await callback.answer()
	await push_state(state, CVState.choosing_subvocation)


@router_seeker.callback_query(CVState.choosing_subvocation, SubvocationData.filter())
async def choosing_subvocation_callback(callback: CallbackQuery, callback_data: SubvocationData, state: FSMContext):
	await state.update_data(subvocation=callback_data.subvocation)

	message = cast(Message, callback.message)
	
	await message.edit_text(
		"Оберіть вікову групу",
		reply_markup=append_back_button(age_group_keyboard(callback.from_user.id), "choosing_subvocation")
	)  

	await callback.answer()
	await push_state(state, CVState.choosing_age_group)

@router_seeker.callback_query(CVState.choosing_age_group, AgeGroupData.filter())
async def choosing_age_group_callback(callback: CallbackQuery, callback_data: AgeGroupData, state: FSMContext):
	await state.update_data(age_group=callback_data.age_group)

	message = cast(Message, callback.message)
	
	await message.edit_text(
		"Вкажіть досвід роботи",
		reply_markup=append_back_button(experience_keyboard(callback.from_user.id), "choosing_age_group")
	)

	await callback.answer()
	await push_state(state, CVState.choosing_experience)

@router_seeker.callback_query(CVState.choosing_experience, ExperienceData.filter())
async def choosing_experience_callback(callback: CallbackQuery, callback_data: ExperienceData, state: FSMContext):
	await state.update_data(experience=callback_data.experience)

	message = cast(Message, callback.message)

	if callback_data.experience == ExperienceEnum.NO_EXPERIENCE:
		await message.edit_text("Вкажіть мінімальну зарплату в місяць", reply_markup=append_back_button(None, "choosing_min_salary"))

		await callback.answer()
		return await push_state(state, CVState.choosing_min_salary)
	
	await message.edit_text(
		"Як хочете вказати минуле місце роботи? (1/3)", 
		reply_markup=append_back_button(experience_type_keyboard(callback.from_user.id), "choosing_experience")
	)

	await callback.answer()
	await push_state(state, CVState.choosing_experience_type)

@router_seeker.callback_query(CVState.choosing_experience_type, ExperienceTypeData.filter())
async def choosing_experience_type_callback(callback: CallbackQuery, callback_data: ExperienceTypeData, state: FSMContext):
	await state.update_data(experience_type=callback_data.experience_type)
	data = await state.get_data()
	message = cast(Message, callback.message)

	filters = {
		'city': data['city'],
		'vocation': data['vocation'],
		'age_group': data['age_group'],
		'experience': data['experience']
	}

	district = data.get('district', None)

	if data.get('subvocation'):
		filters['subvocation'] = data['subvocation']

	if district and data['district'] != DistrictEnum.ALL.value[0]:
		filters['district'] = data['district']

	vacancies = await Vacancies.filter(**filters).all()
	exp_vacancies = await get_exactly_experience_vacancy(filters)

	if callback_data.experience_type == ExperienceTypeEnum.SKIP:
		await callback.answer()

		await message.reply("Продовжуємо без досвіду")
		await message.answer("Вкажіть мінімальну зарплату в місяць", reply_markup=append_back_button(None, "choosing_experience_type"))

		return await push_state(state, CVState.choosing_min_salary)

	if not vacancies and not exp_vacancies:
		await message.edit_text("Не знайдено вакансій")
		await message.answer("Вкажіть назву місця роботи", reply_markup=append_back_button(None, "choosing_experience_name"))
		return await push_state(state, CVState.choosing_experience_name)
	
	if callback_data.experience_type == ExperienceTypeEnum.NAME:
		
		await message.edit_text("Вкажіть назву місця роботи", reply_markup=append_back_button(None, "choosing_experience_name"))
		return await push_state(state, CVState.choosing_experience_name)

	final_vacancies = vacancies + exp_vacancies
	text, markup = send_vocation(callback.from_user.full_name, final_vacancies, 0, len(final_vacancies), True)

	await state.update_data(
		vacancies=[v.id for v in vacancies],
		experience_vacancies=[v.id for v in exp_vacancies],
		index=0,
	)

	await message.delete()
	await message.answer_photo(final_vacancies[0].photo_id, caption=text, reply_markup=markup) \
			if getattr(final_vacancies[0], "photo_id", None) else \
			await message.answer(text=text, reply_markup=markup)

	await push_state(state, CVState.choosing_experience_vacancy)	

@router_seeker.callback_query(CVState.choosing_experience_vacancy, ExperienceVacancyData.filter())
async def choosing_experience_vacancy(callback: CallbackQuery, callback_data: ExperienceVacancyData, state: FSMContext):
	vacancy = await Vacancies.get_or_none(id=callback_data.vacancy_id)
	exp_vacancy = await ExperienceVacancy.get_or_none(id=callback_data.vacancy_id)
	
	message = cast(Message, callback.message)
	await message.edit_reply_markup(reply_markup=None)

	await save_experience_and_continue(state, vacancy=vacancy, exp_vacancy=exp_vacancy, message=cast(Message, callback.message), id=callback.from_user.id)
	

@router_seeker.message(CVState.choosing_experience_name)
async def choosing_experience_name(message: Message, state: FSMContext):
	await save_experience_and_continue(state, message=message, vacancy=None, exp_vacancy=None, id=message.from_user.id, is_name=True)

@router_seeker.message(CVState.choosing_min_salary)
async def choosing_min_salary_callback(message: Message, state: FSMContext):
	min_salary = message.text 
	print(await state.get_data())
	try:
		min_salary = int(min_salary) #type: ignore
	except ValueError:
		return await message.answer("🔴 Будь ласка, введіть число для мінімальної зарплати")

	await state.update_data(min_salary=min_salary)

	await message.answer("Вкажіть бажану зарплату", reply_markup=append_back_button(None, "choosing_min_salary"))

	await push_state(state, CVState.choosing_desired_salary)

@router_seeker.message(CVState.choosing_desired_salary)
async def choosing_desired_salary(message: Message, state: FSMContext):
	desired_salary = message.text 

	try:
		desired_salary = int(desired_salary) #type: ignore
	except ValueError:
		return await message.answer("🔴 Будь ласка, введіть число для бажаної зарплати")

	await state.update_data(desired_salary=desired_salary)

	await message.answer("Вкажіть ваш номер телефону", reply_markup=append_back_button(None, "choosing_desired_salary"))

	await push_state(state, CVState.choosing_phone_number)

@router_seeker.message(CVState.choosing_phone_number)
async def choosing_phone_number(message: Message, state: FSMContext):
	phone_number = message.text


	if isinstance(phone_number, str):
		if not validate_phone_number(phone_number):
			return await message.answer("🔴 Невірний формат номера телефону.\n\nДоступні формати: +380631234567 0631234567 0 67 123 45 67 +38-067-123-45-67")
	else:
		return await message.answer("🔴 Будь ласка, введіть коректно текст")

	await state.update_data(phone_number=phone_number)

	builder = InlineKeyboardBuilder()

	builder.button(
		text="⏫ Продовжити без зображення",
		callback_data=ImageData(user_id=message.from_user.id, with_image=False, photo_id=None)
	)

	await message.answer(
		"Бажаєте додати зображення до резюме? Надішліть",
		reply_markup=append_back_button(builder.as_markup(), "choosing_phone_number")
	)

	await push_state(state, CVState.choosing_photo_id)

@router_seeker.message(CVState.choosing_photo_id, F.photo, ~ImageData.filter())
async def choosing_photo_id(message: Message, state: FSMContext):
	photo = message.photo[-1] if message.photo else None

	if not photo:
		return await message.answer("🔴 Зображення не знайдено")

	await data_full_get(message, state, photo)

@router_seeker.callback_query(CVState.choosing_photo_id, ImageData.filter())
async def choosing_photo_id_callback(callback: CallbackQuery, callback_data: ImageData, state: FSMContext):
	with_img = callback_data.with_image

	if with_img == True:
		return await callback.message.answer("🔴 Сталася помилка")

	message = cast(Message, callback.message)
	
	await callback.answer()
	await data_full_get(message, state, full_name=callback.from_user.full_name)

async def data_full_get(message: Message, state: FSMContext, photo: PhotoSize | None = None, full_name: str | None = None):
	data = await state.get_data()

	vocation = data['vocation']

	if (subvocation := data.get('subvocation', None)) != None and vocation:
		vocation = subvocation
	else:
		vocation = vocation.value


	full_data = f"""{message.from_user.full_name if not full_name else full_name}
➖➖➖➖➖
♟ {vocation}
📍 Місто: {data["city"].value}
🏠 Район: {data['district']}
💰 Мінімальна з/п: {int(data['min_salary'])}
💵 Бажана з/п: {int(data['desired_salary'])}
👨‍🦳 Вік: до {data['age_group']}
💡 Досвід роботи: {data['experience'].value}
📞 Телефон: {data['phone_number']}"""
	
	reset_keyboard_inline = reset_keyboard().inline_keyboard

	cv_keyboard_reset = cv_keyboard().inline_keyboard + reset_keyboard_inline

	cv_keyboard_reset_markup = InlineKeyboardMarkup(inline_keyboard=cv_keyboard_reset)

	if not photo:
		await message.answer(full_data, reply_markup=cv_keyboard_reset_markup)
	else:
		await message.answer_photo(photo.file_id, full_data, reply_markup=cv_keyboard_reset_markup)

	await state.update_data(photo_id=photo.file_id if photo else None)
	await push_state(state, CVState.final_state)
	
@router_seeker.callback_query(CVState.final_state, FinalDataCv.filter())
async def cv_final_state(callback: CallbackQuery, callback_data: FinalDataCv, state: FSMContext):
	data = await state.get_data()
	await state.clear()

	if not data:
		return await callback.answer("🔴 Дані не знайдено")

	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("subscriptions")
	message = cast(Message, callback.message)

	if not user:
		return await message.answer("🔴 Сталася помилка, користувача не знайдено")

	subscriptions = [sub.status for sub in user.subscriptions] if user.subscriptions else [] #type: ignore

	vocation = data.get('subvocation') or data['vocation'].value
	full_name = callback.from_user.full_name or ''
	city = data["city"]
	district = data["district"]
	age_group = data["age_group"]

	full_data = f"""{full_name}
➖➖➖➖➖
♟ {vocation}
📍 Місто: {city.value}
🏠 Район: {district}
💰 Мінімальна з/п: {int(data['min_salary'])}
💵 Бажана з/п: {int(data['desired_salary'])}
👨‍🦳 Вік: до {age_group}
💡 Досвід роботи: {data['experience'].value}
📞 Телефон: {data['phone_number']}"""

	try:
		new_cv = await CVs.create(
			city=city,
			district=district,
			vocation=data["vocation"],
			subvocation=data.get("subvocation"),
			age_group=age_group,
			experience_enum=data['experience'],
			min_salary=int(data["min_salary"]),
			desired_salary=int(data["desired_salary"]),
			phone_number=data["phone_number"],
			photo_id=data["photo_id"],
			user=user,
			published=callback_data.published
		)

		experience_indices = set()
		for key in data:
			if key.startswith("experience_") and "_name" in key and not "_set" in key:
				experience_indices.add(key.split("_")[1])
			elif key.startswith("experience_name_") and "_set" in key:
				experience_indices.add(key.split("_")[2])


		for index in experience_indices:
			exp_name = data.get(f"experience_{index}_name")
			if not exp_name:
				exp_name = data.get(f"experience_name_{index}_set")

			vacancy_id = data.get(f"experience_{index}_vacancy_id", None)

			if not vacancy_id:
				vacancy_id = data.get(f"experience_{index}_exp_vacancy_id")

			vacancy: Vacancies | ExperienceVacancy | None = None
			subscriptions: list[PriceOptionEnum] = []

			if vacancy_id:
				vacancy = await Vacancies.get_or_none(id=vacancy_id).prefetch_related("user")
				if not vacancy:
					vacancy = await ExperienceVacancy.get_or_none(id=vacancy_id).prefetch_related("user")

				subscriptions = [sub.status for sub in user.subscriptions] # type: ignore
		
				if not vacancy:
					return await message.answer("🔴 Сталася помилка, вакансію не знайдено, зверніться до адміністратора!")
				if not subscriptions:
					return await message.answer("🔴 Сталася помилка, даних про підписку не знайдено, зверніться до адміністратора!")

			exp_vac = ExperienceVacancy(
				name=exp_name,
				user=user,
				cv=new_cv
			)

			if vacancy:
				exp_vac.city = vacancy.city
				exp_vac.district = vacancy.district
				exp_vac.vocation = vacancy.vocation
				exp_vac.subvocation = vacancy.subvocation
				exp_vac.rate = vacancy.rate
				exp_vac.salary = vacancy.salary
				exp_vac.phone_number = vacancy.phone_number
				exp_vac.telegram_link = vacancy.telegram_link
				exp_vac.communications = vacancy.communications
				exp_vac.work_schedule = vacancy.work_schedule
				exp_vac.issuance_salary = vacancy.issuance_salary
				exp_vac.age_group = vacancy.age_group

			await exp_vac.save()
			if vacancy_id and PriceOptionEnum.VIEW_COMMENTS in subscriptions:
				caption = f"🟢 Користувач (<b><i>{full_name}</i></b>) вибрав ваш заклад (<b><i>{vacancy.name}</i></b>) в якості минулого місця роботи!\n\n{full_data}"
				if new_cv.photo_id:
					msg = await bot.send_photo(vacancy.user.user_id, photo=new_cv.photo_id, caption=caption, reply_markup=rating_cv_button(exp_id=exp_vac.id))
				else:
					msg = await bot.send_message(vacancy.user.user_id, caption, reply_markup=rating_cv_button(exp_id=exp_vac.id))
				await bot.pin_chat_message(vacancy.user.user_id, msg.message_id)

		await new_cv.save()

		await message.reply(f"🟢 Резюме збережено{', вам будуть приходити повідомлення, якщо зʼявляться відповідні вакансії' if callback_data.published else ''}")
		await callback.answer()
	except Exception as e:
		print(e)
		await message.answer("🔴 Сталася помилка")


