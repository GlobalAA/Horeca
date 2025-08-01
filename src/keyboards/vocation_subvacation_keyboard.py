from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import SubvocationData, VocationData, VocationEnum
from models.enums import SubvocationEnum


def vocation_keyboard(user_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for vocation in VocationEnum:
		builder.button(
			text=vocation.value.title(),
			callback_data=VocationData(user_id=user_id, vocation=vocation).pack()
		)
		
	builder.adjust(1)

	return builder.as_markup()

def subvocation_keyboard(user_id: int, vocation: VocationEnum) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()
	
	vocation_index = list(VocationEnum).index(vocation)+1
	
	for sub in SubvocationEnum:
		if sub.value[1] == vocation_index:
			builder.button(
				text=sub.value[0].title(),
				callback_data=SubvocationData(user_id=user_id, subvocation=sub.value[0]).pack()
			)

	builder.adjust(1)

	return builder.as_markup()