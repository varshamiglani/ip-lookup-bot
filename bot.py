#!/usr/bin/env python3
"""
Telegram IP Info Bot
- Command: /ip <ip-or-domain>
- Plain message: can be an IP or domain (it will try to resolve)
- /start, /help, /raw (returns raw JSON of last lookup for user)
"""

import asyncio
import logging
import os
import json
import socket
import ipaddress
from typing import Optional, Dict

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ---------- Configuration ----------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # set this in env
API_URL = "http://ip-api.com/json/{ip_or_domain}?fields=status,message,query,reverse,as,org,isp,country,regionName,city,zip,lat,lon,timezone,countryCode,continent,proxy,hosting,query"

# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- In-memory store for raw responses (per user) ----------
LAST_RAW: Dict[int, dict] = {}

# ---------- Helpers ----------
def is_ip(text: str) -> bool:
    try:
        ipaddress.ip_address(text)
        return True
    except ValueError:
        return False

def clean_input(text: str) -> str:
    return text.strip().strip("`").strip()

async def resolve_domain(domain: str) -> Optional[str]:
    try:
        loop = asyncio.get_running_loop()
        infos = await loop.getaddrinfo(domain, None, proto=socket.IPPROTO_TCP)
        for family, _, _, _, sockaddr in infos:
            ip = sockaddr[0]
            return ip
    except Exception as e:
        logger.debug("Domain resolution error for %s: %s", domain, e)
        return None

async def fetch_ip_info(session: aiohttp.ClientSession, query: str) -> dict:
    url = API_URL.format(ip_or_domain=query)
    async with session.get(url, timeout=15) as resp:
        data = await resp.json(content_type=None)
        return data

def format_response(data: dict) -> str:
    if data.get("status") != "success":
        msg = data.get("message") or "Failed to lookup IP"
        return f"⚠️ Lookup failed: {msg}"

    parts = []
    parts.append(f"🔍 Query: `{data.get('query')}`")
    as_info = data.get("as") or ""
    org = data.get("org") or ""
    isp = data.get("isp") or ""
    if as_info or org or isp:
        parts.append(f"🏷 ASN / Org / ISP: {as_info} {org} {isp}".strip())
    country = data.get("country", "")
    region = data.get("regionName", "")
    city = data.get("city", "")
    zipcode = data.get("zip", "")
    parts.append(f"📍 Location: {city}, {region}, {country} {('• '+zipcode) if zipcode else ''}")
    lat = data.get("lat")
    lon = data.get("lon")
    if lat is not None and lon is not None:
        maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        parts.append(f"🗺 Coordinates: {lat}, {lon} — [Map]({maps})")
    tz = data.get("timezone")
    if tz:
        parts.append(f"🕒 Timezone: {tz}")
    cc = data.get("countryCode")
    continent = data.get("continent")
    if cc or continent:
        parts.append(f"🌐 Country code: {cc or '-'} • Continent: {continent or '-'}")
    reverse = data.get("reverse")
    if reverse:
        parts.append(f"🔁 Reverse DNS: `{reverse}`")
    proxy = data.get("proxy")
    hosting = data.get("hosting")
    flags = []
    if proxy:
        flags.append("Proxy")
    if hosting:
        flags.append("Hosting")
    if flags:
        parts.append(f"⚙ Flags: {', '.join(flags)}")
    parts.append("\n_Type `/raw` to get the raw JSON for this lookup._")
    return "\n\n".join(parts)

# ---------- Command Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Hi! Send `/ip <ip-or-domain>` or just type an IP or domain and I'll fetch details.\n\n"
        "Examples:\n"
        "`/ip 8.8.8.8`\n"
        "`/ip example.com`\n\n"
        "I return ASN, ISP, location, timezone, coordinates and a map link."
    )
    await update.message.reply_markdown_v2(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def raw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    raw = LAST_RAW.get(user_id)
    if not raw:
        await update.message.reply_text("No recent lookup found. Use `/ip <ip-or-domain>` or send an IP/domain.")
        return
    pretty = json.dumps(raw, indent=2, ensure_ascii=False)
    if len(pretty) > 3500:
        await update.message.reply_document(document=bytes(pretty, "utf-8"), filename="ip_lookup.json")
    else:
        await update.message.reply_text(f"```\n{pretty}\n```", parse_mode="MarkdownV2")

# ---------- Core message handler ----------
async def handle_ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    text = clean_input(msg.text)
    if text.startswith("/ip"):
        parts = text.split(maxsplit=1)
        if len(parts) == 1:
            await msg.reply_text("Usage: /ip <ip-or-domain>\nExample: `/ip 8.8.8.8`", parse_mode="MarkdownV2")
            return
        text = clean_input(parts[1])
    ip_to_query = None
    if is_ip(text):
        ip_to_query = text
    else:
        await msg.reply_text("Resolving domain to IP... 🔎")
        resolved = await resolve_domain(text)
        if not resolved:
            await msg.reply_text("❌ Could not resolve domain to an IP. Make sure the domain is valid.")
            return
        ip_to_query = resolved
    await msg.reply_text(f"Looking up `{ip_to_query}`... ⏳", parse_mode="MarkdownV2")
    try:
        async with aiohttp.ClientSession() as session:
            data = await fetch_ip_info(session, ip_to_query)
    except asyncio.TimeoutError:
        await msg.reply_text("⚠️ Request timed out. Try again later.")
        return
    except Exception as e:
        logger.exception("Error fetching IP info: %s", e)
        await msg.reply_text("⚠️ An error occurred while fetching data.")
        return
    LAST_RAW[update.effective_user.id] = data
    formatted = format_response(data)
    buttons = []
    if data.get("lat") and data.get("lon"):
        maps = f"https://www.google.com/maps/search/?api=1&query={data['lat']},{data['lon']}"
        buttons.append([InlineKeyboardButton("Open Map", url=maps)])
    if data.get("status") == "success":
        buttons.append([InlineKeyboardButton("Show raw JSON", callback_data="show_raw")])
    markup = InlineKeyboardMarkup(buttons) if buttons else None
    await msg.reply_markdown_v2(formatted, reply_markup=markup, disable_web_page_preview=True)

from telegram.ext import CallbackQueryHandler

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "show_raw":
        user_id = query.from_user.id
        raw = LAST_RAW.get(user_id)
        if not raw:
            await query.edit_message_text("No raw data available.")
            return
        pretty = json.dumps(raw, indent=2, ensure_ascii=False)
        if len(pretty) > 3500:
            await query.message.reply_document(document=bytes(pretty, "utf-8"), filename="ip_lookup.json")
        else:
            await query.message.reply_text(f"```\n{pretty}\n```", parse_mode="MarkdownV2")

# ---------- Main ----------
def main():
    token = TELEGRAM_TOKEN or ""
    if not token:
        raise RuntimeError("Please set TELEGRAM_TOKEN environment variable with your bot token.")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("raw", raw_command))
    app.add_handler(CallbackQueryHandler(callback_query_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_ip_lookup))
    app.add_handler(MessageHandler(filters.Regex(r"^/ip"), handle_ip_lookup))
    logger.info("Starting IP info bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
