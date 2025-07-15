from flask import Flask
from threading import Thread
import time
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import pytz

# --- KEEP ALIVE (Flask + Thread) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot działa!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- BLOKADA POWITAŃ PO STARCIE ---
START_TIME = time.time()
welcomed_users = set()

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

REGULAMIN_CHANNEL_ID = 1386059827368955934  # ID kanału regulaminu

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
    # Dodaj pozostałe kategorie według potrzeb...
}

def human_delta(delta):
    hours = int(delta.total_seconds() // 3600)
    if hours == 1:
        return "1 godzina temu"
    else:
        return f"{hours} godzin temu"

def human_created(delta):
    months = int(delta.days // 30)
    if months == 1:
        return "1 miesiąc temu"
    else:
        return f"{months} miesięcy temu"

def human_day(delta):
    days = delta.days
    if days == 0:
        return "dzisiaj"
    elif days == 1:
        return "wczoraj"
    else:
        return f"{days} dni temu"

# --- POWITALNIA ---
@bot.event
async def on_member_join(member):
    if time.time() - START_TIME < 15:
        return
    if member.guild.id != CONFIG["GUILD_ID"]:
        return
    if member.id in welcomed_users:
        return
    welcomed_users.add(member.id)

    channel_id = 1386060178348179486
    channel = member.guild.get_channel(channel_id)    if not channel:
        print(f"Kanał o ID {channel_id} nie został znaleziony.")
        return

    # Pobierz emotkę :dupka: z serwera
    emoji_dupka = discord.utils.get(member.guild.emojis, name="dupka")
    emoji_dupka_str = f"<:{emoji_dupka.name}:{emoji_dupka.id}>" if emoji_dupka else ":dupka:"

    now = datetime.now(timezone.utc)
    start_time = now  # czas wysłania powitania
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

    member_count = member.guild.member_count

    powitanie_tekst = (
        f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
        f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#{REGULAMIN_CHANNEL_ID}> {emoji_dupka_str}\n"
        f"ᴍᴀᴍʏ ɴᴀᴅᴢɪᴇᴊᴇ, ᴢ̇ᴇ ᴢᴏꜱᴛᴀɴɪᴇꜱᴢ ᴢ ɴᴀᴍɪ ɴᴀ ᴅᴌᴜᴢ̇ᴇᴊ!\n\n"
        f"`⏰` Dołączono na serwer: `{human_delta(joined_delta)}`\n"
        f"`📅` Konto zostało stworzone: `{human_created(created_delta)}`\n\n"
        f"`👤`  ᴀᴋᴛᴜᴀʟɴɪᴇ ɴᴀ ꜱᴇʀᴡᴇʀᴢᴇ ᴘᴏꜱɪᴀᴅᴀᴍʏ {member_count} ᴏꜱᴏ́ʙ"
    )

    embed = discord.Embed(
        description=powitanie_tekst,
        color=0xffa500
    )
    avatar_url = member.display_avatar.url if member.display_avatar else member.avatar.url
    pomarancz_logo_url = "https://i.imgur.com/zkHaVeg.png"
    embed.set_author(name=f"Witaj {member.display_name} 👋🏼", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)
    embed.set_image(url=pomarancz_logo_url)
    embed.set_footer(text=f"{emoji_dupka_str} ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ - {human_day(now - start_time)}")

    msg = await channel.send(embed=embed)

    async def update_embed():
        for _ in range(0, 60):  # aktualizuj przez 60 sekund
            now2 = datetime.now(timezone.utc)
            joined_delta2 = now2 - joined_utc
            powitanie_tekst2 = (
                f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
                f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#{REGULAMIN_CHANNEL_ID}> {emoji_dupka_str}\n"
                f"ᴍᴀᴍʏ ɴᴀᴅᴢɪᴇᴊᴇ, ᴢ̇ᴇ ᴢᴏꜱᴛᴀɴɪᴇꜱᴢ ᴢ ɴᴀᴍɪ ɴᴀ ᴅᴌᴜᴢ̇ᴇᴊ!\n\n"
                f"`⏰` Dołączono na serwer: `{human_delta(joined_delta2)}`\n"
                f"`📅` Konto zostało stworzone: `{human_created(created_delta)}`\n\n"
                f"`👤`  ᴀᴋᴛᴜᴀʟɴɪᴇ ɴᴀ ꜱᴇʀᴡᴇʀᴢᴇ ᴘᴏꜱɪᴀᴅᴀᴍʏ {member_count} ᴏꜱᴏ́ʙ"
            )
            embed2 = discord.Embed(
                description=powitanie_tekst2,
                color=0xffa500
            )
            embed2.set_author(name=f"Witaj {member.display_name} 👋🏼", icon_url=avatar_url)
            embed2.set_thumbnail(url=avatar_url)
            embed2.set_image(url=pomarancz_logo_url)
            embed2.set_footer(text=f"{emoji_dupka_str} ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ - {human_day(now2 - start_time)}")
            try:
                await msg.edit(embed=embed2)
            except Exception:
                pass
            await asyncio.sleep(1)

    bot.loop.create_task(update_embed())

# --- TICKETY, /send itd. ---
# (reszta kodu ticketów i komendy /send z poprzednich wersji – jeśli chcesz, mogę wkleić całość)

# ...tutaj wklej kod ticketów i komendy /send...

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ Brak tokenu w zmiennych środowiskowych!")
        exit()
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Błąd: {e}")
