from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import MyCvData, MyVocationData


def cabinet_keyboard() -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text="🗂 Моє резюме", callback_data=MyCvData(action="get_cv"))
	builder.button(text="📰 Мої вакансії", callback_data=MyVocationData(action="get_vacations"))
	
	builder.adjust(2)

	return builder.as_markup()