"""
Inline button callback handlers
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states.registration import RegistrationStates, TestEntryStates

router = Router()


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
    await callback.message.edit_text(
        "🔑 <b>Test kodini kiriting</b>\n\n"
        "O'qituvchingizdan olgan test kodini yuboring:",
        parse_mode="HTML"
    )
    await state.set_state(TestEntryStates.waiting_for_test_code)
    await callback.answer()


@router.callback_query(F.data == "my_results")
async def callback_my_results(callback: CallbackQuery):
    """Handle my results button"""
    from api_client import api_client
    
    try:
        # First get user by telegram_id to get UUID
        user = await api_client.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.message.edit_text(
                "❌ Siz hali ro'yxatdan o'tmagansiz.\n\n"
                "/start buyrug'ini yuboring.",
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        results = await api_client.get_user_results(user['id'])
        
        if not results:
            await callback.message.edit_text(
                "📊 <b>Natijalar</b>\n\n"
                "Siz hali hech qanday test topshirmadingiz.",
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        # Format results
        text = "📊 <b>Sizning natijalaringiz:</b>\n\n"
        
        for i, result in enumerate(results, 1):
            test_code = result.get('test_code', '')
            text += f"<b>{i}. {result.get('test_title', 'Test')}</b>\n"
            if test_code:
                text += f"   🔑 Kod: {test_code}\n"
            text += f"   📝 Test: {result['mcq_score']}/{result.get('mcq_total', 35)}\n"
            text += f"   ✍️ Yozma: {result['written_score']}/{result.get('written_total', 2)}\n"
            text += f"   ⭐️ Jami: {result['total_score']}\n"
            text += f"   📅 Sana: {result['submitted_at'][:10]}\n\n"
        
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Xatolik yuz berdi: {str(e)}",
            parse_mode="HTML"
        )
        await callback.answer()


@router.callback_query(F.data == "test_analytics")
async def callback_test_analytics(callback: CallbackQuery):
    """Handle test analytics button"""
    await callback.message.edit_text(
        "📈 <b>Test tahlili</b>\n\n"
        "Bu funksiya tez orada qo'shiladi!",
        parse_mode="HTML"
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

