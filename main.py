from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import re
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@amazoneprimedeal"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅Bot Online!\n\nSend me an Amazon affiliate link.")


def resolve_url(short_url: str) -> str:
    """Follow redirects to get the final Amazon product URL."""
    try:
        resp = requests.get(short_url, headers=HEADERS, allow_redirects=True, timeout=10)
        return resp.url
    except Exception:
        return short_url


def scrape_product(url: str):
    """Scrape title, price, and image from an Amazon product page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")

        title_tag = soup.select_one("#productTitle")
        title = title_tag.get_text(strip=True) if title_tag else None

        price = None
        price_selectors = [
            "span.a-price-whole",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "span.a-price > span.a-offscreen",
        ]
        for sel in price_selectors:
            tag = soup.select_one(sel)
            if tag and tag.get_text(strip=True):
                price = tag.get_text(strip=True)
                break

        image = None
        img_tag = soup.select_one("#landingImage") or soup.select_one("#imgBlkFront")
        if img_tag:
            image = img_tag.get("src") or img_tag.get("data-old-hires")

        return title, price, image
    except Exception:
        return None, None, None


async def deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    url_match = re.search(r"https?://\S+", text)
    if not url_match:
        await update.message.reply_text("⚠️ Please send a valid Amazon link.")
        return

    link = url_match.group(0)
    await update.message.reply_text("⏳ Fetching product details...")

    final_url = resolve_url(link)
    title, price, image = scrape_product(final_url)

    if not title:
        title = "🔥 Amazon Best Deal 🔥"

    price_line = f"💰 Price: {price}\n" if price else ""

    caption = f"""🔥 {title} 🔥

{price_line}🛒 Buy Now: {link}

⚡Limited Time Offer
💯Genuine Product
🚚Fast Delivery

#Amazon #Deals #Discount #Shopping"""

    try:
        if image:
            await context.bot.send_photo(chat_id=CHANNEL, photo=image, caption=caption)
        else:
            await context.bot.send_message(chat_id=CHANNEL, text=caption)
        await update.message.reply_text("✅Deal Posted Successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to post: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, deal))

    print("Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()