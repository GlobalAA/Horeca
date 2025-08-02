from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import CommentData, DeleteCv, UnPublishCv
from models.models import CVs, User


async def get_cvs_keyboard(user_id: int, only_comments: bool = False) -> InlineKeyboardMarkup:
	user = await User.get_or_none(user_id=user_id).prefetch_related("cvs")
	cv: CVs = await user.cvs.all().first() #type: ignore

	builder = InlineKeyboardBuilder()

	if not only_comments:
		builder.button(text=f"🍀 {"Зняти з публікації" if cv.published else "Опублікувати"}", callback_data=UnPublishCv(action="unpublish" if cv.published else "publish"))
		builder.button(text="🗑 Видалити", callback_data=DeleteCv(action="delete_cv"))
		builder.button(text="💬 Коментарі", callback_data="view_comments")
		builder.button(text="Повернутися у профіль", callback_data="back_to_profile")
	else:
		builder.button(text="💬 Коментарі", callback_data="view_comments")
		
	builder.adjust(1)

	return builder.as_markup()