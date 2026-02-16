"""
Keyboard menus for the bot.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Testni boshlash")],
            [KeyboardButton(text="📊 Natijalarim")],
            [KeyboardButton(text="📈 Test tahlili")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Get cancel keyboard for FSM flows."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )
    return keyboard
