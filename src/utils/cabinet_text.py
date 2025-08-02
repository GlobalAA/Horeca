from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import ExperienceVacancyData
from keyboards.back_keyboard import append_back_button
from models.enums import PriceOptionEnum
from models.models import ExperienceVacancy, Subscriptions, User, Vacancies


def format_subscriptions(subscriptions: list [Subscriptions]):
	if not subscriptions:
		return "У вас немає активних підписок🍂"
	
	text_map = {
		PriceOptionEnum.FREE: "Безкоштовний",
		PriceOptionEnum.VIP: "VIP",
		PriceOptionEnum.RESUME_SUB: "Підписка на розсилку резюме",
		PriceOptionEnum.VIEW_COMMENTS: "Можливість взаємодіяти з минулими працівниками"
	}

	result_lines = ["🍀 <b>Підписки:</b>"]
	for sub in subscriptions:
		expired = sub.time_expired.strftime("%d.%m.%Y") if sub.time_expired else "∞"
		result_lines.append(f"• {text_map[sub.status]} — до <b>{expired}</b>")
	return '\n'.join(result_lines)

def get_cabinet_text(callback: CallbackQuery | Message, user: User, len_cv: int, len_published_cv: int, len_vacancies: int, subscriptions: list[Subscriptions]):
	return f"""📇 Ім'я: {callback.from_user.full_name}
🔑 ID: {callback.from_user.id}
💰 Баланс: {user.balance} грн
📅 Дата реєстрації: {user.created_at.strftime("%d.%m.%Y")}
➖➖➖➖➖
{format_subscriptions(subscriptions)}
➖➖➖➖➖
📝 Кількість створених резюме: {len_cv} шт.
📌 Кількість опублікованих резюме: {len_published_cv} шт
➖➖➖➖➖
📰 Кількість створених вакансій: {len_vacancies} шт
"""

def send_vocation(full_name: str, vocations: list[Vacancies | ExperienceVacancy], index: int, total: int, view_all: bool = False) -> tuple[str, InlineKeyboardMarkup]:
	vocation_model = vocations[index]
	phone_number = vocation_model.phone_number
	telegram_link = vocation_model.telegram_link

	communication_text = phone_number if phone_number else telegram_link

	vocation = vocation_model.vocation

	if (subvocation := vocation_model.subvocation) != None and vocation:
		vocation = subvocation
	else:
		vocation = vocation.value


	text = f"""Заклад <i>{vocation_model.name}</i>
➖➖➖➖➖
📍 Місто: {vocation_model.city.value}
🏠 Район: {vocation_model.district}
♟ {vocation}
⏱️ Графік роботи: {vocation_model.work_schedule}
💰 Заробітна плата: {int(vocation_model.salary)} | Ставка: {vocation_model.rate}
📆 Видається з/п: {vocation_model.issuance_salary}
👨‍🦳 Вік: до {vocation_model.age_group}
💡 Досвід роботи: {vocation_model.experience.value}
📞 Для зв'язку: {communication_text} | {full_name}
📩 Спосіб зв'язку: {vocation_model.communications.value}"""
	
	builder = InlineKeyboardBuilder()

	if not view_all:
		builder.button(text="Повернутися у профіль", callback_data="back_to_profile")

	if index > 0:
		builder.button(text="⬅️ Назад", callback_data=f"slider_prev_vacancies:{view_all}")
	if index < total - 1:
		builder.button(text="➡️ Вперед", callback_data=f"slider_next_vacancies:{view_all}")
	if not view_all:
		builder.button(text="Продовжити публікацію", callback_data="extend_publication")

	if view_all:
		builder.button(text="🟢 Обрати", callback_data=ExperienceVacancyData(vacancy_id=vocation_model.id))
		
		if index > 0 and index < total - 1:
			builder.adjust(2, 1)
		else:
			builder.adjust(1, 1)

		with_back = append_back_button(builder.as_markup(), "choosing_experience_type")

		return text, with_back
	else:
		if index > 0 and index < total - 1:
			builder.adjust(1, 2, 1)
		else:
			builder.adjust(1, 1, 1)
		return text, builder.as_markup()
	
async def comment_slider_button(index: int, total: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	if index > 0:
		builder.button(text="⬅️ Назад", callback_data=f"slider_prev_comment")
	if index < total - 1:
		builder.button(text="➡️ Вперед", callback_data=f"slider_next_comment")

	builder.button(text="Повернутися у профіль", callback_data="back_to_profile")

	if index > 0 and index < total - 1:
		builder.adjust(2, 1)
	else:
		builder.adjust(1, 1)

	return builder.as_markup()
