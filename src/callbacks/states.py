from aiogram.fsm.state import State, StatesGroup


class CVState(StatesGroup):
	choosing_city = State()
	choosing_district = State()
	choosing_vocation = State()
	choosing_subvocation = State()
	choosing_age_group = State()
	choosing_experience = State()
	choosing_experience_search = State()
	choosing_experience_type = State()
	choosing_experience_name = State()
	choosing_experience_vacancy = State()
	choosing_min_salary = State()
	choosing_desired_salary = State()
	choosing_phone_number = State()
	choosing_photo_id = State()
	final_state = State()

class VocationState(StatesGroup):
	choosing_city = State()
	choosing_district = State()
	choosing_vocation = State()
	choosing_subvocation = State()
	choosing_name = State()
	choosing_address = State()
	choosing_work_schedule = State()
	choosing_age_group = State()
	choosing_experience = State()
	choosing_salary = State()
	choosing_rate_type = State()
	choosing_rate = State()
	choosing_issuance_salary = State()
	choosing_additional_information = State()
	choosing_phone_number = State()
	choosing_telegram_link = State()
	choosing_communications = State()
	choosing_photo_id = State()
	choosing_price = State()
	
class VocationSlider(StatesGroup):
	viewing = State()

class CVComments(StatesGroup):
	set_comment = State()

class AdminInfoState(StatesGroup):
	send_document = State()

class EditCvState(StatesGroup):
	choosing_phone_number = State()
	choosing_vocation = State()
	choosing_subvocation = State()
	choosing_min_salary = State()
	choosing_desired_salary = State()