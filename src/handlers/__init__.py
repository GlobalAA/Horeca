from aiogram import Router

from . import main
from .admin import admin_router
from .resume_sub import router_sub


def setup_router() -> Router:
	router = Router()
	
	router.include_routers(
		main.router,
		admin_router,
		router_sub
	)

	return router