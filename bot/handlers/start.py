"""
Start command handler with inline buttons.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from api_client import api_client
from keyboards.menu import get_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handle /start command with inline buttons.
    """
    try:
        # Remove any existing reply keyboard first
        await message.answer("⏳", reply_markup=ReplyKeyboardRemove())
        
        # Check if user is registered
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        
        if user:
            # User exists - show main menu
            await message.answer(
                f"👋 <b>Xush kelibsiz, {user['full_name']}!</b>\n\n"
                f"🎓 <b>Bu bot nimalar qila oladi?</b>\n\n"
                f"<i>Assalomu alaykum‼️</i>\n"
                f"<i>@SayxunTeamLC kanalining RASH MODULIDA test "
                f"tekshiruvchi botiga xush kelibsiz ✅</i>\n\n"
                f"🎯 <b>Siz bu bot orqali Milliy Sertifikat testlari ishlab o'z "
                f"natijangizni bilib olishingiz mumkin!</b>\n\n"
                f"Foydalanishni boshlash uchun pastdagi tugmani bosing 🤝🤝",
                reply_markup=get_main_menu(),
                parse_mode="HTML"
            )
        else:
            # User doesn't exist - show register button
            await message.answer(
                f"👋 <b>Salom, {message.from_user.first_name}!</b>\n\n"
                f"📋 <b>Test ishlash uchun pastdagi tugmani bosing:</b>\n\n"
                f"Ro'yxatdan o'tganingizdan so'ng testlarni ishlashingiz mumkin bo'ladi.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
                ]),
                parse_mode="HTML"
            )
    except Exception as e:
        # If API fails, still allow registration
        await message.answer(
            f"👋 <b>Salom, {message.from_user.first_name}!</b>\n\n"
            f"📋 <b>Test ishlash uchun pastdagi tugmani bosing:</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
            ]),
            parse_mode="HTML"
        )
