from aiogram import Router

from . import main


def setup_router() -> Router:
	router = Router()
	
	router.include_routers(
		main.router
	)

	return router