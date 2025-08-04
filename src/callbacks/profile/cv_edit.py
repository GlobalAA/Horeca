from typing import cast

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callbacks.states import EditCvState
from callbacks.types import BackData, EditCv, SubvocationData, VocationData
from keyboards.back_keyboard import append_back_button
from keyboards.vocation_subvacation_keyboard import (subvocation_keyboard,
                                                     vocation_keyboard)
from models.enums import EditCvEnum, VocationEnum
from models.models import CVs
from utils.validate import validate_phone_number

edit_router = Router()

async def save_vocation(state: FSMContext, message: Message):
	data = await state.get_data()
	cv_id = int(data.get("cv_id", ""))
	
	cv: CVs | None = await CVs.get_or_none(id=cv_id)

	if not cv:
		return await message.answer("🔴 Сталася помилка, резюме не знайдено")
	
	cv.vocation = data['vocation']

	subvocation = data.get('subvocation', None)

	if subvocation:
		cv.subvocation = subvocation

	await cv.save()
	await state.clear()

	await message.edit_text("🟢 Сферу діяльності оновлено")

@edit_router.callback_query(BackData.filter(F.edit == True))
async def vocation_back_handler(callback: CallbackQuery, state: FSMContext):
	message = cast(Message, callback.message)

	await message.edit_text(
		"Виберіть сферу діяльності",
		reply_markup=vocation_keyboard(callback.from_user.id)
	)

	await callback.answer()
	await state.set_state(EditCvState.choosing_vocation)

@edit_router.callback_query(EditCv.filter(F.type == EditCvEnum.PHONE_NUMBER), StateFilter(None))
async def edit_phone_number(callback: CallbackQuery, callback_data: EditCv, state: FSMContext):
	message = cast(Message, callback.message)
	await message.edit_text("Введіть новий номер телефону")

	await state.set_state(EditCvState.choosing_phone_number)
	await state.update_data(cv_id=callback_data.cv_id)

@edit_router.message(EditCvState.choosing_phone_number)
async def save_phone_number(message: Message, state: FSMContext):
	text = str(message.text)

	if not validate_phone_number(text):
		return await message.answer("🔴 Невірний формат номера телефону.\n\nДоступні формати: +380631234567 0631234567 0 67 123 45 67 +38-067-123-45-67")
	
	data = await state.get_data()
	cv_id = int(data.get("cv_id", ""))
	
	cv: CVs | None = await CVs.get_or_none(id=cv_id)

	if not cv:
		return await message.answer("🔴 Сталася помилка, резюме не знайдено")
	
	cv.phone_number = text

	await cv.save()
	await state.clear()

	await message.answer("🟢 Номер телефону успішно змінено")

@edit_router.callback_query(EditCv.filter(F.type == EditCvEnum.SALARY), StateFilter(None))
async def edit_min_salary(callback: CallbackQuery, callback_data: EditCv, state: FSMContext):
	message = cast(Message, callback.message)
	await message.edit_text("Введіть мінімальну заробітну плату")

	await state.set_state(EditCvState.choosing_min_salary)
	await state.update_data(cv_id=callback_data.cv_id)

@edit_router.message(EditCvState.choosing_min_salary)
async def edit_desired_salary(message: Message, state: FSMContext):
	min_salary = message.text 

	try:
		min_salary = int(min_salary) #type: ignore
	except ValueError:
		return await message.answer("🔴 Будь ласка, введіть число для мінімальної зарплати")
	await message.answer("Введіть бажану заробітну плату")

	await state.set_state(EditCvState.choosing_desired_salary)
	await state.update_data(min_salary=min_salary)

@edit_router.message(EditCvState.choosing_desired_salary)
async def save_salary(message: Message, state: FSMContext):
	desired_salary = message.text 

	try:
		desired_salary = int(desired_salary) #type: ignore
	except ValueError:
		return await message.answer("🔴 Будь ласка, введіть число для мінімальної зарплати")
	
	data = await state.get_data()
	cv_id = int(data.get("cv_id", ""))
	
	cv: CVs | None = await CVs.get_or_none(id=cv_id)

	if not cv:
		return await message.answer("🔴 Сталася помилка, резюме не знайдено")
	
	cv.min_salary = int(data['min_salary'])
	cv.desired_salary = desired_salary

	await cv.save()
	await state.clear()

	await message.answer("🟢 Заробітну плату збережено")

@edit_router.callback_query(EditCv.filter(F.type == EditCvEnum.VACATION), StateFilter(None))
async def choosing_district_callback(callback: CallbackQuery, callback_data: EditCv, state: FSMContext):
	message = cast(Message, callback.message)

	await message.edit_text(
		"Виберіть сферу діяльності",
		reply_markup=vocation_keyboard(callback.from_user.id)
	)

	await callback.answer()
	await state.set_state(EditCvState.choosing_vocation)
	await state.update_data(cv_id=callback_data.cv_id)

@edit_router.callback_query(EditCvState.choosing_vocation, VocationData.filter())
async def choosing_vocation_callback(callback: CallbackQuery, callback_data: VocationData, state: FSMContext):
	await state.update_data(vocation=callback_data.vocation)

	message = cast(Message, callback.message)

	if callback_data.vocation in (VocationEnum.HOSTESS, VocationEnum.CASHIER, VocationEnum.PURCHASER, VocationEnum.CLEANER, VocationEnum.SECURITY, VocationEnum.ACCOUNTANT, VocationEnum.HOOKAH):
		return await save_vocation(state, message)

	await message.edit_text(
		"Виберіть підвакансію",
		reply_markup=append_back_button(subvocation_keyboard(callback.from_user.id, callback_data.vocation), "choosing_vocation", edit=True)
	)

	await callback.answer()
	await state.set_state(EditCvState.choosing_subvocation)


@edit_router.callback_query(EditCvState.choosing_subvocation, SubvocationData.filter())
async def choosing_subvocation_callback(callback: CallbackQuery, callback_data: SubvocationData, state: FSMContext):
	await state.update_data(subvocation=callback_data.subvocation)

	message = cast(Message, callback.message)
	
	return await save_vocation(state, message)