from aiogram import Router

from . import main
from .admin import admin_router


def setup_router() -> Router:
	router = Router()
	
	router.include_routers(
		main.router,
		admin_router
	)

	return router