import os
import httpx
import jellyfish
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- CORE LOGIC: R-METHOD (Scrapers) ---

async def check_netlify(name):
    """Checks if name.netlify.app is taken by pinging it."""
    url = f"https://{name.lower()}.netlify.app"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            # If it returns 200 or 403, it exists. 404 means it's likely free.
            return "❌ Taken" if response.status_code != 404 else "✅ Free"
        except httpx.ConnectError:
            return "✅ Free"
        except Exception:
            return "⚠️ Error"

async def check_social(platform_url, name):
    """General scraper for socials like Instagram/X/GitHub."""
    url = platform_url.format(name.lower())
    async with httpx.AsyncClient() as client:
        try:
            # We use a mobile User-Agent to avoid some blocks
            headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"}
            response = await client.get(url, headers=headers, timeout=5.0)
            return "❌ Taken" if response.status_code == 200 else "✅ Free"
        except:
            return "⚠️ Timeout"

# --- CORE LOGIC: G-METHOD (Smart Phonetics) ---

def get_phonetic_risk(name):
    """Uses Soundex to see if the name sounds too much like a big brand."""
    # List of big tech brands to avoid 'Sound-Alikes'
    big_brands = ["Google", "Facebook", "Amazon", "Netflix", "Apple", "Microsoft"]
    user_sound = jellyfish.soundex(name)
    
    risks = []
    for brand in big_brands:
        if jellyfish.soundex(brand) == user_sound:
            risks.append(brand)
    
    return risks

# --- TELEGRAM BOT HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **BrandGuard AI v1.0**\n\n"
        "Send me a name (e.g., 'HyBox') and I will scan the digital universe for you.\n"
        "Brought to you by **Malik Softwebs X HyBox**."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    brand_name = update.message.text.strip()
    wait_msg = await update.message.reply_text(f"🔍 Scanning '{brand_name}'... please wait.")

    # 1. Phonetic Check
    phonetic_conflicts = get_phonetic_risk(brand_name)
    risk_status = "⚠️ Warning" if phonetic_conflicts else "✅ Clean"
    
    # 2. Domain Check
    netlify_status = await check_netlify(brand_name)
    
    # 3. Social Check
    insta_status = await check_social("https://www.instagram.com/{}/", brand_name)
    github_status = await check_social("https://github.com/{}", brand_name)

    report = (
        f"📊 **Brand Report: {brand_name}**\n\n"
        f"🔹 **Phonetic Risk:** {risk_status}\n"
        f"{'   (Sounds like: ' + ', '.join(phonetic_conflicts) + ')' if phonetic_conflicts else '   No major sound-alikes found.'}\n\n"
        f"🌐 **Web Presence:**\n"
        f"• Netlify: {netlify_status}\n"
        f"• GitHub: {github_status}\n"
        f"• Instagram: {insta_status}\n\n"
        f"💡 *Advice: If Netlify is taken but GitHub is free, you can still secure the code namespace!*"
    )

    await wait_msg.edit_text(report, parse_mode='Markdown')

if __name__ == '__main__':
    # Use your Bot Token from @BotFather
    TOKEN = "8697874067:AAFso3HzikgTXPIhRcxtFxXipOmEoR3L3MY"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running...")
    app.run_polling()
