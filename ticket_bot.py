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
    "TICKET_CATEGORY_ID": 1386061124356804748,  # ID kategorii ticketów
    "STAFF_ROLE_ID": 1386072963832352779,       # ID roli administracji
    "LOG_CHANNEL_ID": None,
    "GUILD_ID": 1386058522030117004,            # ID Twojego serwera
    "EXTRA_ROLES": [
        1386072859717144696,
        1386072749658603602,
        1386072657795219638,
        1386072509715058759,
        1386072406346698904
    ]
}

REGULAMIN_CHANNEL_ID = 1386059827368955934  # ID kanału regulaminu
POWITANIA_CHANNEL_ID = 1386060178348179486  # ID kanału powitań

TICKET_CATEGORIES = {
    "report_user": {
        "label": "Zgłoś użytkownika",
        "description": "Kliknij jeśli chcesz zgłosić użytkownika",
        "emoji": "⚠️",
        "color": 0x2ecc40,  # zielony
        "longdesc": (
            "Witaj! Jeżeli chcesz zgłosić użytkownika łamiącego regulamin, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz dokładnie sytuację i podaj nick osoby, którą zgłaszasz.__"
        ),
        "slug": "zglos_uzytkownika"
    },
    "backup": {
        "label": "Backup",
        "description": "Kliknij jeśli chcesz backup",
        "emoji": "💾",
        "color": 0x2ecc40,
        "longdesc": (
            "Witaj! Jeżeli potrzebujesz backupu swojej działki, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Podaj nazwę działki i powód prośby o backup.__"
        ),
        "slug": "backup"
    },
    "forgot_password": {
        "label": "Zapomniane hasło",
        "description": "Kliknij jeśli chcesz odzyskać hasło",
        "emoji": "🔐",
        "color": 0x2ecc40,
        "longdesc": (
            "Witaj! Jeżeli zapomniałeś hasła do konta, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Podaj swój nick oraz wszelkie informacje, które mogą pomóc w weryfikacji.__"
        ),
        "slug": "zapomniane_haslo"
    },
    "unban_appeal": {
        "label": "Odwołanie od kary",
        "description": "Kliknij jeśli chcesz się odwołać od kary",
        "emoji": "🛡️",
        "color": 0x2ecc40,
        "longdesc": (
            "Witaj! Jeżeli chcesz się odwołać od bana lub mute, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz powód odwołania i podaj swój nick.__"
        ),
        "slug": "odwolanie_od_kary"
    },
    "payment_issue": {
        "label": "Problem z płatnością",
        "description": "Kliknij jeśli masz problem z płatnością",
        "emoji": "💳",
        "color": 0x2ecc40,
        "longdesc": (
            "Witaj! Jeżeli masz problem z płatnością lub zakupem, wybierz tę kategorię.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz dokładnie problem i podaj szczegóły transakcji.__"
        ),
        "slug": "problem_z_platnoscia"
    },
    "other": {
        "label": "Inne",
        "description": "Inne sprawy",
        "emoji": "❓",
        "color": 0x2ecc40,
        "longdesc": (
            "Witaj! Jeżeli Twoja sprawa nie pasuje do żadnej z powyższych kategorii, wybierz tę opcję.\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd.** Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Opisz swój problem jak najdokładniej.__"
        ),
        "slug": "inne"
    }
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

def powitania_footer(sent_time, warsaw):
    local_sent = sent_time.astimezone(warsaw)
    now = datetime.now(warsaw)
    today = now.date()
    sent_date = local_sent.date()
    days_diff = (today - sent_date).days
    if days_diff == 0:
        return "ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ - dzisiaj"
    elif days_diff == 1:
        return "ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ - wczoraj"
    else:
        return f"ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ - {days_diff} dni temu"

def make_powitanie_text(joined_delta, created_delta, member_count):
    return (
        f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
        f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#{REGULAMIN_CHANNEL_ID}> 🦺\n"
        f"ᴍᴀᴍʏ ɴᴀᴅᴢɪᴇᴊᴇ, ᴢ̇ᴇ ᴢᴏꜱᴛᴀɴɪᴇꜱᴢ ᴢ ɴᴀᴍɪ ɴᴀ ᴅᴌᴜᴢ̇ᴇᴊ!\n\n"
        f"`⏰` Dołączono na serwer: `{human_delta(joined_delta)}`\n"
        f"`📅` Konto zostało stworzone: `{human_created(created_delta)}`\n\n"
        f"`👤`  ᴀᴋᴛᴜᴀʟɴɪᴇ ɴᴀ ꜱᴇʀᴡᴇʀᴢᴇ ᴘᴏꜱɪᴀᴅᴀᴍʏ {member_count} ᴏꜱᴏ́ʙ"
    )

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

    channel = member.guild.get_channel(POWITANIA_CHANNEL_ID)
    if not channel:
        print(f"Kanał o ID {POWITANIA_CHANNEL_ID} nie został znaleziony.")
        return

    now = datetime.now(timezone.utc)
    warsaw = pytz.timezone('Europe/Warsaw')

    joined_utc = member.joined_at
    if joined_utc.tzinfo is None:
        joined_utc = joined_utc.replace(tzinfo=timezone.utc)
    joined_delta = now - joined_utc

    created_utc = member.created_at
    if created_utc.tzinfo is None:
        created_utc = created_utc.replace(tzinfo=timezone.utc)
    created_delta = now - created_utc

    member_count = member.guild.member_count

    powitanie_tekst = make_powitanie_text(joined_delta, created_delta, member_count)

    embed = discord.Embed(description=powitanie_tekst, color=0xffa500)
    avatar_url = member.display_avatar.url if member.display_avatar else member.avatar.url
    pomarancz_logo_url = "https://i.imgur.com/zkHaVeg.png"
    embed.set_author(name=f"Witaj {member.display_name} 👋🏼", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)
    embed.set_image(url=pomarancz_logo_url)
    embed.set_footer(text=powitania_footer(now, warsaw))
    await channel.send(embed=embed)

# --- KOMENDA /send ---
@bot.tree.command(name="send", description="Wyślij dowolną wiadomość przez bota (tylko dla administratorów)")
@app_commands.describe(message="Treść wiadomości do wysłania (możesz wpisać :nazwa_emotki:)")
async def send(interaction: discord.Interaction, message: str):
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Nie masz uprawnień do użycia tej komendy.", ephemeral=True)
        return
    if not interaction.guild:
        await interaction.response.send_message("Komenda tylko na serwerze.", ephemeral=True)
        return
    for emoji in interaction.guild.emojis:
        message = message.replace(f":{emoji.name}:", str(emoji))
    await interaction.response.send_message(message)

# --- SYSTEM TICKETÓW Z PANELEM ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=cat["label"],
                description=cat["description"],
                emoji=cat["emoji"],
                value=cat_id
            )
            for cat_id, cat in TICKET_CATEGORIES.items()
        ]
        super().__init__(
            placeholder="Wybierz kategorię zgłoszenia...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        kategoria = self.values[0]
        await create_ticket(interaction, kategoria)

class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        allowed_roles = [CONFIG["STAFF_ROLE_ID"]] + CONFIG["EXTRA_ROLES"]
        user_roles = [role.id for role in getattr(interaction.user, 'roles', [])]
        if not any(role_id in user_roles for role_id in allowed_roles) and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ Tylko administracja może zamykać tickety!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔒 Zamykanie Ticketu",
            description="Ticket zostanie zamknięty za 5 sekund...",
            color=0xff0000  # czerwony
        )
        await interaction.response.send_message(embed=embed)

        try:
            await asyncio.sleep(5)
            await interaction.channel.delete()
        except Exception as e:
            print(f"Błąd przy usuwaniu kanału: {e}")
            try:
                await interaction.followup.send("❌ Wystąpił błąd przy zamykaniu ticketu. Skontaktuj się z administratorem.", ephemeral=True)
            except Exception as e2:
                print(f"Błąd followup: {e2}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

async def create_ticket(interaction: discord.Interaction, kategoria: str):
    if not interaction.guild:
        await interaction.response.send_message("Komenda tylko na serwerze.", ephemeral=True)
        return
    if kategoria not in TICKET_CATEGORIES:
        await interaction.response.send_message("Nieprawidłowa kategoria.", ephemeral=True)
        return
    category = interaction.guild.get_channel(CONFIG["TICKET_CATEGORY_ID"])
    if not category or not isinstance(category, discord.CategoryChannel):
        await interaction.response.send_message("Nie znaleziono kategorii ticketów.", ephemeral=True)
        return
    staff_role = interaction.guild.get_role(CONFIG["STAFF_ROLE_ID"])
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    for role_id in CONFIG["EXTRA_ROLES"]:
        role = interaction.guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    cat = TICKET_CATEGORIES[kategoria]
    # Nazwa kanału: 🎫-(nick)-(kategoria)
    ticket_channel = await interaction.guild.create_text_channel(
        name=f"🎫-{interaction.user.name}-{cat['slug']}",
        category=category,
        overwrites=overwrites
    )
    embed = discord.Embed(
        title=f"{cat['emoji']} {cat['label']}",
        description=cat['longdesc'],
        color=0x2ecc40,  # zielony
        timestamp=datetime.now()
    )
    embed.add_field(
        name="📋 Informacje",
        value=f"**Użytkownik:** {interaction.user.mention}\n**Kategoria:** {cat['label']}\n**ID:** {interaction.user.id}",
        inline=False
    )
    embed.set_footer(text="Aby zamknąć ticket, kliknij przycisk poniżej")
    view = TicketControls()
    await ticket_channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"✅ Stworzono ticket! {ticket_channel.mention}", ephemeral=True)

@bot.tree.command(name="ticket-panel", description="Stwórz panel do tworzenia ticketów")
async def ticket_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Nie masz uprawnień!", ephemeral=True)
        return

    embed = discord.Embed(
        title="TICKETY",
        description=(
            "Witaj, jeżeli potrzebujesz pomocy od naszego zespołu administracji, to wybierz interesującą ciebie kategorię!\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd**. Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Wybierz kategorię, która cię interesuje__"
        ),
        color=0x2ecc40  # zielony
    )

    await interaction.response.send_message(embed=embed, view=TicketView())

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
