from aiogram import Bot

from keyboards import get_cvs_keyboard
from src.models.models import CVs, User, Vacancies


async def cv_mailing(ctx):
	vacancies = await Vacancies.filter(resume_sub=True).all()

	for vacancy in vacancies:
		filters = {
			'city': vacancy.city,
			'district': vacancy.district,
			'vocation': vacancy.vocation,
			'age_group': vacancy.age_group,
			'min_salary__lt': vacancy.salary
		}

		if vacancy.subvocation:
			filters['subvocation'] = vacancy.subvocation

		cvs = await CVs.filter(**filters).all().prefetch_related("user", "experience")

		if not cvs:
			continue

		for cv in cvs:
			bot: Bot = ctx['bot']

			if vacancy.id in cv.vacancies_ids:
				continue

			rating = cv.experience.rating

			text = f"""{cv.user.full_name}
➖➖➖➖➖
♟ {cv.vocation.value}
📍 Місто: {cv.city.value}
🏠 Район: {cv.district}
💰 Мінімальна з/п: {cv.min_salary}
💵 Бажана з/п: {cv.desired_salary}
👨‍🦳 Вік: до {cv.age_group}
➖➖➖➖➖
💡 Досвід роботи: {cv.experience.experience.value}
💻 Минуле місце роботи: {cv.experience.name.capitalize() if cv.experience.name else 'Не вказано'}{f"\n🤩 Оцінка: {'⭐️'* rating}" if rating > 0 else ""}
➖➖➖➖➖
📞 Телефон: {cv.phone_number}"""
			
			if cv.photo_id:
				await bot.send_photo(cv.user.user_id, cv.photo_id, caption=text, reply_markup=await get_cvs_keyboard(cv.user.id, only_comments=True))
			else:
				await bot.send_message(cv.user.user_id, text=text, reply_markup=await get_cvs_keyboard(cv.user.id, only_comments=True))

			cv.vacancies_ids.append(vacancy.id)
			await cv.save()

async def vacancy_mailing(ctx):
	cvs = await CVs.all().prefetch_related("user")
	
	for cv in cvs:
		filters = {
			'city': cv.city,
			'district': cv.district,
			'vocation': cv.vocation,
			'age_group': cv.age_group,
			'salary__gt': cv.min_salary
		}

		if cv.subvocation:
			filters['subvocation'] = cv.subvocation

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
			

