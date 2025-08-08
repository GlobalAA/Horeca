from models.enums import ExperienceEnum

EXPERIENCE_MAP = {
	ExperienceEnum.NO_EXPERIENCE: 0,
	ExperienceEnum.UP_TO_1_YEAR: 0, 
	ExperienceEnum.ONE_TO_TWO_YEARS: 1,
	ExperienceEnum.TWO_TO_THREE_YEARS: 2,
	ExperienceEnum.THREE_TO_FIVE_YEARS: 3,
}

def is_suitable(candidate_exp: ExperienceEnum, employer_exp: ExperienceEnum) -> bool:
	candidate_years = EXPERIENCE_MAP[candidate_exp]
	employer_years = EXPERIENCE_MAP[employer_exp]
	return candidate_years >= employer_years