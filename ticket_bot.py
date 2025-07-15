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

load_dotenv()

print("🤖 Discord Ticket Bot - Wersja Replit")
print("=" * 40)
print("Skrypt się uruchomił!")

# Konfiguracja bota (intents)
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

            ticket_name = f"{category['emoji']}-{user.display_name}-{category_id}".replace(" ", "-").replace("ł", "l").replace("ś", "s").replace("ć", "c").replace("ń", "n").replace("ó", "o").replace("ż", "z").replace("ź", "z").replace("ą", "a").replace("ę", "e").replace("Ś", "S").replace("Ł", "L").replace("Ć", "C").replace("Ń", "N").replace("Ó", "O").replace("Ż", "Z").replace("Ź", "Z").replace("Ą", "A").replace("Ę", "E").lower()
            ticket_name = ticket_name[:90]

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

# --- POWITALNIA ---
@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.id == CONFIG["GUILD_ID"]:
        channel_id = 1386060178348179486
        channel = guild.get_channel(channel_id)
        if not channel:
            print(f"Kanał o ID {channel_id} nie został znaleziony.")
            return

        # Profilowe użytkownika
        avatar_url = member.display_avatar.url if member.display_avatar else member.avatar.url

        # Logo PomaranczCraft (bezpośredni link do obrazka)
        pomarancz_logo_url = "https://i.imgur.com/0Q9QZ5F.png"  # <- tutaj jest bezpośredni link do obrazka/logo

        now = datetime.now(timezone.utc)
        joined_delta = now - member.joined_at
        created_delta = now - member.created_at

        def format_delta(delta, unit):
            if unit == "godzin":
                hours = int(delta.total_seconds() // 3600)
                return f"{hours} godziny temu" if hours != 1 else "1 godzinę temu"
            if unit == "miesięcy":
                months = int(delta.days // 30)
                return f"{months} miesięcy temu" if months != 1 else "1 miesiąc temu"
            return "?"

        joined_str = format_delta(joined_delta, "godzin")
        created_str = format_delta(created_delta, "miesięcy")

        member_count = guild.member_count

        if joined_delta < timedelta(hours=24):
            powitanie_data = f"dzisiaj - {member.joined_at.strftime('%H:%M')}"
        elif joined_delta < timedelta(hours=48):
            powitanie_data = f"wczoraj o {member.joined_at.strftime('%H:%M')}"
        else:
            powitanie_data = member.joined_at.strftime('%d.%m.%Y o %H:%M')

        powitanie_tekst = (
            f"ᴡɪᴛᴀᴍʏ ɴᴀ ᴏꜰɪᴄᴊᴀʟɴʏᴍ ᴅɪꜱᴄᴏʀᴅᴢɪᴇ ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ\n"
            f"ᴘᴀᴍɪᴇᴛᴀᴊ ᴀʙʏ ᴘʀᴢᴇᴄᴢʏᴛᴀć <#1386059827368955934> 🦺\n"
            f"ᴍᴀᴍʏ ɴᴀᴅᴢɪᴇᴊᴇ, ᴢ̇ᴇ ᴢᴏꜱᴛᴀɴɪᴇꜱᴢ ᴢ ɴᴀᴍɪ ɴᴀ ᴅᴌᴜᴢ̇ᴇᴊ!\n\n"
            f"`⏰` Dołączono na serwer: {joined_str}\n"
            f"`📅` Konto zostało stworzone: {created_str}\n\n"
            f"`👤`  ᴀᴋᴛᴜᴀʟɴɪᴇ ɴᴀ ꜱᴇʀᴡᴇʀᴢᴇ ᴘᴏꜱɪᴀᴅᴀᴍʏ {member_count} ᴏꜱᴏ́ʙ"
        )

        embed = discord.Embed(
            description=powitanie_tekst,
            color=0xffa500  # pomarańczowy
        )
        embed.set_author(name=f"Witaj {member.display_name} 👋🏼", icon_url=avatar_url)
        embed.set_thumbnail(url=avatar_url)  # lewy górny okrągły avatar
        embed.set_image(url=pomarancz_logo_url)  # duży obrazek na dole

        embed.set_footer(text=f"ᴘᴏᴍᴀʀᴀɴᴄᴢᴄʀᴀꜰᴛ - ᴘᴏᴡɪᴛᴀɴɪᴀ・{powitanie_data}")

        await channel.send(embed=embed)

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

if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")

    if not TOKEN:
        print("❌ Brak tokenu w zmiennych środowiskowych!")
        exit()

    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Błąd: {e}") 
