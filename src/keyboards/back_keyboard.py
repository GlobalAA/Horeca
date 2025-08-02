from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.types import BackData
from models.enums import UserRoleEnum


def append_back_button(markup: InlineKeyboardMarkup | None, to_state: str, role: UserRoleEnum = UserRoleEnum.SEEKER) -> InlineKeyboardMarkup:
	back_button = InlineKeyboardButton(
		text="🔙 Повернутись",
		callback_data=BackData(to_state=to_state, type=role).pack()
	)

	if markup is None:
		return InlineKeyboardMarkup(inline_keyboard=[[back_button]])

	new_inline_keyboard = list(markup.inline_keyboard)
	new_inline_keyboard.append([back_button])
	
	return InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
