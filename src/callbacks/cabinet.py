from datetime import timedelta
from typing import cast

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callbacks.types import (DeleteCv, DeleteVocation, ExtendPublicationData,
                             MyCvData, MyVocationData, UnPublishCv)
from config import config
from keyboards import edit_keyboard, get_cvs_keyboard
from keyboards.vocation_keybaord import vocation_keyboard_price
from models.enums import PriceOptionEnum
from models.models import Comment, CVs, ExperienceVacancy, User, Vacancies
from utils import get_min_price
from utils.cabinet_text import comment_slider_button, send_vocation

cabinet_router = Router()

@cabinet_router.callback_query(MyCvData.filter())
async def get_cvs(callback: CallbackQuery):
	full_name = callback.from_user.full_name

	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("cvs")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")

	cv: CVs = await user.cvs.all().first() #type: ignore
	experiences = await ExperienceVacancy.filter(cv=cv).all()

	if not cv:
		return await callback.answer("У вас ще немає створених резюме")

	message = cast(Message, callback.message)
	
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

	text = f"""{callback.from_user.full_name if not full_name else full_name}
➖➖➖➖➖
♟ {vocation}
📍 Місто: {cv.city.value}
🏠 Район: {cv.district}
💰 Мінімальна з/п: {cv.min_salary}
💵 Бажана з/п: {cv.desired_salary}
👨‍🦳 Вік: до {cv.age_group}
💡 Досвід роботи: {cv.experience_enum.value}{f"\n{experience_text}" if len(experience_blocks) > 0 else experience_text}
➖➖➖➖➖
📞 Телефон: {cv.phone_number}"""
	
	if cv.photo_id:
		return await message.answer_photo(cv.photo_id, caption=text, reply_markup=await get_cvs_keyboard(user_id=callback.from_user.id))
	
	await message.edit_text(text=text, reply_markup=await get_cvs_keyboard(user_id=callback.from_user.id))

@cabinet_router.callback_query(UnPublishCv.filter())
async def unpublish_cv(callback: CallbackQuery, callback_data: UnPublishCv):
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("cvs")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	cv: CVs = await user.cvs.all().first() #type: ignore

	cv.published = callback_data.action == "publish"

	try:
		await cv.save()

		message = cast(Message, callback.message)
		reply_markup = await get_cvs_keyboard(user_id=callback.from_user.id)

		await callback.answer("🟢 Статус резюме успішно змінено!")
		await message.edit_reply_markup(reply_markup=reply_markup)
	except:
		await callback.answer("🔴 Сталася помилка!")

@cabinet_router.callback_query(DeleteCv.filter())
async def delete_cv(callback: CallbackQuery):
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("cvs")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")

	cv: CVs = await user.cvs.all().first() #type: ignore
	with_photo = cv.photo_id != None
	await cv.delete()

	message = cast(Message, callback.message)

	if not with_photo:
		await message.edit_text("🟢 Резюме успішно видалено!")
	else:
		await message.delete()
		await message.answer("🟢 Резюме успішно видалено!")

@cabinet_router.callback_query(MyVocationData.filter())
async def vocation_get(callback: CallbackQuery, state: FSMContext):
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("vacancies")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	vacancies: list[Vacancies | ExperienceVacancy] = await user.vacancies.all() #type: ignore
	if len(vacancies) <= 0:
		return await callback.answer("У вас ще немає створених вакансій")
	vacancy: Vacancies | ExperienceVacancy = await vacancies[0]

	await state.update_data(vacancies=[v.id for v in vacancies], index=0)

	message = cast(Message, callback.message)
	text, markup = send_vocation(user.full_name, vacancies, 0, len(vacancies))

	if vacancy.photo_id:
		return await message.answer_photo(vacancy.photo_id, caption=text, reply_markup=markup)
	
	await message.edit_text(text=text, reply_markup=markup)

@cabinet_router.callback_query(DeleteVocation.filter())
async def delete_vocation(callback: CallbackQuery, callback_data: DeleteVocation, state: FSMContext):
	data = await state.get_data()
	steps = data.get('delete_step', 1)

	if steps <= 1:
		await callback.answer("Натисніть ще раз, щоб підтвердити видалення")
		return await state.update_data(delete_step=steps + 1)
	
	vocation = await Vacancies.get_or_none(id=callback_data.vocation_id)

	if not vocation:
		await callback.answer()
		return await callback.message.reply("🔴 Сталася помилка, вакансію не знайдено, зверніться до адміністратора")
	
	await state.clear()
	await vocation.delete()

	message = cast(Message, callback.message)

	if not vocation.photo_id:
		await message.edit_text("🟢 Вакансія успішно видалена!")
	else:
		await message.delete()	
		await message.answer("🟢 Вакансія успішно видалена!")

@cabinet_router.callback_query(F.data == "extend_publication")
async def extend_publication(callback: CallbackQuery, state: FSMContext):
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("subscriptions")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")

	
	message = cast(Message, callback.message)

	subscriptions: list[PriceOptionEnum] = [sub.status for sub in user.subscriptions] # type: ignore

	is_vip = PriceOptionEnum.VIP in subscriptions

	bad_balance = get_min_price() > user.balance

	if bad_balance:
		callback.answer()
		return await callback.message.answer("🔴 На жаль, на вашому балансі недостатньо коштів. Поповніть баланс для створення вакансій!")

	if user.on_week <= 0 and bad_balance and PriceOptionEnum.VIP in subscriptions:
		callback.answer()
		return await callback.message.answer("🔴 Ви вже витратили усі свої можливості на створення вакансій. Чекайте оновлення наступного місяця")

	data = await state.get_data()
	index = data['index']

	await callback.answer()
	await message.edit_reply_markup(reply_markup=None)
	await message.reply(
		"Варіант продовження", reply_markup=vocation_keyboard_price(
			balance=user.balance,
			vip=is_vip,
			extend=True,
			index=index
		)
	)	

@cabinet_router.callback_query(ExtendPublicationData.filter())
async def extend_publication_next(callback: CallbackQuery, callback_data: ExtendPublicationData, state: FSMContext):
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("subscriptions", "vacancies")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	data = await state.get_data()
	index = data['index']

	vacancies: list[Vacancies] = await user.vacancies.all() #type: ignore
	vacancy = vacancies[index]

	subscriptions: list[PriceOptionEnum] = [sub.status for sub in user.subscriptions] # type: ignore

	message = cast(Message, callback.message)

	if not vacancy:
		await callback.answer()
		return await message.answer("🔴 Будь ласка, зверніться до адміністратора, сталася помилка!")
	
	extend_type = callback_data.extend_type

	resume_sub_in_subscriptions = PriceOptionEnum.RESUME_SUB in subscriptions
	is_vip = PriceOptionEnum.VIP in subscriptions and extend_type == PriceOptionEnum.VIP

	is_week = extend_type == PriceOptionEnum.ONE_WEEK
	is_day = extend_type == PriceOptionEnum.ONE_DAY

	if is_week or is_day:
		price = config.price_options.ONE_WEEK if is_week else config.price_options.ONE_DAY
		if user.balance <  price:
			await callback.answer()
			return await message.answer("🔴 На вашому балансі недостатньо коштів для здійснення операції")
		user.balance -= int(price)
		vacancy.time_expired = vacancy.time_expired + timedelta(weeks=1)

		await vacancy.save()
		await user.save()

		await message.edit_text("Публікація вашої вакансії продовжена ще на тиждень")
	
	if extend_type == PriceOptionEnum.RESUME_SUB:
		if not resume_sub_in_subscriptions:
			await callback.answer()
			return await message.answer("В вашому тарифі не неможливо зробити, перейдіть в профіль, щоб оформити підписку/поповнити баланс")

		vacancy.resume_sub = True

		await vacancy.save()

		await message.edit_text("Тепер вам будуть надсилатись резюме, які підходять під ваші критерії")
	
	if is_vip:
		if user.on_week > 0:
			user.on_week -= 1

			vacancy.time_expired = vacancy.time_expired + timedelta(weeks=1)

			await vacancy.save()
			await user.save()
			
			await message.edit_text(f"За допомогою підписки, ви опублікували вакансію ще на один тиждень! У вас залишилось: {user.on_week} пуб.")
	
	await state.clear()
	await callback.answer()

@cabinet_router.callback_query(F.data == "view_comments")
async def view_comments(callback: CallbackQuery, state: FSMContext):
	message = cast(Message, callback.message)

	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("cvs")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")

	cv: CVs = await user.cvs.all().first() #type: ignore
	experiences = await ExperienceVacancy.filter(cv=cv).all()
	comments: list[Comment] = []

	for experience in experiences:
		comments_exp: list[Comment] = await experience.comments.all() #type: ignore
		for comment in comments_exp:
			comments.append(comment) 

	if len(comments) <= 0:
		return await message.answer("До вашої вакансії коментарів не знайдено")
	
	await state.update_data(comments=[comment.id for comment in comments], index=0)

	comment = comments[0]

	text = f"""Користувач {comment.author}
{comment.text}
Опубліковано {comment.created_at.strftime("%d.%m.%Y")}
"""
	await message.answer(text, reply_markup=await comment_slider_button(0, len(comments)))

@cabinet_router.callback_query(F.data == "edit_cv")
async def edit_cv_callback(callback: CallbackQuery):
	await callback.answer()
	user = await User.get_or_none(user_id=callback.from_user.id).prefetch_related("cvs")

	if not user:
		return await callback.message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	cv: CVs = await user.cvs.all().first() #type: ignore
	message = cast(Message, callback.message)

	await message.answer("Виберіть, що саме хочете змінити", reply_markup=edit_keyboard(cv.id))