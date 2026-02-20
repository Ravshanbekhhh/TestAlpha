"""
Results handler for viewing detailed test results by test code.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import json

from states.registration import ResultStates
from keyboards.menu import get_main_menu, get_cancel_keyboard
from api_client import api_client

router = Router()


@router.message(ResultStates.waiting_for_result_code)
async def process_result_code(message: Message, state: FSMContext):
    """Process entered test code and show detailed results."""
    test_code = message.text.strip().upper()
    data = await state.get_data()
    user_id = data.get("user_id")
    
    if not user_id:
        await state.clear()
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        return
    
    try:
        result = await api_client.get_result_by_test_code(user_id, test_code)
        
        if not result:
            await message.answer(
                f"❌ <b>{test_code}</b> kodi bo'yicha natija topilmadi.\n\n"
                "Test kodini tekshirib, qayta kiriting yoki bekor qiling.",
                parse_mode="HTML",
                reply_markup=get_cancel_keyboard()
            )
            return
        
        # Build detailed results message
        text = f"📊 <b>{result['test_title']}</b>\n"
        text += f"🔑 Kod: {result['test_code']}\n\n"
        
        # MCQ results (1-35)
        text += "<b>📝 Test savollari (1-35):</b>\n"
        mcq_answers = result.get('mcq_answers', [])
        
        # Show in rows of 5 for readability
        for i in range(0, len(mcq_answers), 5):
            row = mcq_answers[i:i+5]
            line = ""
            for a in row:
                icon = "✅" if a['is_correct'] else "❌"
                line += f"{a['question_number']}-{icon}  "
            text += line.strip() + "\n"
        
        text += "\n"
        
        # Written results (36-45)
        written_answers = result.get('written_answers', [])
        if written_answers:
            text += "<b>✍️ Yozma savollar (36-45):</b>\n"
            for wa in written_answers:
                q_num = wa['question_number']
                score = wa['score']
                # score is 0, 1, or 2 (for each sub-part correct)
                if score == 2:
                    icon = "✅✅"
                    detail = "a) ✅  b) ✅"
                elif score == 1:
                    # We know one part is correct, but don't know which without more data
                    icon = "⚠️"
                    detail = "1/2 to'g'ri"
                else:
                    icon = "❌❌"
                    detail = "a) ❌  b) ❌"
                text += f"{q_num}-savol: {detail}\n"
        
        text += "\n"
        
        # Summary
        mcq_score = result.get('mcq_score', 0)
        written_score = result.get('written_score', 0)
        total_score = result.get('total_score', 0)
        
        text += "<b>📈 Umumiy natija:</b>\n"
        text += f"   📝 Test: {mcq_score}/35\n"
        text += f"   ✍️ Yozma: {written_score}/20\n"
        text += f"   ⭐️ Jami: {total_score}\n"
        
        await state.clear()
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        await state.clear()
        await message.answer(
            f"❌ Xatolik yuz berdi: {str(e)}",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
