from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import (ExperienceData, ExperienceEnum,
                             ExperienceTypeData, ExperienceTypeEnum)


def experience_keyboard(user_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for exp in ExperienceEnum:
		builder.button(text=exp.value, callback_data=ExperienceData(user_id=user_id, experience=exp).pack())
		
	builder.adjust(1)

	return builder.as_markup()

def experience_type_keyboard(user_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	exp_type_text = {
		ExperienceTypeEnum.NAME: "Вказати назву закладу",
		ExperienceTypeEnum.VACANCY: "Вибрати заклад з бази",
		ExperienceTypeEnum.SKIP: "Без досвіду"
	}

	for exp_type in ExperienceTypeEnum:
		builder.button(text=exp_type_text[exp_type], callback_data=ExperienceTypeData(user_id=user_id, experience_type=exp_type).pack())

	builder.adjust(2, 1)

	return builder.as_markup()