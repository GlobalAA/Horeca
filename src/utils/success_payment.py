from datetime import datetime, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callbacks.types import PriceData
from models.enums import PriceOptionEnum
from models.models import PaymentHistory, Subscription, User, Vacancies
from utils import save_vacancy


async def success_payment(state: FSMContext, message: Message, user_id: int, callback: CallbackQuery, msg: dict, invoice_id: str):
	user = await User.get_or_none(user_id=user_id).prefetch_related("subscriptions")

	if not user:
		return message.answer("Користувача не знайдено")
	
	data = await state.get_data()
	price_option: PriceOptionEnum = data.get('price_enum', PriceOptionEnum.FREE)
	price_ids = data.get("price_ids", [])
	msg_ids = data.get('msg_ids', [])

	subscriptions : list[PriceOptionEnum] = [sub.status for sub in user.subscriptions] # type: ignore

	tariffs = {
		PriceOptionEnum.VIP: [10],
		PriceOptionEnum.VIP_PLUS: [20, PriceOptionEnum.RESUME_SUB],
		PriceOptionEnum.VIP_MAX: [20, PriceOptionEnum.RESUME_SUB, PriceOptionEnum.VIEW_COMMENTS]
	}

	vip_types = {PriceOptionEnum.VIP, PriceOptionEnum.VIP_PLUS, PriceOptionEnum.VIP_MAX}
	is_vip = any(sub in vip_types for sub in subscriptions)

	publication_time = datetime.now() + timedelta(days=7)

	try:
		defaults = [PriceOptionEnum.ONE_DAY, PriceOptionEnum.ONE_WEEK]

		if not price_option in defaults:
			if is_vip:
				best_match = PriceOptionEnum.FREE
				max_matches = 0
				tariff_additional = []
				for tariff, services in tariffs.items():
					tariff_additional_local = set(s for s in services if isinstance(s, PriceOptionEnum))
					matches = len(tariff_additional_local.intersection(subscriptions))
					if matches > max_matches:
						tariff_additional = tariff_additional_local
						max_matches = matches
						best_match = tariff

				if not best_match and not tariff_additional:
					best_match = PriceOptionEnum.VIP

				options = [PriceOptionEnum.VIP, *tariff_additional]

				delta = timedelta(weeks=4)

				for option in options:
					if not option in subscriptions:
						continue


					subscription: Subscription = await user.subscriptions.filter(status=option).first() #type: ignore
					now = datetime.now()
					if subscription.time_expired:
						now = datetime.now(subscription.time_expired.tzinfo)
					
					if not subscription.time_expired or subscription.time_expired < now:
						subscription.time_expired = now + delta
					else:
						subscription.time_expired += delta


					await subscription.save()

					user.on_week = tariffs[best_match][0]
				await user.save()

			else:
				tariff = tariffs[price_option]

				on_week = tariff[0]
				tariff_additional = [tar for tar in tariff if isinstance(tar, PriceOptionEnum)]

				options = [PriceOptionEnum.VIP, *tariff_additional]

				for option in options:
					await Subscription.create(
						user_id=user.id, 
						status=option,
						time_expired=datetime.now() + timedelta(weeks=4)
					)

				user.on_week = on_week
				await user.save()
		if price_option == PriceOptionEnum.ONE_DAY:
			publication_time = datetime.now() + timedelta(days=1)

		update = data.get('update', False)
		vacancy_id = data.get('update_id', None)

		callback_data = PriceData(price_option=price_option, price=data.get('price', 0))
		
		extend = data.get('extend', False)

		if not extend:
			await save_vacancy(
				update=update,
				vacancy_id=vacancy_id,
				callback_data=callback_data,
				callback=callback,
				user=user,
				message=message,
				state=state,
				data=data,
				publication_time=publication_time
			)
		else:
			vacancies_all = data.get('vacancies', [])
			index = data.get('index', 0)
			vacancy_id = vacancies_all[index]

			vacancy: Vacancies | None = await Vacancies.get_or_none(id=vacancy_id)

			if not vacancy:
				return await callback.answer("Вакансію не знайдено")
			
			delta = publication_time - datetime.now()
			
			vacancy.time_expired += delta
			await callback.answer()

			await message.delete()
			await message.answer(f"🟢 Вакансія продовжена до {vacancy.time_expired.strftime("%d.%m.%Y")}")
			await vacancy.save()

		bot = message.bot

		if not extend:
			for id in price_ids:
				await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=id, reply_markup=None)
			
			for id in msg_ids:
				await bot.delete_message(chat_id=message.chat.id, message_id=id)

		await PaymentHistory.create(
			payment_type=price_option,
			amount=int(msg["amount"]),
			invoice_id=invoice_id,
			user=user
		)

		await state.clear()

	except KeyError:
		await message.answer("Сталася помилка, зверніться до адміністратора!")