"""
Inline button callback handlers
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states.registration import RegistrationStates, TestEntryStates
from keyboards.menu import get_main_menu

router = Router()


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Handle main menu button - show main menu"""
    await state.clear()
    from api_client import api_client
    user = await api_client.get_user_by_telegram_id(callback.from_user.id)
    
    if user:
        await callback.message.edit_text(
            f"👋 <b>Xush kelibsiz, {user['full_name']}!</b>\n\n"
            f"🎯 Quyidagi tugmalardan birini tanlang:",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    else:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await callback.message.edit_text(
            "👋 <b>Salom!</b>\n\n"
            "📋 <b>Test ishlash uchun avval ro'yxatdan o'ting:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
            ])
        )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """Handle cancel button during FSM flows"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Bekor qilindi.\n\n"
        "🏠 Asosiy menyuga qaytish uchun tugmani bosing:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "register")
async def callback_register(callback: CallbackQuery, state: FSMContext):
    """Handle registration button"""
    await callback.message.edit_text(
        "📝 <b>Ro'yxatdan o'tish</b>\n\n"
        "Iltimos, <b>ismingizni</b> kiriting:",
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.answer()


@router.callback_query(F.data == "start_test")
async def callback_start_test(callback: CallbackQuery, state: FSMContext):
    """Handle start test button"""
    from keyboards.menu import get_cancel_keyboard
    await callback.message.edit_text(
        "🔑 <b>Test kodini kiriting</b>\n\n"
        "O'qituvchingizdan olgan test kodini yuboring:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(TestEntryStates.waiting_for_test_code)
    await callback.answer()


@router.callback_query(F.data == "my_results")
async def callback_my_results(callback: CallbackQuery, state: FSMContext):
    """Handle my results button - ask for test code"""
    from api_client import api_client
    from states.registration import ResultStates
    from keyboards.menu import get_cancel_keyboard
    
    user = await api_client.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await callback.message.edit_text(
            "❌ Siz hali ro'yxatdan o'tmagansiz.\n\n"
            "/start buyrug'ini yuboring.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
            ])
        )
        await callback.answer()
        return
    
    await state.update_data(user_id=user['id'])
    await state.set_state(ResultStates.waiting_for_result_code)
    await callback.message.edit_text(
        "📊 <b>Natijalarni ko'rish</b>\n\n"
        "🔑 Test kodini kiriting:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()



@router.callback_query(F.data == "test_analytics")
async def callback_test_analytics(callback: CallbackQuery):
    """Handle test analytics button"""
    await callback.message.edit_text(
        "📈 <b>Test tahlili</b>\n\n"
        "Bu funksiya tez orada qo'shiladi!",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "re_register")
async def callback_re_register(callback: CallbackQuery, state: FSMContext):
    """Handle re-registration button"""
    await state.update_data(is_re_register=True)
    await callback.message.edit_text(
        "🔄 <b>Qayta ro'yxatdan o'tish</b>\n\n"
        "Iltimos, <b>yangi ismingizni</b> kiriting:",
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.answer()
