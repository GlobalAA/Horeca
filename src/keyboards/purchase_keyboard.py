from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import PriceData


def purchase_keyboard(url: str, invoice_id: str | None) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text="Оплатити", url=url)
	builder.button(text="Опублікувати", callback_data=f"pay_check:{invoice_id}")
	builder.button(text="Видалити транзакцію", callback_data=f"pay_cancel:{invoice_id}")
	
	builder.adjust(2)

	return builder.as_markup()