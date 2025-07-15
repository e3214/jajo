from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot działa!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Na początku pliku:
keep_alive()

import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import pytz

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

CONFIG = {
    "TICKET_CATEGORY_ID": 1386061124356804748,
    "STAFF_ROLE_ID": 1386072963832352779,
    "LOG_CHANNEL_ID": None,
    "GUILD_ID": 1386058522030117004,
    "EXTRA_ROLES": [
        1386072859717144696,
        1386072749658603602,
        1386072657795219638,
        1386072509715058759,
        1386072406346698904
    ]
}

TICKET_CATEGORIES = {
    "report_user": {
        "label": "Zgłoś użytkownika",
        "description": "Kliknij jeśli chcesz zgłosić użytkownika",
        "emoji": "⚠️",
        "color": 0xff4444,
        "longdesc": (
            "Witaj! Jeżeli chcesz zgłosić użytkownika łamiącego regulamin, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz dokładnie sytuację i podaj nick osoby, którą zgłaszasz.__"
        )
    },
    "backup": {
        "label": "Backup",
        "description": "Kliknij jeśli chcesz backup",
        "emoji": "💾",
        "color": 0x4444ff,
        "longdesc": (
            "Witaj! Jeżeli potrzebujesz backupu swojej działki, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Podaj nazwę działki i powód prośby o backup.__"
        )
    },
    "forgot_password": {
        "label": "Zapomniane hasło",
        "description": "Kliknij jeśli chcesz odzyskać hasło",
        "emoji": "🔐",
        "color": 0xffaa44,
        "longdesc": (
            "Witaj! Jeżeli zapomniałeś hasła do konta, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Podaj swój nick oraz wszelkie informacje, które mogą pomóc w weryfikacji.__"
        )
    },
    "unban_appeal": {
        "label": "Odwołanie od kary",
        "description": "Kliknij jeśli chcesz się odwołać od kary",
        "emoji": "🛡️",
        "color": 0x44ff44,
        "longdesc": (
            "Witaj! Jeżeli chcesz się odwołać od bana lub mute, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz powód odwołania i podaj swój nick.__"
        )
    },
    "payment_issue": {
        "label": "Problem z płatnością",
        "description": "Kliknij jeśli masz problem z płatnością",
        "emoji": "💳",
        "color": 0xff44ff,
        "longdesc": (
            "Witaj! Jeżeli masz problem z płatnością lub zakupem, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz dokładnie problem i podaj szczegóły transakcji.__"
        )
    },
    "other": {
        "label": "Inne",
        "description": "Inne sprawy",
        "emoji": "❓",
        "color": 0x888888,
        "longdesc": (
            "Witaj! Jeżeli Twoja sprawa nie pasuje do żadnej z powyższych kategorii, wybierz tę opcję.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz swój problem jak najdokładniej.__"
        )
    }
}

# --- Funkcja do formatowania czasu ---
def human_delta(delta):
    seconds = int(delta.total_seconds())
    years, rem = divmod(seconds, 31536000)
    days, rem = divmod(rem, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if years > 0:
        parts.append(f"{years} rok" + ("ów" if years > 1 else ""))
    if days > 0:
        parts.append(f"{days} dni" if days > 1 else "1 dzień")
    if hours > 0:
        parts.append(f"{hours} godzin" if hours > 1 else "1 godzina")
    if minutes > 0:
        parts.append(f"{minutes} minut" if minutes > 1 else "1 minuta")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} sekund" if seconds > 1 else "1 sekunda")
    return " i ".join(parts) + " temu"

# --- POWITALNIA ---
@bot.event
async def on_member_join(member):
    if member.guild.id != CONFIG["GUILD_ID"]:
        return

    channel_id = 1386060178348179486
    channel = member.guild.get_channel(channel_id)
    if not channel:
        print(f"Kanał o ID {channel_id} nie został znaleziony.")
        return

    avatar_url = member.display_avatar.url if member.display_avatar else member.avatar.url
    pomarancz_logo_url = "https://i.imgur.com/0Q9QZ5F.png"

    now = datetime.now(timezone.utc)
    warsaw = pytz.timezone('Europe/Warsaw')

    joined_utc = member.joined_at
    if joined_utc.tzinfo is None:
        joined_utc = joined_utc.replace(tzinfo=timezone.utc)
    joined_local = joined_utc.astimezone(warsaw)

    created_utc = member.created_at
    if created_utc.tzinfo is None:
        created_utc = created_utc.replace(tzinfo=timezone.utc)
    created_local = created_utc.astimezone(warsaw)

    joined_delta = now - joined_utc
    created_delta = now - created_utc

    joined_ago = human_delta(joined_delta)

    def format_delta(delta, unit):
        if unit == "miesięcy":
            months = int(delta.days // 30)
            return f"{months} miesięcy temu" if months > 1 else "1 miesiąc temu"
        return "?"

    created_str = format_delta(created_delta, "miesięcy")

    member_count = member.guild.member_count

    powitanie_tekst = (
        f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
        f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#1386059827368955934> 🦺\n"
        f"ᴍᴀᴍʏ ɴᴀᴅᴢɪᴇᴊᴇ, ᴢ̇ᴇ ᴢᴏꜱᴛᴀɴɪᴇꜱᴢ ᴢ ɴᴀᴍɪ ɴᴀ ᴅᴌᴜᴢ̇ᴇᴊ!\n\n"
        f"`⏰` Dołączono na serwer: {joined_ago}\n"
        f"`📅` Konto zostało stworzone: {created_str}\n\n"
        f"`👤`  ᴀᴋᴛᴜᴀʟɴɪᴇ ɴᴀ ꜱᴇʀᴡᴇʀᴢᴇ ᴘᴏꜱɪᴀᴅᴀᴍʏ {member_count} ᴏꜱᴏ́ʙ"
    )

    embed = discord.Embed(
        description=powitanie_tekst,
        color=0xffa500
    )
    embed.set_author(name=f"Witaj {member.display_name} 👋🏼", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)
    embed.set_image(url=pomarancz_logo_url)
    embed.set_footer(text=f"ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ")

    await channel.send(embed=embed)

# --- TICKETY ---
# (reszta kodu ticketów bez zmian – jak w poprzednich wersjach)

# ... (tu wklej kod ticketów z poprzednich wersji, bo nie zmieniał się w tej części)

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ Brak tokenu w zmiennych środowiskowych!")
        exit()
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Błąd: {e}")
