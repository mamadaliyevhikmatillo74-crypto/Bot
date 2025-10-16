from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,ContextTypes, ConversationHandler, filters)

# <<< Bot token >>>
BOT_TOKEN = "7989613801:AAFZkkq8syBxuMnNnQ8GgX5-chWz75PDzmY"
# @userinfobot orqali olingan ID
ADMIN_ID = 7067985805  

# Bosqichlar uchun constantalar
ASK_NAME, ASK_PHONE, ASK_ISSUE = range(3)
GPT_MODE = range(3, 4)   # Chat GPT rejimi uchun yangi state

import openai
from telegram import Update
from telegram.ext import ContextTypes

# Chat gpt API kaliti
client = openai.OpenAI(
    api_key=
    "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"
)  # openai>=1.0.0 versiyada shunday yoziladi

# Asosiy menyu klaviaturasi
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🛠 Texnik yordam", "🛠 Xizmatlar"],
            ["🆕 Yangiliklar", "📞 Biz bilan bog‘lanish"],
            ["🧠 AI yordam", "📄 Bot haqida"
             ]  # <<< Shu tugmadagi yozuv aniq shunday bo‘lishi kerak
        ],
        resize_keyboard=True)

# Start from conv
async def start_from_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # bu flag global bosh_menyu_handlerga bildiradi: bu start conversation ichidan chaqirildi
    context.chat_data["_handled_by_conv"] = True
    await start(update, context)

# Chat gpt start
async def gpt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["in_gpt_mode"] = True   # ✅ GPT rejimiga kirdik
    await update.message.reply_text(
        "🤖 Siz AI yordam rejimiga kirdingiz.\n"
        "Savollaringizni yozishingiz mumkin.\n\n"
        "🏠 Bosh menyu tugmasi orqali chiqishingiz mumkin.",
        reply_markup=ReplyKeyboardMarkup([["🏠 Bosh menyu"]], resize_keyboard=True)
    )
    return GPT_MODE

# GPT rejimidan chiqish va bosh menyuga qaytish
async def gpt_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data["in_gpt_mode"] = False
    await update.message.reply_text(
        "👋 Siz bosh menyuga qaytdingiz.",
        reply_markup=main_menu_keyboard()  # asosiy menyu tugmalari
    )
    return ConversationHandler.END

# Chat gpt handler 
async def gpt_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    if not context.chat_data.get("in_gpt_mode"):
        return

    user_message = update.message.text.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role":
                "system",
                "content":
                "Siz foydalanuvchiga yordam beruvchi yordamchisiz."
            }, {
                "role": "user",
                "content": user_message
            }])

        reply_text = response.choices[0].message.content.strip()

    except openai.RateLimitError:
        reply_text = "❗Bu funksiya ishlab chiqilmoqda. Tez orada yangilanadi. "

    except Exception as e:
        reply_text = f"⚠️ Xatolik yuz berdi: {str(e)}\n\nAdmin bilan bog‘laning: @unicam_admin"

    # Har qanday holatda ham quyidagi tavsiya qo‘shiladi
    reply_text += "\n\nℹ️ Agar bu javob muammoni hal qilmasa, iltimos admin bilan bog‘laning: @unicam_admin, yoki muammoni batafsil tushuntirib bering !"

    await update.message.reply_text(reply_text)

# Bosh menyu komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user(update.effective_user)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=
        "AgACAgIAAxkBAAIIimiInW37SJqypY8-tKRkfAUNfcgeAALC9zEb5Vs5SGAwX29mkOrhAQADAgADeAADNgQ",
        caption=
        "👋 Salom! Unicam botiga xush kelibsiz.\nPastdan kerakli bo‘limni tanlang:\nYoki: 'Hikvision', 'Hilook', 'KANIHAD', 'Ubiquiti', 'Mikrotik', 'ZkTeco', 'TpLink', 'WiTek', 'RUBEZH', 'Bolid', 'Western Digital'  ga tegishli maxsulot nomini kiriting:",
        reply_markup=main_menu_keyboard()
        # parse_mode="HTML"
    )
    # log_user(user)  # 👈 Foydalanuvchini logga yozamiz
    return ConversationHandler.END


import pandas as pd

# Faylni ochish
df = pd.read_csv("KSS_final_01-09-2025.csv", encoding="utf-8")

import csv

# Mahsulotlarni yuklaymiz (bir marta)
products = []
with open("KSS_final_tavsif_bilan.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        products.append({
            "nomi": row["Nomi"].strip().lower(),
            "narxi": row["Narxi ($)"],
            "tavsif": row["Tavsifi"],
            "rasm_yoli": row["Rasm"]
        })

# search_product handler faqat ConversationHandler tashqarisida ishlasin
async def search_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agar foydalanuvchi GPT rejimida bo‘lsa - bu handler ishlamasin
    if context.chat_data.get("in_gpt_mode"):
        return  

    text = update.message.text.strip().lower()

    found = []
    for p in products:
        if text in p["nomi"]:
            found.append(p)

    if not found:
        await update.message.reply_text(
            "❗️Bu mahsulot topilmadi. Iltimos, to‘liq yoki to‘g‘ri nom kiriting."
        )
        return

    for p in found:
        caption = (f"📦 <b>{p['nomi'].upper()}</b>\n"
                   f"💰 Narxi: {p['narxi']} $\n"
                   f"📝 {p['tavsif']}\n"
                   f"📩 Buyurtma berish: @unicam_admin")
        await update.message.reply_text(caption, parse_mode="HTML")
# xizmatlar bo'limi
async def xizmatlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = ("🛠<b>Xizmatlarimiz:</b>\n\n"
            "🔹 Kamera va xavfsizlik tizimlari o‘rnatish\n"
            "🔹 Face Id va Turniket tizimlari\n"
            "🔹 Domafon va shlakbaum tizimlari\n"
            "🔹 Sun’iy intellektli tizimlar (AI)\n"
            "🔹 Telegram bot yaratish\n"
            "🔹 Web-sayt va internet do‘konlar\n"
            "🔹 Instagram va boshqa ilovalar uchun Target xizmatlari\n"
            "🔹 Onlayn texnik xizmat\n"
            "🔹 Texnologik konsalting\n\n"
            "📩 Qo‘shimcha ma’lumot uchun biz bilan bog‘laning!\n"
            "👨‍💻 @unicam_admin\n"
            "👨‍💻 @Rayimov_m6\n")
    await update.message.reply_text(matn, parse_mode="HTML")

# Texnik yordam boshlanishi
async def tehnik_yordam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 Ismingizni kiriting:\n\n🏠 Bosh menyu tugmasi bilan orqaga qaytishingiz mumkin.",
        reply_markup=ReplyKeyboardMarkup([["🏠 Bosh menyu"]],
                                         resize_keyboard=True))
    return ASK_NAME


# # Telefon raqamni so‘rash
# async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if update.message.text == "🏠 Bosh menyu":
#         context.chat_data["_handled_by_conv"] = True   # 👈 qo‘shildi
#         await start(update, context)
#         return ConversationHandler.END  # <== Qo‘shildi
#     context.user_data["name"] = update.message.text
#     await update.message.reply_text(
#         "📞 Telefon raqamingizni kiriting:(+998200111151)")
#     return ASK_PHONE
# # Telefon so'rovini yuboruvchi funksiya
# Telefon raqamni so‘rash (kontakt orqali)
from telegram import KeyboardButton

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Bosh menyu":
        context.chat_data["_handled_by_conv"] = True
        await start(update, context)
        return ConversationHandler.END
    
    context.user_data["name"] = update.message.text

    # ✅ "Raqamni yuborish" tugmasi
    contact_button = KeyboardButton("📞 Raqamni yuborish", request_contact=True)
    markup = ReplyKeyboardMarkup([[contact_button], ["🏠 Bosh menyu"]], resize_keyboard=True)

    await update.message.reply_text(
        "📱 Iltimos, raqamingizni yuboring:",
        reply_markup=markup
    )
    return ASK_PHONE


# Kontaktni qabul qilish
async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Bosh menyu":
        context.chat_data["_handled_by_conv"] = True
        await start(update, context)
        return ConversationHandler.END

    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text.strip()

    await update.message.reply_text(
        "🛠 Endi muammo tafsilotlarini yozing:",
        reply_markup=ReplyKeyboardMarkup([["🏠 Bosh menyu"]], resize_keyboard=True)
    )
    return ASK_ISSUE

# Muammo so‘rash
async def ask_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Bosh menyu":
        context.chat_data["_handled_by_conv"] = True   # 👈 qo‘shildi
        await start(update, context)
        return ConversationHandler.END  # <== Qo‘shildi
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🛠 Qanday muammo bo‘layapti?")
    return ASK_ISSUE
 # Ma’lumotlarni yakunlash
async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Bosh menyu":
        context.chat_data["_handled_by_conv"] = True   # 👈 qo‘shildi
        await start(update, context)
        return ConversationHandler.END  # <== Qo‘shildi
    context.user_data["issue"] = update.message.text
    data = context.user_data
    message = (f"📩 Texnik yordam so‘rovi:\n"
               f"👤 Ism: {data['name']}\n"
               f"📞 Tel: {data['phone']}\n"
               f"📝 Muammo: {data['issue']}")
    await context.bot.send_message(chat_id=7067985805, text=message)
    await update.message.reply_text(
        "✅ So‘rovingiz qabul qilindi. Tez orada bog‘lanamiz.",
        reply_markup=main_menu_keyboard())
    return ConversationHandler.END




async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"file_id: <code>{file_id}</code>",
                                        parse_mode="HTML")
    elif update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(
            f"🎥 Video file_id:\n<code>{file_id}</code>", parse_mode="HTML")
    else:
        await update.message.reply_text("❗️Faqat rasm yoki video yuboring.")


async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Siz bu buyruqdan foydalana olmaysiz.")
        return

    try:
        with open("users_moslashtirilgan.csv", encoding="utf-8") as f:
            lines = f.readlines()  # Sarlavhani tashlab yubor
            if not lines:
                await update.message.reply_text(
                    "📭 Hozircha foydalanuvchi yo‘q.")
                return

            msg = f"👥 Foydalanuvchilar soni: {len(lines)} ta\n\n"
            for line in lines[1:][
                    -20:]:  # Oxirgi 20 foydalanuvchini ko‘rsatamiz
                user_id, username, full_name, date = line.strip().split(",")
                msg += f"🆔 {user_id} | 👤 {full_name} | 🧷 @{username if username else 'yo‘q'} | 🕒 {date}\n"

            await update.message.reply_text(msg)

    except FileNotFoundError:
        await update.message.reply_text("❗ Foydalanuvchilar fayli topilmadi.")


import os
import csv
from datetime import datetime


def log_user(user):
    file_name = "users_moslashtirilgan.csv"
    file_exists = os.path.exists(file_name)

    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["ID", "Username", "Full Name", "Vaqt"])
        writer.writerow([
            user.id, user.username or "", user.full_name or "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])


# Yangiliklar menyusi
async def post_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     # Yangilik 1: Rasm bilan
    #     await context.bot.send_photo(
    #         chat_id=update.effective_chat.id,
    #         photo="AgACAgIAAxkBAAIBg2h_2fAF-GTRKCsvDIe74GQ-PXLJAALf9jEbKFEAAUh2MsweC6npHAEAAwIAA3kAAzYE",
    #         caption=(
    #             "<b>📢 YANGI MAHSULOT!</b>\n\n"
    #             "🔸 Endi <b>intellektual kamera va turniketlar</b> to‘plami savdoda.\n"
    #             "💬 Batafsil: @unicam_uz"
    #         ),
    #         parse_mode="HTML"
    #     )

    # Yangilik 2: Video bilan
    # await context.bot.send_video(
    #     chat_id=update.effective_chat.id,
    #     video="BAACAgIAAxkBAAIBtWh_5H3_ZidzwYqM1cmFJ2epq9alAAItfgACKFEAAUjDgsW2f3z7czYE",
    #     caption="🎥 Yangi promo video: xavfsizlik tizimlarimiz haqida qisqacha!",
    #     parse_mode="HTML"
    # )

    # Yangilik 3: Faqat matnli
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text=(
    #         "<b>🧠 AI Kamera tizimi</b>\n\n"
    #         "Endi yuzni aniqlovchi AI texnologiyali kameralar bilan xavfsizlikni yangi bosqichga olib chiqing!"
    #     ),
    #     parse_mode="HTML"
    # )

    # Yangilik 4: Yana bir rasm
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=
        "AgACAgIAAxkBAAIIpWiIoZm9O3W8VcRQegXcdQAB5JxhIQACKPsxG7hKSUjo6tmrkhrIwQEAAwIAA3kAAzYE",
        caption=
        "📢 UNICAM GROUPDAN AKSIYA!\n📷 Kamera o‘rnatishda chegirmalar davom etmoqda!\n🚨 Tez, sifatli va arzon – kamera o‘rnatish xizmati\n🔧 Kafolatli xizmat, professional montaj va qo‘llab-quvvatlash\n📸 Bizdan buyurtma bering - 24 soat ichida o‘rnatamiz!\n🎁 Hozir buyurtma qilganlarga – maxsus aksiya narxlari!\n🕑 Aksiya muddatli — imkoniyatni qo‘ldan boy bermang!\n📲 Batafsil: @unicam_admin",
        parse_mode="HTML")

    # 2-usul: Video bilan
    # await context.bot.send_video(
    #     chat_id=update.effective_chat.id,
    #     video=open("video.mp4", "rb"),
    #     caption="🎥 Yangi promo video: xavfsizlik tizimlarimiz haqida qisqacha!",
    #     parse_mode="HTML"
    # )


# Admin bilan bog‘lanish menyusi
async def admin_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Biz bilan bog‘lanish: 👨‍💻@unicam_admin 👨‍💻+998200111151"
    )  

# Bot haqida ma'lumot
async def bot_haqida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>📄 Bot haqida</b>\n\n"
        "🤖 <b>Nomi:</b> Unicam bot\n"
        "📅 <b>Yaratilgan:</b> 2025-yil, iyul\n"
        "👨‍💻 <b>Yaratuvchi:</b> 'Unicam Group' by 'Hikmatillo Mamadaliyev'\n"
        "🔧 <b>Maqsadi:</b> mijozlarga texnik yordam ko'rsatish, yangiliklar va aloqa\n\n"
        "📅 <b>Yangiliklar:</b> Botni yangi versiyasi tez orada ishga tushadi\n"
        # "🤖 Bot 24/7 rejimda ishlaydi\n"
        "🤖 Botda suniy intelekt muammolaringizni yechishda ko'maklashadi\n\n"
        "🤖 Botda qandaydir tehnik xato sezsangiz bizga habar bering. Biz bundan mamnun bo'lamiz☺️\n\n"
        "☎️ <b>Bog‘lanish:</b> @unicam_admin\n",
        parse_mode="HTML")


# Bosh menyu uchun handler
async def bosh_menyu_handler(update: Update,context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.pop("_handled_by_conv", False):
        return
    await start(update, context)


# Har qanday noto‘g‘ri xabar
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❗️ Kechirasiz, noto‘g‘ri buyruq yubordingiz.\nPastdagi menyudan birini tanlang.",
        reply_markup=main_menu_keyboard())


# Asosiy ishga tushirish funksiyasi
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Texnik yordam uchun ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🛠 Texnik yordam$"), tehnik_yordam)],
        states={
            ASK_NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            # ASK_PHONE:[MessageHandler(filters.TEXT & ~filters.COMMAND, ask_issue)],
            ASK_PHONE: [
            MessageHandler(filters.CONTACT, receive_phone),   # ✅ Kontaktni qabul qilish
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)
        ],

            ASK_ISSUE:[MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[MessageHandler(filters.Regex("^🏠 Bosh menyu$"), start_from_conv)],   # 👈 o‘zgardi
    )
    gpt_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🧠 AI yordam"), gpt_start)],
        states={
            GPT_MODE: [
                MessageHandler(filters.Regex("^🏠 Bosh menyu$"), gpt_exit),   # Bosh menyu ishlaydi
                MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_chat_handler),
            ],
        },
    fallbacks=[MessageHandler(filters.Regex("^🏠 Bosh menyu$"), gpt_exit)],
    )

    app.add_handler(conv_handler)
    app.add_handler(gpt_conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", post_news))
    app.add_handler(CommandHandler("help", admin_contact))
    app.add_handler(CommandHandler("support", tehnik_yordam))
    
    app.add_handler(MessageHandler(filters.Regex("^🆕 Yangiliklar$"),  post_news))
    app.add_handler(MessageHandler(filters.Regex("^📞 Biz bilan bog‘lanish$"), admin_contact))
    app.add_handler(MessageHandler(filters.Regex("^🏠 Bosh menyu$"), bosh_menyu_handler))
    app.add_handler(CommandHandler("users", show_users))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, get_file_id))
    app.add_handler(MessageHandler(filters.Regex("(?i)bot haqida"), bot_haqida))
    # app.add_handler(MessageHandler(filters.Regex("^🧠 Chat GPT yordam$"), gpt_chat_handler))
    app.add_handler(MessageHandler(filters.Regex("^🛠 Xizmatlar$"), xizmatlar))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_product))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))
    print("🤖 Bot ishga tushdi...")

    app.run_polling()


# To‘g‘ri ishga tushirish qismi
if __name__ == "__main__":
    main()






