from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.types import CityData, CityEnum, DistrictData
from models.enums import DistrictEnum


def city_keyboard(user_id: int) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for city in CityEnum:
		builder.button(
			text=city.value.title(),
			callback_data=CityData(user_id=user_id, city=city).pack()
		)

	builder.adjust(1)

	return builder.as_markup()


def district_keyboard(user_id: int, city: CityEnum) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	city_index = list(CityEnum).index(city)+1
	for district in DistrictEnum:
		if district.value[1] == city_index or district.value[1] == -1:
			builder.button(
				text=district.value[0].title(),
				callback_data=DistrictData(user_id=user_id, district=district.value[0]).pack()
			)

	builder.adjust(1)

	return builder.as_markup()