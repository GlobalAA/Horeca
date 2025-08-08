from models.models import ExperienceVacancy


async def get_exactly_experience_vacancy() -> list[ExperienceVacancy]:
	qs = ExperienceVacancy.all().prefetch_related("user")
	count = await qs.count()

	if count < 10:
		return []
	
	records = await qs.all()

	seen = set()
	unique = []

	for record in records:
		name = record.name.lower()
		cv_user = record.user.id

		unique_str = f"{name}+{cv_user}"
		if unique_str not in seen:
			seen.add(unique_str)
			unique.append(record)

	return unique