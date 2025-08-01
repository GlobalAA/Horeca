from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import CommunicationMethodData
from models.enums import CommunicationMethodEnum


def communication_method_keyboard(user_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for method in CommunicationMethodEnum:
		builder.button(text=method.value, callback_data=CommunicationMethodData(user_id=user_id, method=method).pack())
		
	builder.adjust(1)

	return builder.as_markup()