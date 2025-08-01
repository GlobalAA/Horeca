from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import AgeGroupData, AgeGroupEnum


def age_group_keyboard(user_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for age in AgeGroupEnum:
		builder.button(text=f'До {age.value} років', callback_data=AgeGroupData(user_id=user_id, age_group=age).pack())
		
	builder.adjust(1)

	return builder.as_markup()