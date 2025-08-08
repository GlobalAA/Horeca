from aiogram.filters.callback_data import CallbackData

from models.enums import (AgeGroupEnum, CityEnum, CommunicationMethodEnum,
                          EditCvEnum, ExperienceEnum, ExperienceTypeEnum,
                          PriceOptionEnum, RateTypeEnum, ResumeSliderEnum,
                          UserRoleEnum, VocationEnum, VocationSliderEnum)


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
	edit: bool

class ResetData(CallbackData, prefix="reset"):
	type: UserRoleEnum
	for_update: bool

class FinalDataCv(CallbackData, prefix="final"):
	published: bool

class ResumeSubNextData(CallbackData, prefix="resume_sub_next"):
	index: int
	total: int
	type: ResumeSliderEnum

class VocationNextData(CallbackData, prefix="vocation_next"):
	index: int
	total: int
	type: VocationSliderEnum

class RatingCvData(CallbackData, prefix="rate"):
	exp_id: int
	stars: int

class CommentData(CallbackData, prefix="comment"):
	exp_id: int

class PriceData(CallbackData, prefix="price_data"):
	price_option: PriceOptionEnum
	price: int

class DetailData(CallbackData, prefix="detail_data"):
	price_option: PriceOptionEnum
	action: str

class MyCvData(CallbackData, prefix="cv_data"):
	action: str

class MyVocationData(CallbackData, prefix="vacations_data"):
	action: str

class UnPublishCv(CallbackData, prefix="unpublish_cv"):
	action: str

class DeleteCv(CallbackData, prefix="delete_cv"):
	action: str

class DeleteVocation(CallbackData, prefix="delete_vocation"):
	vocation_id: int

class ExtendPublicationDetail(DetailData, prefix="extend_publication_detail"): ...

class ExtendPublicationPrice(PriceData, prefix="extend_publication_price"): ...

class VacancyNameSkip(CallbackData, prefix="vacancy_name_skip"):
	last_name: str

class EditCv(CallbackData, prefix="edit_cv"):
	type: EditCvEnum
	cv_id: int