from io import BytesIO

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from aiogram.utils.chat_action import ChatActionSender
from fpdf import FPDF

from constants import bot
from keyboards import start_keyboard
from keyboards.cabinet_keyboards import cabinet_keyboard
from models.models import (PaymentHistory, PriceOptionEnum, Subscription, User,
                           UserRoleEnum)
from utils.cabinet_text import get_cabinet_text

router = Router()

@router.message(CommandStart())
async def start_message(message: Message):
	await message.answer(f"Вітаємо, {message.from_user.first_name}!\nЗа допомогою даного боту Ви можете швидко й зручно знайти співробітника для свого закладу або бажану роботу.", reply_markup=start_keyboard())

	username = message.from_user.username
	full_name = message.from_user.full_name

	if not username:
		username = "Не визначено"
	
	user, _ = await User.get_or_create(
		user_id=message.from_user.id,
		username=username,
		full_name=full_name,
		defaults={
			"role": UserRoleEnum.USER,
			"referrer_id": message.from_user.id,
			"last_msg_id": 0,
			"date_sub": None
		}
	)

	await Subscription.get_or_create(
		status=PriceOptionEnum.FREE,
		user=user
	)

@router.message(Command("cabinet"))
async def cabinet(message: Message):
	user = await User.get_or_none(user_id=message.from_user.id).prefetch_related("cvs", "vacancies", "subscriptions", "history")

	if not user:
		return await message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
	
	len_cv = len(user.cvs) #type: ignore
	len_vacancies = len(user.vacancies) #type: ignore

	len_published_cv = len([cv for cv in user.cvs if cv.published]) #type: ignore

	subscriptions: list[Subscription] = [sub for sub in user.subscriptions] #type: ignore
	
	text = get_cabinet_text(message, user, len_cv, len_published_cv, len_vacancies, subscriptions)
	
	await message.answer(text, reply_markup=cabinet_keyboard())

@router.message(Command("history"))
async def history_command(message: Message):
	async with ChatActionSender.upload_document(bot=bot, chat_id=message.from_user.id):
		user = await User.get_or_none(user_id=message.from_user.id).prefetch_related("history")

		if not user:
			return await message.answer("🔴 Сталася помилка, користувача не знайдено, зверніться до адміністратора!")
		
		with_history = await user.history.all().count() > 0 #type: ignore
		if with_history:
			pdf = FPDF()
			pdf.add_page()
			pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
			pdf.set_font("DejaVu", size=12)

			history: list[PaymentHistory] = await user.history.all() #type: ignore

			for h in history:
				text_pdf = (
					f"Ідентифікатор: {h.invoice_id}\n"
					f"Створено: {h.created_at.strftime('%d.%m.%Y %H:%M')}\n"
					f"Ціна: {h.amount}грн\n"
					f"Товар: {h.payment_type.value}\n\n"
				)

				pdf.multi_cell(0, 10, text_pdf, align="L")
			
			pdf_bytes = pdf.output(dest='S')
			if isinstance(pdf_bytes, bytearray):
				pdf_bytes = bytes(pdf_bytes)

			pdf_buffer = BytesIO(pdf_bytes)
			pdf_buffer.seek(0)

			input_file = BufferedInputFile(pdf_buffer.getvalue(), filename="payment_history.pdf")

			return await message.answer_document(
				document=input_file,
				caption="Історія платежів"
			)
		await message.answer("У вас ще не було жодного платежу")

@router.message(Command("info"))
async def info(message: Message):
	user = await User.get_or_none(user_id=message.from_user.id).prefetch_related()
	is_admin = True if user and user.role == UserRoleEnum.ADMIN else False

	description = (
    "Бот для пошуку роботи та співробітників.\n"
    "Обирайте, кого шукаєте — вакансію чи працівника.\n\n"
    "🟢 /start — розпочати пошук\n"
    "👤 /cabinet — особистий кабінет\n"
		"💰 /history — Історія платежів"
		"🔍 /search — Пошук резюме (від VIP+ тарифу)\n"
		f"{'📊 /statistic — статистика користувачів\n' if is_admin else ''}"
    "📩 Щогодини отримуйте нові вакансії або резюме!\n\n"
    "💰 Тарифи:\n"
    "• 1 оголошення на 1 день — 100 грн\n"
    "• 1 оголошення на тиждень — 300 грн\n\n"
		"🍀 Вигідні Тарифи\n"
    "• Тариф VIP (2000грн) - 10 оголошень на місяць з розміщенням на тиждень\n"
		"• Тариф VIP+ (3000грн) - 20 оголошень на місяць з розміщенням на тиждень + розсилка резюме"
		"• Тариф VIP (4000грн) - 20 оголошень на місяць з розміщенням на тиждень + розсилка резюме + можливість читати і писати коментарі про претендентів на роботу"
    "• Підписка на резюме на місяць\n\n"
		"📞 Підтримка: @german_mu"
	)
	
	await message.answer(description)