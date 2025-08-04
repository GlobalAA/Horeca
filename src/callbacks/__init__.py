from aiogram import Router

from .cabinet import cabinet_router
from .main import router as main_router
from .profile import edit_router, router_employer, router_seeker


def setup_callbacks() -> Router:
	router = Router()
	
	router.include_routers(
		main_router,
		router_employer,
		router_seeker,
		cabinet_router,
		edit_router
	)

	return router