import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("NATU_BOT_TOKEN")
ADMIN_ID = os.getenv("NATU_ADMIN_ID")

LANG, NAME, PHONE, ITEM, PICKUP, DROP, CONFIRM = range(7)

TEXTS = {
    "am": {
        "welcome": "🚚 እንኳን ወደ NATU DELIVERY በደህና መጡ!\nቋንቋ ይምረጡ።",
        "name": "ሙሉ ስምዎን ያስገቡ፦",
        "phone": "ስልክ ቁጥርዎን ያስገቡ፦",
        "item": "ምን እቃ ማስረከብ ይፈልጋሉ?",
        "pickup": "እቃው የሚወሰድበትን ቦታ ይጻፉ፦",
        "drop": "እቃው የሚደርስበትን ቦታ ይጻፉ፦",
        "yes": "✅ አረጋግጥ",
        "no": "❌ ሰርዝ",
        "confirm": "ትዕዛዝዎን ያረጋግጡ፦",
        "done": "✅ ትዕዛዝዎ ተቀብሏል! እናመሰግናለን።",
        "cancel": "ትዕዛዝዎ ተሰርዟል።",
        "invalid": "እባክዎ አረጋግጥ ወይም ሰርዝ ይምረጡ።",
        "labels": ["ስም", "ስልክ", "እቃ", "መነሻ", "መድረሻ"]
    },
    "om": {
        "welcome": "🚚 Gara NATU DELIVERY baga nagaan dhuftan!\nAfaan filadhaa.",
        "name": "Maqaa guutuu keessan galchaa:",
        "phone": "Lakkoofsa bilbilaa keessan galchaa:",
        "item": "Meeshaa maalii erguu barbaaddu?",
        "pickup": "Bakka meeshaan irraa fudhatamu galchaa:",
        "drop": "Bakka meeshaan itti geeffamu galchaa:",
        "yes": "✅ Mirkaneessi",
        "no": "❌ Haqi",
        "confirm": "Ajaja keessan mirkaneessaa:",
        "done": "✅ Ajajni keessan fudhatameera! Galatoomaa.",
        "cancel": "Ajajni keessan haqameera.",
        "invalid": "Maaloo Mirkaneessi ykn Haqi filadhaa.",
        "labels": ["Maqaa", "Bilbila", "Meeshaa", "Bakka fudhannaa", "Bakka geessuu"]
    },
    "en": {
        "welcome": "🚚 Welcome to NATU DELIVERY!\nPlease choose your language.",
        "name": "Please enter your full name:",
        "phone": "Please enter your phone number:",
        "item": "What item do you want to deliver?",
        "pickup": "Enter the pickup location:",
        "drop": "Enter the delivery location:",
        "yes": "✅ Confirm",
        "no": "❌ Cancel",
        "confirm": "Please confirm your order:",
        "done": "✅ Your order has been received! Thank you.",
        "cancel": "Your order has been cancelled.",
        "invalid": "Please choose Confirm or Cancel.",
        "labels": ["Name", "Phone", "Item", "Pickup", "Delivery"]
    }
}


def lang(context):
    return context.user_data.get("lang", "am")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🇪🇹 አማርኛ"],
        ["🇪🇹 Afaan Oromoo"],
        ["🇬🇧 English"]
    ]

    await update.message.reply_text(
        TEXTS["am"]["welcome"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return LANG


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text

    if "Afaan" in choice:
        selected = "om"
    elif "English" in choice:
        selected = "en"
    else:
        selected = "am"

    context.user_data.clear()
    context.user_data["lang"] = selected

    await update.message.reply_text(TEXTS[selected]["name"])
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(TEXTS[lang(context)]["phone"])
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text(TEXTS[lang(context)]["item"])
    return ITEM


async def get_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["item"] = update.message.text
    await update.message.reply_text(TEXTS[lang(context)]["pickup"])
    return PICKUP


async def get_pickup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pickup"] = update.message.text
    await update.message.reply_text(TEXTS[lang(context)]["drop"])
    return DROP


async def get_drop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["drop"] = update.message.text
    d = context.user_data
    t = TEXTS[lang(context)]["labels"]

    summary = (
        f"{t[0]}: {d['name']}\n"
        f"{t[1]}: {d['phone']}\n"
        f"{t[2]}: {d['item']}\n"
        f"{t[3]}: {d['pickup']}\n"
        f"{t[4]}: {d['drop']}"
    )

    context.user_data["summary"] = summary

    keyboard = [[
        TEXTS[lang(context)]["yes"],
        TEXTS[lang(context)]["no"]
    ]]

    await update.message.reply_text(
        summary + "\n\n" + TEXTS[lang(context)]["confirm"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = lang(context)
    answer = update.message.text
    t = TEXTS[language]

    if answer == t["yes"]:
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text="🚚 NEW NATU DELIVERY ORDER\n\n"
                + context.user_data["summary"]
            )

        await update.message.reply_text(t["done"])

    elif answer == t["no"]:
        await update.message.reply_text(t["cancel"])

    else:
        await update.message.reply_text(t["invalid"])
        return CONFIRM

    context.user_data.clear()
    return ConversationHandler.END


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Your Telegram ID: {update.effective_user.id}"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Cancelled. Send /start to begin again."
    )
    context.user_data.clear()
    return ConversationHandler.END


def main():
    if not TOKEN:
        raise RuntimeError("NATU_BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_item)],
            PICKUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pickup)],
            DROP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_drop)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("myid", myid))

    print("NATU DELIVERY BOT IS RUNNING!")
    app.run_polling()


if __name__ == "__main__":
    main()