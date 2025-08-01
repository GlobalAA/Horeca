from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import RateTypeData
from models.enums import RateTypeEnum


def rate_type_keyboard(user_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for rate in RateTypeEnum:
		builder.button(text=rate.value, callback_data=RateTypeData(user_id=user_id, rate_type=rate).pack())
		
	builder.adjust(1)

	return builder.as_markup()