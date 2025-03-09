import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Bot tokeni (sizniki kiritilgan)
TOKEN = "8112954505:AAGMrNmHGXJekKeoXpbpENJWJTTfvsx-wuM"

# Bot va dispatcher obyektlari
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Logger sozlamalari
logging.basicConfig(level=logging.INFO)

# Test savollari va ballar
questions = [
    ("Yoshingiz nechida?", ["0–39", "40–49", "50–59", "60+"], [0, 1, 2, 3]),
    ("Jinsingiz?", ["Erkak", "Ayol"], [1, 0]),
    ("Qarindoshlaringizda diabet bormi?", ["Yo‘q", "Ha, 2-darajali", "Ha, 1-darajali"], [0, 1, 2]),
    ("Tana massasi indeksi (BMI)?", ["< 25", "25–30", "> 30"], [0, 1, 3]),
    ("Bel atrofi katta (erkaklar > 94 sm, ayollar > 80 sm)?", ["Yo‘q", "Ha"], [0, 3]),
    ("Kuniga 30 daqiqa harakat qilasizmi?", ["Ha", "Yo‘q"], [0, 2]),
    ("Sizda yuqori qon bosimi bormi?", ["Yo‘q", "Ha"], [0, 2]),
    ("Sizda shifokor tomonidan diabet xavfi aniqlanganmi?", ["Yo‘q", "Ha"], [0, 5])
]

user_scores = {}

# Klaviatura yaratish
def get_keyboard(options):
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*[KeyboardButton(option) for option in options])

# Start komandasi
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_scores[message.chat.id] = {"score": 0, "question_index": 0}
    await ask_question(message)

# Savolni foydalanuvchiga yuborish
async def ask_question(message: types.Message):
    user_id = message.chat.id
    user_data = user_scores[user_id]
    
    current_question = questions[user_data["question_index"]]
    await message.answer(current_question[0], reply_markup=get_keyboard(current_question[1]))

# Foydalanuvchi javoblarini qayta ishlash
@dp.message_handler(lambda message: message.chat.id in user_scores)
async def handle_answer(message: types.Message):
    user_id = message.chat.id
    user_data = user_scores[user_id]

    # Foydalanuvchining javobini ballga aylantirish
    current_question = questions[user_data["question_index"]]
    if message.text in current_question[1]:
        answer_index = current_question[1].index(message.text)
        user_data["score"] += current_question[2][answer_index]

    # Keyingi savol yoki natija chiqarish
    user_data["question_index"] += 1
    if user_data["question_index"] < len(questions):
        await ask_question(message)
    else:
        # Natijani hisoblash
        total_score = user_data["score"]
        risk_level = determine_risk_level(total_score)
        await message.answer(f"Test yakunlandi!\n\nSizning umumiy ballingiz: {total_score}\n\n{risk_level}")
        del user_scores[user_id]  # Testni tugatgandan keyin ma'lumotni o‘chirish

# Diabet xavfini aniqlash
def determine_risk_level(total_score):
    if total_score <= 6:
        return "✅ Diabet xavfi past. Sog‘lom turmush tarzini davom ettiring!"
    elif total_score <= 11:
        return "⚠️ Diabet xavfi bor. Profilaktika choralarini ko‘rish tavsiya etiladi."
    else:
        return "🚨 Diabet xavfi yuqori! Tez orada shifokorga murojaat qiling."

# Botni ishga tushirish
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)