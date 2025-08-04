from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import EditCv
from models.enums import EditCvEnum


def edit_keyboard(cv_id: int) -> InlineKeyboardMarkup | None:
	builder = InlineKeyboardBuilder()

	text_map = {
		EditCvEnum.VACATION: "💻 Змінити вакансію",
		EditCvEnum.SALARY: "💵 Змінити заробітну плату",
		EditCvEnum.PHONE_NUMBER: "☎️ Змінити номер телефону"
	}

	for edit in EditCvEnum:
		builder.button(
			text=text_map[edit],
			callback_data=EditCv(type=edit, cv_id=cv_id)
		)
		
	builder.adjust(1)

	return builder.as_markup()
