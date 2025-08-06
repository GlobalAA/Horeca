from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import DetailData, ExtendPublicationData, PriceData
from config import config
from models.enums import PriceOptionEnum


def builder_add(builder: InlineKeyboardBuilder, text_data: dict[PriceOptionEnum, str], enum: PriceOptionEnum, name: str, value: int, extend: bool = False, index: int = 0) -> InlineKeyboardBuilder:
	vip_option = [PriceOptionEnum.VIP, PriceOptionEnum.VIP_PLUS, PriceOptionEnum.VIP_MAX]
	# callback_data = FinalDataVocation(published=not name == PriceOptionEnum.RESUME_SUB, price_option=enum, price=value).pack()
	callback_data = PriceData(price_option=enum, price=value).pack()
	if enum in vip_option:
		callback_data = DetailData(price_option=enum)

	if extend:
		callback_data = ExtendPublicationData(index=index, extend_type=enum).pack()

	builder.button(
		text=text_data[enum],
		callback_data=callback_data
	)
	return builder


def vocation_keyboard_price(balance: float, vip: bool, extend: bool = False, index: int = 0, update: bool = False) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	text_data = {
		PriceOptionEnum.ONE_DAY: "📰 Розмістити оголошення на один день (50 грн)",
		PriceOptionEnum.ONE_WEEK: "📰 Розмістити оголошення на тиждень (300 грн)",
		PriceOptionEnum.VIP: "🍀 Тариф VIP",
		PriceOptionEnum.VIP_PLUS: "🍀 Тариф VIP+",
		PriceOptionEnum.VIP_MAX: "🍀 Тариф VIP MAX"
	}

	vip_text_data = {
		PriceOptionEnum.VIP: "🍀 Розмістити за допомогою підписки",
	}

	if not update:
		for name, value in config.price_options:
			enum = PriceOptionEnum[name]

			if enum in [PriceOptionEnum.VIEW_COMMENTS, PriceOptionEnum.RESUME_SUB]:
				continue

			if vip and enum == PriceOptionEnum.VIP:
				builder_add(builder, vip_text_data, enum, name, value, extend, index)
				break
			
			if value <= balance:
				builder_add(builder, text_data, enum, name, value, extend, index)
	else:
		builder.button(
			text="Продовжити публікацію",
			# callback_data=FinalDataVocation(published=False, price_option=PriceOptionEnum.FREE, price=0)
			callback_data=PriceData(price_option=PriceOptionEnum.FREE, price=0).pack()
		)
	
	builder.adjust(1)

	return builder.as_markup()