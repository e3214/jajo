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
    channel = member.guild.get_channel(channel_id)
    if not channel:
        print(f"Kanał o ID {channel_id} nie został znaleziony.")
        return

    now = datetime.now(timezone.utc)
    warsaw = pytz.timezone('Europe/Warsaw')

    joined_utc = member.joined_at
    if joined_utc.tzinfo is None:
        joined_utc = joined_utc.replace(tzinfo=timezone.utc)
    joined_local = joined_utc.astimezone(warsaw)
    joined_delta = now - joined_utc

    created_utc = member.created_at
    if created_utc.tzinfo is None:
        created_utc = created_utc.replace(tzinfo=timezone.utc)
    created_local = created_utc.astimezone(warsaw)
    created_delta = now - created_utc

    member_count = member.guild.member_count

    def make_powitanie_text(joined_delta, created_delta, now):
        return (
            f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
            f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#{REGULAMIN_CHANNEL_ID}> :dupka:\n"
            f"ᴍᴀᴍʏ ɴᴀᴅᴢɪᴇᴊᴇ, ᴢ̇ᴇ ᴢᴏꜱᴛᴀɴɪᴇꜱᴢ ᴢ ɴᴀᴍɪ ɴᴀ ᴅᴌᴜᴢ̇ᴇᴊ!\n\n"
            f"`⏰` Dołączono na serwer: `{human_delta(joined_delta)}`\n"
            f"`📅` Konto zostało stworzone: `{human_created(created_delta)}`\n\n"
            f"`👤`  ᴀᴋᴛᴜᴀʟɴɪᴇ ɴᴀ ꜱᴇʀᴡᴇʀᴢᴇ ᴘᴏꜱɪᴀᴅᴀᴍʏ {member_count} ᴏꜱᴏ́ʙ"
            f"\n\n:dupka: ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ - {human_day(now - now)}"
        )

    powitanie_tekst = make_powitanie_text(joined_delta, created_delta, now)

    embed = discord.Embed(
        description=powitanie_tekst,
        color=0xffa500
    )
    avatar_url = member.display_avatar.url if member.display_avatar else member.avatar.url
    pomarancz_logo_url = "https://i.imgur.com/zkHaVeg.png"
    embed.set_author(name=f"Witaj {member.display_name} 👋🏼", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)
    embed.set_image(url=pomarancz_logo_url)

    await channel.send(embed=embed)

# --- KOMENDA /send ---
@bot.tree.command(name="send", description="Wyślij dowolną wiadomość przez bota (tylko dla administratorów)")
@app_commands.describe(message="Treść wiadomości do wysłania (możesz wpisać :nazwa_emotki:)")
async def send(interaction: discord.Interaction, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        return
    try:
        for emoji in bot.emojis:
            message = message.replace(f":{emoji.name}:", str(emoji))
        await interaction.channel.send(message)
        await interaction.response.send_message("✅ Wiadomość została wysłana!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

# --- SYSTEM TICKETÓW (przykład prosty, rozbuduj wg potrzeb) ---
@bot.tree.command(name="ticket", description="Otwórz nowy ticket")
@app_commands.describe(kategoria="Kategoria zgłoszenia")
async def ticket(interaction: discord.Interaction, kategoria: str):
    if not interaction.guild:
        await interaction.response.send_message("Komenda tylko na serwerze.", ephemeral=True)
        return
    if kategoria not in TICKET_CATEGORIES:
        await interaction.response.send_message("Nieprawidłowa kategoria.", ephemeral=True)
        return
    category = discord.utils.get(interaction.guild.categories, id=CONFIG["TICKET_CATEGORY_ID"])
    if not category:
        await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
        return
    staff_role = interaction.guild.get_role(CONFIG["STAFF_ROLE_ID"])
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    ticket_channel = await interaction.guild.create_text_channel(
        name=f"ticket-{interaction.user.name}",
        category=category,
        overwrites=overwrites
    )
    await ticket_channel.send(f"{interaction.user.mention}, Twój ticket został utworzony! {TICKET_CATEGORIES[kategoria]['longdesc']}")
    await interaction.response.send_message(f"Ticket utworzony: {ticket_channel.mention}", ephemeral=True)

# --- READY ---
@bot.event
async def on_ready():
    print(f'✅ {bot.user} jest online!')
    try:
        synced = await bot.tree.sync()
        print(f'Slash commands synced: {len(synced)}')
    except Exception as e:
        print(f'Błąd synchronizacji komend: {e}')

# --- START ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Brak DISCORD_TOKEN w zmiennych środowiskowych!")
bot.run(TOKEN)
