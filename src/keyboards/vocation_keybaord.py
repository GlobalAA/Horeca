from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import DetailData, ExtendPublicationDetail, PriceData
from config import config
from models.enums import PriceOptionEnum


def builder_add(builder: InlineKeyboardBuilder, text_data: dict[PriceOptionEnum, str], enum: PriceOptionEnum, value: int, extend: bool = False) -> InlineKeyboardBuilder:
	vip_option = [PriceOptionEnum.VIP, PriceOptionEnum.VIP_PLUS, PriceOptionEnum.VIP_MAX]
	callback_data = PriceData(price_option=enum, price=value).pack()

	if enum in vip_option:
		callback_data = DetailData(price_option=enum, action="")
	if value <= 0 and enum in vip_option:
		callback_data = DetailData(price_option=enum, action="is_vip")

	if extend:
		if enum in vip_option:
			callback_data = ExtendPublicationDetail(price_option=enum, action="").pack()
		if enum in vip_option and value <= 0:
			callback_data = ExtendPublicationDetail(price_option=enum, action="is_vip").pack()

	builder.button(
		text=text_data[enum],
		callback_data=callback_data
	)
	return builder


def vocation_keyboard_price(vip: bool, extend: bool = False, update: bool = False) -> InlineKeyboardMarkup:
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
				builder_add(builder, vip_text_data, enum, 0, extend)
				break
			
			builder_add(builder, text_data, enum, value, extend)
	else:
		builder.button(
			text="Оновити публікацію",
			callback_data=PriceData(price_option=PriceOptionEnum.FREE, price=0).pack()
		)
	
	builder.adjust(1)

	return builder.as_markup()