from typing import cast

from aiogram import F, Router
from aiogram.filters import BaseFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardMarkup,
                           InputMediaPhoto, Message)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tortoise.expressions import Q

from callbacks.types import ResumeSubNextData
from models.enums import DistrictEnum, PriceOptionEnum, ResumeSliderEnum
from models.models import CVs, ExperienceVacancy, Subscription, User, Vacancies
from utils.suitable import is_suitable


class SubscriptionFilter(BaseFilter):
	def __init__(self, subscription: PriceOptionEnum):
		self.subscription = subscription

	async def __call__(self, message: Message) -> bool:
		user = await User.get_or_none(user_id=message.from_user.id).prefetch_related("subscriptions")
		subscriptions: list[PriceOptionEnum] = [sub.status for sub in await user.subscriptions.all()] #type: ignore

		return self.subscription in subscriptions

router_sub = Router()

async def generate_slider_keyboard(index: int, total: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text=f"{index+1}/{total}", callback_data="slider_total_info__skip")

	if index > 0:
		builder.button(
			text="⬅️ Назад", 
			callback_data=ResumeSubNextData(
					index=index-1, 
					total=total, 
					type=ResumeSliderEnum.BACK
				)
			)
		
	if index < total - 1:
		builder.button(
			text="➡️ Вперед", 
			callback_data=ResumeSubNextData(
					index=index+1, 
					total=total, 
					type=ResumeSliderEnum.NEXT
				)
			)

	builder.adjust(1, 2)

	return builder.as_markup()

async def send_cv(experiences: list[ExperienceVacancy], cv: CVs, cvs_id: list[int], index: int = 0) -> tuple[str, InlineKeyboardMarkup]:
	ratings = {}
	
	for experience in experiences:
		if experience.rating:
			ratings[experience.name] = experience.rating
		else:
			ratings[experience.name] = 0

	vocation = cv.vocation.value
	subvocation = cv.subvocation

	if subvocation and vocation:
		vocation = subvocation

	experience_blocks = []
	for idx, experience in enumerate(experiences[:3], start=1):
		name = experience.name.capitalize() if experience.name else "Не вказано"
		rating = experience.rating or 0
		stars = f"\n🤩 Оцінка: {'⭐️' * rating}" if rating > 0 else ""
		
		block = f"""➖➖➖➖➖
💻 Минуле місце роботи ({idx}/3): {name}{stars}"""
		experience_blocks.append(block)

	experience_text = "\n".join(experience_blocks)

	text = f"""{cv.user.full_name}
➖➖➖➖➖
♟ Шукає: {vocation}
📍 Місто: {cv.city.value}
🏠 Район: {cv.district}
💰 Мінімальна з/п: {cv.min_salary}
💵 Бажана з/п: {cv.desired_salary}
👨‍🦳 Вік: до {cv.age_group}
💡 Досвід роботи: {cv.experience_enum.value}{f"\n{experience_text}" if len(experience_blocks) > 0 else experience_text}
➖➖➖➖➖
📞 Телефон: {cv.phone_number}"""
	
	reply_markup = await generate_slider_keyboard(index, len(cvs_id))

	return text, reply_markup

@router_sub.message(Command("search"), SubscriptionFilter(PriceOptionEnum.RESUME_SUB))
async def search_command(message: Message, state: FSMContext):
	user = await User.get_or_none(user_id=message.from_user.id).prefetch_related("vacancies")

	if not user:
		return await message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	vacancies: list[Vacancies] = await user.vacancies.all() #type: ignore
	if len(vacancies) <= 0:
		return await message.answer("🔴 У вас ще немає створених вакансій")
	
	if len(vacancies) <= 0:
		return await message.answer("🔴 У вас немає створених вакансій")
	
	cvs_found = False

	data = await state.get_data()
	cvs_id: list[int] = data.get('cvs_id', [])

	for vacancy in vacancies:
		filters = Q(
			city=vacancy.city,
			vocation=vacancy.vocation,
			age_group__lte=int(vacancy.age_group),
			min_salary__lte=vacancy.salary,
			desired_salary__lte=vacancy.salary
		)

		if vacancy.subvocation:
			filters &= Q(subvocation=vacancy.subvocation)
		
		cvs: list[CVs] = await CVs.filter(filters).all()

		for cv in cvs:
			if not is_suitable(cv.experience_enum, vacancy.experience):
				continue
		
		cvs_id.extend([cv.id for cv in cvs])
		if len(cvs_id) > 0:
			cvs_found = True

	if not cvs_found:
		return await message.answer("🔴 Не знайдено резюме, які би підішли під ваші вакансії")
	
	await state.update_data(cvs_id=cvs_id, index=0)

	cv = await CVs.get_or_none(id=cvs_id[0]).prefetch_related("user")
	
	if not cv:
		return await message.answer("🔴 Сталася помилка, резюме не знайдено, зверніться до адміністратора!")
	
	experiences = await ExperienceVacancy.filter(cv=cv).all()
	
	text, reply_markup = await send_cv(experiences, cv, cvs_id)

	if cv.photo_id:
		return await message.answer_photo(cv.photo_id, caption=text, reply_markup=reply_markup)
	
	await message.answer(text, reply_markup=reply_markup)

@router_sub.callback_query(ResumeSubNextData.filter(F.type == ResumeSliderEnum.NEXT))
@router_sub.callback_query(ResumeSubNextData.filter(F.type == ResumeSliderEnum.BACK))
async def resume_slider(callback: CallbackQuery, callback_data: ResumeSubNextData, state: FSMContext):
	data = await state.get_data()
	cvs_id: list[int] = data.get('cvs_id', [])
	index = callback_data.index

	cv = await CVs.get_or_none(id=cvs_id[index]).prefetch_related("user")

	if not cv:
		return await callback.answer("🔴 Сталася помилка, резюме не знайдено, зверніться до адміністратора!")

	experiences = await ExperienceVacancy.filter(cv=cv).all()

	text, reply_markup = await send_cv(experiences, cv, cvs_id, index)

	message = cast(Message, callback.message)

	if cv.photo_id:
		return await message.edit_media(
			InputMediaPhoto(
				media=cv.photo_id,
				caption=text
			),
			reply_markup=reply_markup
		)

	await message.edit_text(
		text=text,
		reply_markup=reply_markup
	)