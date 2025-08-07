from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import CallbackQuery, Message

from models.enums import PriceOptionEnum
from models.models import Subscription, User


class RoleFilter(BaseFilter):
	def __init__(self, subscription: PriceOptionEnum):
		self.subscription = subscription

	async def __call__(self, message: Message) -> bool:
		user = await User.get_or_none(user_id=message.from_user.id).prefetch_related("subscriptions")
		subscriptions: list[Subscription] = await user.subscriptions.all() #type: ignore
		print(subscriptions)
		return self.subscription in subscriptions

router_sub = Router()

@router_sub.message(Command("search"), RoleFilter(PriceOptionEnum.RESUME_SUB))
async def search_command(message: Message):
	print(1)