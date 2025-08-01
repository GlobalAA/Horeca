from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import ResetData
from models.enums import UserRoleEnum


def reset_keyboard(role: UserRoleEnum = UserRoleEnum.SEEKER) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text="🔄 Почати спочатку", callback_data=ResetData(type=role))
	
	builder.adjust(1)

	return builder.as_markup()