"""
Start command handler with inline buttons.
"""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from api_client import api_client

router = Router()


def get_inline_menu(registered: bool = False):
    """Get inline keyboard with buttons"""
    buttons = []
    
    if registered:
        # Registered user - show test button and results
        buttons.append([InlineKeyboardButton(text="✅ Testni boshlash", callback_data="start_test")])
        buttons.append([
            InlineKeyboardButton(text="📊 Natijalarim", callback_data="my_results"),
            InlineKeyboardButton(text="📈 Test tahlili", callback_data="test_analytics")
        ])
        buttons.append([InlineKeyboardButton(text="🔄 Qayta ro'yxatdan o'tish", callback_data="re_register")])
    else:
        # Not registered - show register button
        buttons.append([InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Handle /start command with inline buttons.
    """
    try:
        # Check if user is registered
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        
        if user:
            # User exists
            await message.answer(
                f"👋 <b>Xush kelibsiz, {user['full_name']}!</b>\n\n"
                f"🎓 <b>Bu bot nimalar qila oladi?</b>\n\n"
                f"<i>Assalomu alaykum‼️</i>\n"
                f"<i>@SayxunTeamLC kanalining RASH MODULIDA test "
                f"tekshiruvchi botiga xush kelibsiz ✅</i>\n\n"
                f"🎯 <b>Siz bu bot orqali Milliy Sertifikat testlari ishlab o'z "
                f"natijangizni bilib olishingiz mumkin!</b>\n\n"
                f"Foydalanishni boshlash uchun pastdagi tugmani bosing 🤝🤝",
                reply_markup=get_inline_menu(registered=True),
                parse_mode="HTML"
            )
        else:
            # User doesn't exist
            await message.answer(
                f"👋 <b>Salom, {message.from_user.first_name}!</b>\n\n"
                f"📋 <b>Test ishlash uchun pastdagi tugmani bosing:</b>\n\n"
                f"Ro'yxatdan o'tganingizdan so'ng testlarni ishlashingiz mumkin bo'ladi.",
                reply_markup=get_inline_menu(registered=False),
                parse_mode="HTML"
            )
    except Exception as e:
        # If API fails, still allow registration
        await message.answer(
            f"👋 <b>Salom, {message.from_user.first_name}!</b>\n\n"
            f"📋 <b>Test ishlash uchun pastdagi tugmani bosing:</b>",
            reply_markup=get_inline_menu(registered=False),
            parse_mode="HTML"
        )
