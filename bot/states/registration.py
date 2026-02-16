"""
FSM states for bot conversation flows.
"""
from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration flow."""
    waiting_for_full_name = State()
    waiting_for_surname = State()
    waiting_for_region = State()


class TestEntryStates(StatesGroup):
    """States for test code entry flow."""
    waiting_for_test_code = State()
