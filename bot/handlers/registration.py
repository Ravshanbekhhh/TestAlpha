"""
User registration handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states.registration import RegistrationStates
from keyboards.menu import get_main_menu, get_cancel_keyboard
from api_client import api_client


router = Router()


@router.message(Command("register"))
async def start_registration(message: Message, state: FSMContext):
    """
    Start registration process.
    """
    # Check if already registered
    user = await api_client.get_user_by_telegram_id(message.from_user.id)
    
    if user:
        await message.answer(
            f"Siz allaqachon {user['full_name']} {user['surname']} sifatida ro'yxatdan o'tgansiz.\n\n"
            "Asosiy menyuga o'tish uchun /start buyrug'ini yuboring.",
            reply_markup=get_main_menu()
        )
        return
    
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await message.answer(
        "📝 <b>Ro'yxatdan o'tish</b>\n\n"
        "Iltimos, <b>ismingizni</b> kiriting:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Process full name input."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "Ro'yxatdan o'tish bekor qilindi.",
            reply_markup=get_main_menu()
        )
        return
    
    await state.update_data(full_name=message.text)
    await state.set_state(RegistrationStates.waiting_for_surname)
    await message.answer(
        "Iltimos, <b>familiyangizni</b> kiriting:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(RegistrationStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    """Process surname input."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "Ro'yxatdan o'tish bekor qilindi.",
            reply_markup=get_main_menu()
        )
        return
    
    await state.update_data(surname=message.text)
    await state.set_state(RegistrationStates.waiting_for_region)
    await message.answer(
        "Iltimos, <b>viloyatingizni</b> kiriting:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(RegistrationStates.waiting_for_region)
async def process_region(message: Message, state: FSMContext):
    """Process region input and complete registration."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "Ro'yxatdan o'tish bekor qilindi.",
            reply_markup=get_main_menu()
        )
        return
    
    data = await state.get_data()
    is_re_register = data.get('is_re_register', False)
    
    try:
        if is_re_register:
            # Update existing user
            user = await api_client.update_user(
                telegram_id=message.from_user.id,
                full_name=data['full_name'],
                surname=data['surname'],
                region=message.text
            )
            
            await state.clear()
            await message.answer(
                f"✅ <b>Ma'lumotlaringiz yangilandi!</b>\n\n"
                f"Ism: {user['full_name']} {user['surname']}\n"
                f"Viloyat: {user['region']}\n\n"
                "Testlarni ishlashingiz mumkin! 🎓",
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )
        else:
            # Register new user
            user = await api_client.register_user(
                telegram_id=message.from_user.id,
                full_name=data['full_name'],
                surname=data['surname'],
                region=message.text
            )
            
            await state.clear()
            await message.answer(
                f"✅ <b>Ro'yxatdan o'tish muvaffaqiyatli!</b>\n\n"
                f"Ism: {user['full_name']} {user['surname']}\n"
                f"Viloyat: {user['region']}\n\n"
                "Endi testlarni ishlashingiz mumkin! 🎓",
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )
    except Exception as e:
        await message.answer(
            f"❌ Xatolik: {str(e)}\n\n"
            "Iltimos, /start buyrug'i bilan qayta urinib ko'ring",
            reply_markup=get_main_menu()
        )
        await state.clear()

