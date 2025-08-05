from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import ExtendPublicationData, FinalDataVocation
from config import config
from models.enums import PriceOptionEnum


def builder_add(builder: InlineKeyboardBuilder, text_data: dict[PriceOptionEnum, str], enum: PriceOptionEnum, name: str, value: int, extend: bool = False, index: int = 0) -> InlineKeyboardBuilder:
	callback_data = FinalDataVocation(published=not name == PriceOptionEnum.RESUME_SUB, price_option=enum, price=value).pack()

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
		PriceOptionEnum.RESUME_SUB: "📰 Підписатись на розсилку резюме",
		PriceOptionEnum.VIP: "🍀 Розмістити за допомогою підписки",
	}

	if not update:
		for name, value in config.price_options:
			enum = PriceOptionEnum[name]

			if enum == PriceOptionEnum.VIEW_COMMENTS:
				continue
			
			if vip and enum == PriceOptionEnum.VIP:
				builder_add(builder, text_data, enum, name, value, extend, index)
				break
			
			if value <= balance:
				if enum == PriceOptionEnum.VIP:
					continue
				builder_add(builder, text_data, enum, name, value, extend, index)
	else:
		builder.button(
			text="Продовжити публікацію",
			callback_data=FinalDataVocation(published=False, price_option=PriceOptionEnum.FREE, price=0)
		)
	
	builder.adjust(1)

	return builder.as_markup()