from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@amazonprimedeal"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Online!\n\nSend me an Amazon affiliate link.")

async def deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    post = f"""🔥 AMAZON BEST DEAL 🔥

🛒 Buy Now:
{text}

⚡ Limited Time Offer
💯 Genuine Product
🚚 Fast Delivery

#Amazon #Deals #Discount #Shopping
"""

    await context.bot.send_message(chat_id=CHANNEL, text=post)
    await update.message.reply_text("✅ Deal Posted Successfully!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, deal))

    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
