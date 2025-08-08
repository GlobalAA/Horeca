from datetime import datetime, timezone

from aiogram import Bot

from src.models.enums import PriceOptionEnum
from src.models.models import Subscription, Vacancies


async def check_user_time_expired(ctx):
	subs = await Subscription.exclude(status=PriceOptionEnum.FREE).prefetch_related("user")
	for sub in subs:
		time_expired = sub.time_expired

		if not time_expired:
			continue

		if time_expired < datetime.now(tz=timezone.utc):
			bot: Bot = ctx['bot']
			text_map = {
				PriceOptionEnum.VIP: "VIP",
				PriceOptionEnum.RESUME_SUB: "Підписка на розсилку резюме",
				PriceOptionEnum.VIEW_COMMENTS: "Можливість взаємодіяти з минулими працівниками"
			}
			await bot.send_message(sub.user.user_id, f"Одна з ваших підписок закінчилась, пройшов вже місяць з моменту покупки. Перейдіть в профіль, щоб знову її купити\n\n🍀 {text_map[sub.status]}")
			await sub.delete()

async def check_vacancy_time_expired(ctx):
	vacancies = await Vacancies.all().prefetch_related("user")
	for vacancy in vacancies:
		time_expired = vacancy.time_expired

		if not time_expired:
			continue

		if time_expired < datetime.now(tz=timezone.utc):
			bot: Bot = ctx['bot']

			communication_text = vacancy.phone_number if vacancy.phone_number else vacancy.telegram_link

			vocation = vacancy.vocation

			if (subvocation := vacancy.subvocation) != None and vocation:
				vocation = subvocation
			else:
				vocation = vocation.value
			
			text = f"""Заклад <i>{vacancy.name}</i> <b>видалено</b> з бази
➖➖➖➖➖
📍 Місто: {vacancy.city.value}
🏠 Район: {vacancy.district}
♟ Шукає: {vocation}
⏱️ Графік роботи: {vacancy.work_schedule}
💰 Заробітна плата: {int(vacancy.salary)} | Ставка: {vacancy.rate}
📆 Видається з/п: {vacancy.issuance_salary}
👨‍🦳 Вік: до {vacancy.age_group}
💡 Досвід роботи: {vacancy.experience.value}
📞 Для зв'язку: <b>{communication_text}</b> | {vacancy.user.full_name	}
📩 Спосіб зв'язку: <b>{vacancy.communications.value}</b>"""
			
			await bot.send_message(vacancy.user.user_id, text)
			await vacancy.delete()

