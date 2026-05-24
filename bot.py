import requests
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8898573242:AAGyXcg9KEhI0PVCXfCmEjoRQ4QYqHjWzZc"

MAJOR_COINS = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "usdt": "tether"}

def get_major_price(symbol):
    try:
        cg_id = MAJOR_COINS.get(symbol.lower())
        if not cg_id: return None
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
        data = requests.get(url, timeout=10).json()
        return float(data[cg_id]['usd'])
    except:
        return None

def get_dex_price(query):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
        data = requests.get(url, timeout=10).json()
        return data["pairs"][0] if data.get("pairs") else None
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Price Bot Siap!</b>\n\n"
        "Kirim: BTC / SOL / ETH / CA token\n"
        "Contoh: 500 SOL ke IDR\n"
        "Contoh: 2.5 * 150", parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "*" in text or "x" in text.lower():
        await handle_calc(update, text)
        return
    if any(word in text.lower() for word in ["ke", "to", "jadi"]):
        await handle_convert(update, text)
        return

    await handle_price(update, text)

async def handle_price(update: Update, text):
    price = get_major_price(text)
    if price:
        await update.message.reply_text(f"💰 <b>{text.upper()}</b> = <b>${price:,.4f}</b>", parse_mode="HTML")
        return

    pair = get_dex_price(text)
    if pair:
        symbol = pair['baseToken']['symbol']
        price = float(pair.get('priceUsd', 0))
        change = pair['priceChange'].get('m5', 0)
        liq = pair['liquidity'].get('usd', 0)
        msg = f"🔥 <b>{symbol}</b>\n💰 ${price:,.8f}\n📈 5m: {change}%\n💧 Liq: ${liq:,.0f}"
        await update.message.reply_text(msg, parse_mode="HTML")
    else:
        await update.message.reply_text("❌ Tidak ditemukan.")

async def handle_convert(update: Update, text):
    try:
        amount = float(re.findall(r'\d+\.?\d*', text)[0])
        t = text.lower()
        sol_price = get_major_price("sol") or 150
        if "sol" in t:
            usd = amount * sol_price
            idr = usd * 16200
            await update.message.reply_text(f"💱 {amount} SOL ≈ ${usd:,.2f} ≈ Rp {idr:,.0f}")
    except:
        await update.message.reply_text("Contoh: 500 SOL ke IDR")

async def handle_calc(update: Update, text):
    try:
        parts = re.split(r'[\*x]', text.replace(" ", ""))
        result = float(parts[0]) * float(parts[1])
        await update.message.reply_text(f"🔢 Hasil: <b>{result:,.4f}</b>", parse_mode="HTML")
    except:
        await update.message.reply_text("Format: 2.5 * 150")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
