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

    avatar_url = member.display_avatar.url if member.display_avatar else member.avatar.url
    pomarancz_logo_url = "https://i.imgur.com/zkHaVeg.png"

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

    member_count = member.guild.member_count

    powitanie_tekst = (
        f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
        f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#1386059827368955934> 🦺\n"
        f"ᴍᴀᴍʏ ɴᴀᴅᴢɪᴇᴊᴇ, ᴢ̇ᴇ ᴢᴏꜱᴛᴀɴɪᴇꜱᴢ ᴢ ɴᴀᴍɪ ɴᴀ ᴅᴌᴜᴢ̇ᴇᴊ!\n\n"
        f"`⏰` Dołączono na serwer: `{human_delta(joined_delta)}`\n"
        f"`📅` Konto zostało stworzone: `{human_created(created_delta)}`\n\n"
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

    msg = await channel.send(embed=embed)

    async def update_embed():
        for _ in range(0, 60):  # aktualizuj przez 60 sekund
            now2 = datetime.now(timezone.utc)
            joined_delta2 = now2 - joined_utc
            powitanie_tekst2 = (
                f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
                f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#1386059827368955934> 🦺\n"
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
            embed2.set_footer(text=f"ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ")
            try:
                await msg.edit(embed=embed2)
            except Exception:
                pass
            await asyncio.sleep(1)

    bot.loop.create_task(update_embed())

# --- TICKETY ---
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
        try:
            category_id = self.values[0]
            category = TICKET_CATEGORIES[category_id]
            guild = interaction.guild
            user = interaction.user

            ticket_name = f"{category['emoji']}-{user.display_name}-{category_id}".replace(" ", "-").lower()[:90]

            existing_ticket = discord.utils.get(guild.channels, name=ticket_name)
            if existing_ticket:
                await interaction.response.send_message(
                    "❌ Masz już otwarty ticket! Zamknij go najpierw.",
                    ephemeral=True
                )
                return

            ticket_category = guild.get_channel(CONFIG["TICKET_CATEGORY_ID"])
            if not ticket_category or not isinstance(ticket_category, discord.CategoryChannel):
                await interaction.response.send_message(
                    "❌ Błąd konfiguracji! Skontaktuj się z administratorem.",
                    ephemeral=True
                )
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True
                ),
                guild.get_role(CONFIG["STAFF_ROLE_ID"]): discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True
                )
            }
            for role_id in CONFIG["EXTRA_ROLES"]:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True,
                        embed_links=True,
                        attach_files=True,
                        read_message_history=True
                    )

            ticket_channel = await guild.create_text_channel(
                name=ticket_name,
                category=ticket_category,
                overwrites=overwrites,
                topic=f"Ticket użytkownika {user.display_name} | Kategoria: {category['label']}"
            )

            embed = discord.Embed(
                title=f"{category['emoji']} {category['label']}",
                description=category['longdesc'],
                color=category['color'],
                timestamp=datetime.now()
            )
            embed.add_field(
                name="📋 Informacje",
                value=f"**Użytkownik:** {user.mention}\n**Kategoria:** {category['label']}\n**ID:** {user.id}",
                inline=False
            )
            embed.set_footer(text="Aby zamknąć ticket, kliknij przycisk poniżej")

            view = TicketControls()
            await ticket_channel.send(embed=embed, view=view)
            await interaction.response.send_message(f"✅ Stworzono ticket! {ticket_channel.mention}", ephemeral=True)
        except Exception as e:
            print(f"Błąd w TicketSelect.callback: {e}")
            await interaction.response.send_message("❌ Wystąpił błąd! Skontaktuj się z administratorem.", ephemeral=True)

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
            color=0xff0000
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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} jest online!')
    guild = bot.get_guild(CONFIG["GUILD_ID"])
    if guild:
        print(f"🔍 Serwer: {guild.name}")
        print(f"👥 Rola staff: {guild.get_role(CONFIG['STAFF_ROLE_ID'])}")
        print("Kategorie na serwerze:")
        for category in guild.categories:
            print(f"{category.name} - {category.id}")
        cat = guild.get_channel(CONFIG["TICKET_CATEGORY_ID"])
        print(f"Obiekt pod TICKET_CATEGORY_ID: {cat} (typ: {type(cat)})")

    try:
        synced = await bot.tree.sync()
        print(f'✅ Zsynchronizowano {len(synced)} komend')
    except Exception as e:
        print(f'❌ Błąd synchronizacji: {e}')

@bot.tree.command(name="ticket-panel", description="Stwórz panel do tworzenia ticketów")
async def ticket_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Nie masz uprawnień!", ephemeral=True)
        return

    embed = discord.Embed(
        title=" TICKETY",
        description=(
            "Witaj, jeżeli potrzebujesz pomocy od naszego zespołu administracji, to wybierz interesującą ciebie kategorie!\n\n"
            "**Cierpliwość.** Prosimy cierpliwie czekać, nie tylko ty czekasz na pomoc. Maksymalny czas na sprawdzenie zgłoszenia to 72h!\n"
            "**Zarząd**. Nie oznaczaj zarządu (Właścicieli/Developerów). Jedyne osoby, które mogą oznaczać zarząd to administracja!\n\n"
            "__Wybierz kategorię, która cię interesuje__"
        ),
        color=0x0099ff
    )

    await interaction.response.send_message(embed=embed, view=TicketView())

# --- KOMENDA /send z obsługą emotek Nitro ---
@bot.tree.command(name="send", description="Wyślij dowolną wiadomość przez bota (tylko dla administratorów)")
@app_commands.describe(message="Treść wiadomości do wysłania (możesz wpisać :nazwa_emotki:)")
async def send(interaction: discord.Interaction, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Nie masz uprawnień do użycia tej komendy!", ephemeral=True)
        return
    try:
        # Sprawdź, czy wiadomość to :nazwa_emotki:
        if message.startswith(":") and message.endswith(":") and len(message) > 2:
            emote_name = message[1:-1]
            # Szukaj emotki po nazwie w dostępnych emotkach bota
            for emoji in bot.emojis:
                if emoji.name == emote_name:
                    await interaction.channel.send(str(emoji))
                    await interaction.response.send_message("✅ Emotka została wysłana!", ephemeral=True)
                    return
            await interaction.response.send_message("❌ Nie znaleziono takiej emotki w dostępnych serwerach bota.", ephemeral=True)
            return

        # Jeśli nie emotka, wyślij normalną wiadomość
        await interaction.channel.send(message)
        await interaction.response.send_message("✅ Wiadomość została wysłana!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Wystąpił błąd: {e}", ephemeral=True)

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ Brak tokenu w zmiennych środowiskowych!")
        exit()
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Błąd: {e}")
