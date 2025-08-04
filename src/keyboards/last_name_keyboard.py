from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import VacancyNameSkip
from models.models import User


async def last_name_keyboard(user_id: int) -> InlineKeyboardMarkup | None:
	user = await User.get_or_none(user_id=user_id)

	if not user or not user.last_vacancy_name:
		return None

	builder = InlineKeyboardBuilder()

	builder.button(
		text=f"Залишити минулу назву закладу ({user.last_vacancy_name})",
		callback_data=VacancyNameSkip(last_name=user.last_vacancy_name)
	)

	return builder.as_markup()
