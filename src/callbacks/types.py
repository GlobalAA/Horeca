from aiogram.filters.callback_data import CallbackData

from models.enums import (AgeGroupEnum, CityEnum, CommunicationMethodEnum,
                          ExperienceEnum, ExperienceTypeEnum, PriceOptionEnum,
                          RateTypeEnum, UserRoleEnum, VocationEnum)


class CityData(CallbackData, prefix="city"):
	user_id: int
	city: CityEnum


class DistrictData(CallbackData, prefix="district"):
	user_id: int
	district: str


class AgeGroupData(CallbackData, prefix="age"):
	user_id: int
	age_group: AgeGroupEnum


class ExperienceData(CallbackData, prefix="exp"):
	user_id: int
	experience: ExperienceEnum

class ExperienceTypeData(CallbackData, prefix="experience"):
	user_id: int
	experience_type: ExperienceTypeEnum

class ExperienceVacancyData(CallbackData, prefix="exp_vacancy"):
	vacancy_id: int

class VocationData(CallbackData, prefix="vocation"):
	user_id: int
	vocation: VocationEnum


class SubvocationData(CallbackData, prefix="subvoc"):
	user_id: int
	subvocation: str

class ImageData(CallbackData, prefix="image"):
	user_id: int
	with_image: bool
	photo_id: str | None

class RateTypeData(CallbackData, prefix="reset_type"):
	user_id: int
	rate_type: RateTypeEnum

	
class CommunicationMethodData(CallbackData, prefix="communication_method"):
	user_id: int
	method: CommunicationMethodEnum

class BackData(CallbackData, prefix="back"):
	to_state: str
	type: UserRoleEnum

class ResetData(CallbackData, prefix="reset"):
	type: UserRoleEnum

class FinalDataCv(CallbackData, prefix="final"):
	published: bool

class RatingCvData(CallbackData, prefix="rate"):
	exp_id: int
	stars: int

class FinalDataVocation(CallbackData, prefix="final_voc"):
	published: bool
	price_option: PriceOptionEnum
	price: int

class MyCvData(CallbackData, prefix="cv_data"):
	action: str

class MyVocationData(CallbackData, prefix="vacations_data"):
	action: str

class UnPublishCv(CallbackData, prefix="unpublish_cv"):
	action: str

class DeleteCv(CallbackData, prefix="delete_cv"):
	action: str

class ExtendPublicationData(CallbackData, prefix="extend_publication"):
	index: int
	extend_type: PriceOptionEnum