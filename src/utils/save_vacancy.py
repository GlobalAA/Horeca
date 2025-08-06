from datetime import datetime, timedelta
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callbacks.types import PriceData
from models.enums import PriceOptionEnum
from models.models import User, Vacancies


async def save_vacancy(update: bool, vacancy_id: int | None, callback_data: PriceData, callback: CallbackQuery, user: User, message: Message, state: FSMContext, data: dict[str, Any], publication_time: datetime, published: bool = False):
	if not update and not vacancy_id:
		subscriptions: list[PriceOptionEnum] = [sub.status for sub in user.subscriptions] # type: ignore

		is_vip = PriceOptionEnum.VIP in subscriptions and callback_data.price_option == PriceOptionEnum.VIP

		resume_sub_in_subscriptions = PriceOptionEnum.RESUME_SUB in subscriptions

		if is_vip:
			if user.on_week > 0:
				user.on_week -= 1
			else:
				await callback.answer()
				return await message.answer("🔴 З вашим тарифом, це зробити неможливо")
		elif callback_data.price_option == PriceOptionEnum.RESUME_SUB:
			if resume_sub_in_subscriptions:
				data['resume_sub'] = True
			else:
				await callback.answer()
				return await message.answer("🔴 З вашим тарифом, це зробити неможливо")
		else:
			if user.balance <  callback_data.price:
				await callback.answer()
				return await message.answer("🔴 На вашому балансі недостатньо коштів для здійснення операції")
			user.balance -= int(callback_data.price)

		await state.clear()

		new_vocation = Vacancies(
			city=data['city'],
			district=data['district'],
			address = data['address'],
			name=data['name'],
			work_schedule=data['work_schedule'],
			issuance_salary=data['issuance_salary'],
			vocation=data['vocation'],
			subvocation=data.get('subvocation', None),
			age_group=data['age_group'],
			experience=data['experience'],
			salary=int(data['salary']),
			rate=data['rate'],
			rate_type=data['rate_type'],
			additional_information=data.get('additional_information', None),
			phone_number=data.get('phone_number', None),
			telegram_link=data.get('telegram_link', None),
			photo_id=data['photo_id'],
			communications=data['communication_data'],
			user=user,
			published=published,
			resume_sub=data.get('resume_sub', False),
			time_expired=publication_time
		)	

		user.last_vacancy_name = data['name']	

		await new_vocation.save()
		await user.save()

		await callback.answer()
		await message.answer(f"🟢 Вакансія збережена!")

	else:
		vacancy = await Vacancies.get_or_none(id=vacancy_id, user=user)

		if not vacancy:
			return await callback.answer("🔴 Вакансію не знайдено")

		vacancy.city = data['city']
		vacancy.district = data['district']
		vacancy.address = data['address']
		vacancy.name = data['name']
		vacancy.work_schedule = data['work_schedule']
		vacancy.issuance_salary = data['issuance_salary']
		vacancy.vocation = data['vocation']
		vacancy.subvocation = data.get('subvocation', None)
		vacancy.age_group = data['age_group']
		vacancy.experience = data['experience']
		vacancy.salary = int(data['salary'])
		vacancy.rate = data['rate']
		vacancy.rate_type = data['rate_type']
		vacancy.additional_information = data.get('additional_information', None)
		vacancy.phone_number = data.get('phone_number', None)
		vacancy.telegram_link = data.get('telegram_link', None)
		vacancy.photo_id = data['photo_id']
		vacancy.communications = data['communication_data']
		vacancy.published = vacancy.published
		vacancy.resume_sub = data.get('resume_sub', False)

		user.last_vacancy_name = data['name']	

		await vacancy.save()
		await user.save()

		await callback.answer()
		await message.reply(f"🟢 Вакансія оновлена!")