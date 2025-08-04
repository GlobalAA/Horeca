import asyncio

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.models.enums import DistrictEnum
from src.models.models import CVs, ExperienceVacancy, Vacancies


async def get_cvs_keyboard() -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text="💬 Коментарі", callback_data="view_comments")
	builder.adjust(1)
	return builder.as_markup()

async def cv_mailing(ctx):
	try:
		vacancies = await Vacancies.filter(resume_sub=True).all()

		for vacancy in vacancies:
			filters = {
				'city': vacancy.city,
				'vocation': vacancy.vocation,
				'age_group': vacancy.age_group,
				'min_salary__lt': vacancy.salary
			}

			if vacancy.subvocation:
				filters['subvocation'] = vacancy.subvocation
			if vacancy.district != DistrictEnum.ALL.value:
				filters['district'] = vacancy.district

			cvs = await CVs.filter(**filters).prefetch_related("user").all()
			print(cvs, filters)
			if not cvs:
				continue

			bot: Bot = ctx['bot']
			for cv in cvs:
				experiences = await ExperienceVacancy.filter(cv=cv).all()

				if vacancy.id in cv.vacancies_ids:
					continue

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
					await bot.send_photo(cv.user.user_id, cv.photo_id, caption=text, reply_markup=await get_cvs_keyboard())
				else:
					await bot.send_message(cv.user.user_id, text=text, reply_markup=await get_cvs_keyboard())

				cv.vacancies_ids.append(vacancy.id)
				await cv.save()

				await asyncio.sleep(2)
	except Exception as e:
		print(e)

async def vacancy_mailing(ctx):
	cvs = await CVs.all().prefetch_related("user")
	
	for cv in cvs:
		filters = {
			'city': cv.city,
			'vocation': cv.vocation,
			'age_group': cv.age_group,
			'salary__gt': cv.min_salary
		}

		if cv.subvocation:
			filters['subvocation'] = cv.subvocation
		if cv.district != DistrictEnum.ALL.value:
			filters['district'] = cv.district

		vacancies = await Vacancies.filter(**filters).all().prefetch_related("user")

		for vacancy in vacancies:
			bot: Bot = ctx['bot']

			if cv.id in vacancy.cvs_id:
				print(1)
				continue

			vocation = vacancy.vocation

			if (subvocation := vacancy.subvocation) != None and vacancy:
				vocation = subvocation
			else:
				vocation = vocation.value

			communication_text = vacancy.phone_number if vacancy.phone_number else vacancy.telegram_link

			text = f"""Заклад <i>{vacancy.name}</i>
		➖➖➖➖➖
		📍 Місто: {vacancy.city.value}
		🏠 Район: {vacancy.district}
		♟ {vocation}
		⏱️ Графік роботи: {vacancy.work_schedule}
		💰 Заробітна плата: {int(vacancy.salary)} | Ставка: {vacancy.rate}
		📆 Видається з/п: {vacancy.issuance_salary}
		👨‍🦳 Вік: до {vacancy.age_group}
		💡 Досвід роботи: {vacancy.experience.value}
		📞 Для зв'язку: {communication_text} | {vacancy.user.full_name}
		📩 Спосіб зв'язку: {vacancy.communications.value}"""
			
			if vacancy.photo_id:
				await bot.send_photo(cv.user.user_id, vacancy.photo_id, caption=text)
			else:
				await bot.send_message(cv.user.user_id, text)

			vacancy.cvs_id.append(cv.id)
			await vacancy.save()
			
			await asyncio.sleep(2)

