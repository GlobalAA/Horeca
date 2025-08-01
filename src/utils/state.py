from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


async def push_state(state: FSMContext, new_state: State):
	data = await state.get_data()
	history: list = data.get("history", [])
	history.append(new_state.state)
	await state.update_data(history=history)
	await state.set_state(new_state)