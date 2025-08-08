from datetime import timedelta

from aiogram import Bot

from src.models.models import ExperienceVacancy, Vacancies


async def get_exactly_experience_vacancy() -> list[ExperienceVacancy]:
	records = await ExperienceVacancy.all().prefetch_related("user")

	seen = {}

	for record in records:
		name = record.name.lower()

		unique_str = f"{name}+{record.user.id}"
		if unique_str not in seen:
			seen[unique_str] = {"record": record, "count": 1}
		if unique_str in seen:
			seen[unique_str]["count"] += 1

	unique = [
		item["record"] for item in seen.values()
		if item["count"] > 10
	]

	return unique

async def vacancy_bonus(ctx):
	exp_vacancies: list[ExperienceVacancy] = await get_exactly_experience_vacancy()
	bot: Bot = ctx['bot']

	for vacancy in exp_vacancies:
		vacancy_model = await Vacancies.get_or_none(name=vacancy.name, city=vacancy.city, vocation=vacancy.vocation)
		
		if not vacancy_model:
			continue

		if vacancy_model.bonus:
			continue

		vacancy_model.bonus = True
		vacancy_model.time_expired = vacancy_model.time_expired + timedelta(weeks=1)

		await vacancy_model.save()

		await bot.send_message(vacancy.user.user_id, f"🎁 Вітаю, ваша вакансія для закладу{vacancy.name} отримала додатковий тиждень по акційній програмі!")