from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard() -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text="💴 Шукаю роботу", callback_data='search_work')
	builder.button(text="👨‍⚕️ Шукаю співробітника", callback_data='search_employer')
	
	builder.adjust(1)

	return builder.as_markup()