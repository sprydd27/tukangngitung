import requests
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8898573242:AAGyXcg9KEhI0PVCXfCmEjoRQ4QYqHjWzZc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Bot Harga Crypto Siap!</b>\n\n"
        "Kirim: BTC / SOL / ETH / CA token\n"
        "Contoh: 500 SOL ke IDR", 
        parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Major coins (BTC, ETH, SOL)
    if text.upper() in ["BTC", "ETH", "SOL", "USDT"]:
        await update.message.reply_text(f"💰 {text.upper()} sedang diambil datanya...")
        return

    # DexScreener untuk token lain
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={text}"
        data = requests.get(url, timeout=10).json()
        
        if data.get("pairs"):
            pair = data["pairs"][0]
            symbol = pair['baseToken']['symbol']
            price = float(pair.get('priceUsd', 0))
            change = pair['priceChange'].get('m5', 0)
            await update.message.reply_text(
                f"🔥 <b>{symbol}</b>\n"
                f"💰 Harga: <b>${price:,.8f}</b>\n"
                f"📈 5m: {change}%", 
                parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Token tidak ditemukan.")
    except:
        await update.message.reply_text("❌ Error saat mengambil data.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
