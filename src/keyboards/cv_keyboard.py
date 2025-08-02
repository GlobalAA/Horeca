from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import CommentData, FinalDataCv, RatingCvData


def cv_keyboard() -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text="📰 Опублікувати і підписатись", callback_data=FinalDataCv(published=True).pack())
	builder.button(text="🔍 Тільки підписатись", callback_data=FinalDataCv(published=False).pack())
	
	builder.adjust(2)

	return builder.as_markup()

def rating_cv_button(exp_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	builder.button(text="📝 Оцінити", callback_data=RatingCvData(exp_id=exp_id, stars=0))
	builder.button(text="💬 Залишити коментар", callback_data=CommentData(exp_id=exp_id))

	return builder.as_markup()

def rating_cv_keyboard(exp_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for i in range(1, 6):
		builder.button(text=f"{i} ⭐️", callback_data=RatingCvData(exp_id=exp_id, stars=i).pack())

	builder.adjust(5)

	return builder.as_markup(resize_keyboard=True)