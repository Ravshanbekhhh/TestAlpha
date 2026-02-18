"""
Test entry handler - for entering test code and getting test link.
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.markdown import hbold

from states.registration import TestEntryStates
from keyboards.menu import get_main_menu, get_cancel_keyboard
from api_client import api_client
from config import settings


router = Router()


@router.message(F.text == "🚀 Testni boshlash")
async def start_test_entry(message: Message, state: FSMContext):
    """
    Start test code entry process.
    """
    # Check if user is registered
    user = await api_client.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer(
            "❌ Avval /register buyrug'i orqali ro'yxatdan o'ting.",
            reply_markup=get_main_menu()
        )
        return
    
    await state.set_state(TestEntryStates.waiting_for_test_code)
    await message.answer(
        "🔐 <b>Test kodini kiriting</b>\n\n"
        "O'qituvchingizdan olgan test kodini yuboring:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(TestEntryStates.waiting_for_test_code)
async def process_test_code(message: Message, state: FSMContext):
    """Process test code and create session."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "Test kirish bekor qilindi.",
            reply_markup=get_main_menu()
        )
        return
    
    test_code = message.text.strip().upper()
    
    try:
        # Get test from API
        test = await api_client.get_test_by_code(test_code)
        
        if not test:
            await message.answer(
                f"❌ '{test_code}' kodli test topilmadi yoki faol emas.\n\n"
                "Iltimos, kodni tekshirib qayta urinib ko'ring.",
                reply_markup=get_cancel_keyboard()
            )
            return
        
        # Get user
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        
        # Create session
        session = await api_client.create_session(user['id'], test['id'])
        
        if not session:
            await message.answer(
                "❌ Siz bu testni allaqachon topshirgansiz!\n\n"
                "Har bir talaba testni faqat bir marta ishlashi mumkin.",
                reply_markup=get_main_menu()
            )
            await state.clear()
            return
        
        # Generate test link
        test_url = f"{settings.WEB_APP_URL}/static/student/index.html?token={session['session_token']}"
        
        # Build message text
        msg_text = (
            f"✅ <b>Test topildi!</b>\n\n"
            f"📝 {test['title']}\n"
            f"⏱️ Vaqt chegarasi: 1 soat 30 daqiqa\n"
            f"📊 Savollar:\n"
            f"   • Test (1-35): 1-32 savollarda 4 ta, 33-35 savollarda 6 ta variant\n"
            f"   • Yozma (36-37): Har bir savolda a) va b) qismlari bor\n\n"
            f"⚠️ <b>Muhim:</b>\n"
            f"• Havolani ochganingizda taymer boshlanadi\n"
            f"• Testni to'xtatib bo'lmaydi\n"
            f"• Vaqt tugaganda avtomatik topshiriladi\n"
            f"• Faqat bir urinish!\n\n"
            f"Omad tilaymiz! 🍀"
        )
        
        await state.clear()
        
        # Telegram rejects localhost URLs in inline buttons,
        # so use inline keyboard only for real domains
        if "localhost" in test_url or "127.0.0.1" in test_url:
            await message.answer(
                msg_text + f"\n\n<b>🔗 Testni boshlash:</b>\n{test_url}",
                parse_mode="HTML",
                reply_markup=get_main_menu(),
                disable_web_page_preview=True
            )
        else:
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Testni boshlash", web_app=WebAppInfo(url=test_url))]
            ])
            await message.answer(
                msg_text,
                parse_mode="HTML",
                reply_markup=inline_kb
            )
        
    except Exception as e:
        await message.answer(
            f"❌ Xatolik: {str(e)}\n\n"
            "Iltimos, qayta urinib ko'ring yoki yordam uchun murojaat qiling.",
            reply_markup=get_main_menu()
        )
        await state.clear()
