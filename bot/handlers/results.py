"""
Results handler - show user's test results.
"""
from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime

from keyboards.menu import get_main_menu
from api_client import api_client


router = Router()


@router.message(F.text == "📊 Natijalarim")
async def show_results(message: Message):
    """
    Show user's test results.
    """
    # Check if user is registered
    user = await api_client.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer(
            "❌ Avval /register buyrug'i orqali ro'yxatdan o'ting.",
            reply_markup=get_main_menu()
        )
        return
    
    try:
        # Get user results
        results = await api_client.get_user_results(user['id'])
        
        if not results:
            await message.answer(
                "📊 <b>Sizning natijalaringiz</b>\n\n"
                "Siz hali hech qanday test topshirmadingiz.\n\n"
                "🚀 Testni boshlash tugmasini bosing!",
                parse_mode="HTML",
                reply_markup=get_main_menu()
            )
            return
        
        # Format results
        results_text = "📊 <b>Sizning natijalaringiz</b>\n\n"
        
        for idx, result in enumerate(results, 1):
            submitted_date = datetime.fromisoformat(result['submitted_at'].replace('Z', '+00:00'))
            date_str = submitted_date.strftime("%Y-%m-%d %H:%M")
            
            results_text += f"<b>{idx}. {result['test_title']}</b>\n"
            results_text += f"   📅 Sana: {date_str}\n"
            results_text += f"   ✅ Test: {result['mcq_score']}/{result['mcq_total']}\n"
            results_text += f"   ✍️ Yozma: {result['written_score']}/{result['written_total']}\n"
            results_text += f"   🎯 Jami: {result['total_score']}/45\n\n"
        
        await message.answer(
            results_text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Natijalarni olishda xatolik: {str(e)}",
            reply_markup=get_main_menu()
        )
