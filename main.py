# =====================================================================================================================
# 🧠 BUGTONGCRYPTIC'S BUGTONG BOT [v0.3]
# Developed by: Sean Martin Tabelisma (@marktinthb)
# =====================================================================================================================

import discord
from datetime import datetime
from discord.ext import tasks
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests

# =====================================================================================================================
# ⚙️ LOAD ENV VARIABLES & TOKENS
# =====================================================================================================================

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BASE_URL = os.getenv("BASE_URL")

# =====================================================================================================================
# 💾 DISCORD SETUP
# =====================================================================================================================

handler = logging.FileHandler(
    filename='discord.log',
    encoding='utf-8',
    mode='w'
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix='?',
    intents=intents
)

# =====================================================================================================================
# 📊 SUPABASE CONFIGURATION
# =====================================================================================================================

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# =====================================================================================================================
# 🤖 DISPLAY BOT STATUS ONCE READY
# =====================================================================================================================

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    if not dailyBugtong.is_running():
        dailyBugtong.start()
        print(f"» dailyBugtong.seq is initialized.")

# =====================================================================================================================
# 🕓 SCHEDULED POST: SHOW THE BUGTONG OF THE DAY! (dailyBugtong.seq)
# - Displays today's bugtong from #🧠｜bugtong-today.
# =====================================================================================================================

@tasks.loop(time=datetime.strptime("16:00", "%H:%M").time())
async def dailyBugtong():

    url = (
        f"{BASE_URL}/daily_clues"
        "?select=clue_text,play_date,answer,profiles(display_name)"
        "&order=play_date.desc"
        "&limit=1"
    )

    response = requests.get(url, headers=HEADERS)
    data = response.json()

    if not data:
        return

    bugtongClue = data[0]

    # Role and Channel - Variables:
    roleNotifier = 1495465150126493876
    announceChannel = 1495463620082012240

    # Date and Time - Variables:
    rawDate = bugtongClue.get("play_date")
    dayToday = datetime.strptime(rawDate, "%Y-%m-%d").strftime("%A")
    dateToday = datetime.strptime(rawDate, "%Y-%m-%d").strftime("%B %d, %Y")

    # Today's Bugtong - Variables:
    userProfile = bugtongClue.get("profiles") or {}
    displayWriter = userProfile.get("display_name") or "Processing..."
    displayClue = bugtongClue.get("clue_text") or "No clue available!"
    displayAnswer = bugtongClue.get("answer") or ""
    displayAnswerLength = len(displayAnswer.replace(" ", ""))

    embed = discord.Embed(
        title=f"BUGTONG OF THE DAY! · {dayToday} — {dateToday}",
        color=discord.Color.from_str("#c4b5fd")
    )
    embed.set_author(
        name=f"Clue written by: {displayWriter}"
    )
    embed.add_field(
        name=f"{displayClue} ({displayAnswerLength})",
        value="> **How is your experience solving this clue? Rate it below!**",
        inline=False
    )
    embed.set_footer(
        text="Haven't solved it yet? Head to bugtong.online now to solve it.",
        icon_url="https://i.imgur.com/PHDkpkx.png"
    )

    displayChannel = bot.get_channel(announceChannel)
    embedClue = await displayChannel.send(content=f"<@&{roleNotifier}>", embed=embed)
    await embedClue.add_reaction("👍")
    await embedClue.add_reaction("👎")


# =====================================================================================================================
# 🔒 ADMIN COMMAND: SHOW DAILY BUGTONG COMMAND (?testdaily)
# - Forcefully displays today's bugtong from #🧠｜bugtong-today.
# =====================================================================================================================

@bot.command()
async def testdaily(ctx):

    allowed_roles = [
        1495366331904688230,
        1495366331904688231
    ]

    user_roles = [role.id for role in ctx.author.roles]

    if not any(role_id in user_roles for role_id in allowed_roles):
        embed = discord.Embed(
            title="An error has occurred!",
            description="**You are not allowed to do this.**",
            color=discord.Color.from_str("#fab4bc")
        )
        return await ctx.send(embed=embed)

    url = (
        f"{BASE_URL}/daily_clues"
        "?select=clue_text,play_date,answer,profiles(display_name)"
        "&order=play_date.desc"
        "&limit=1"
    )

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        embed = discord.Embed(
            title="Failed to get daily clues!",
            description="**Please try again later.**",
            color=discord.Color.from_str("#fab4bc")
        )
        return await ctx.send(embed=embed)

    data = response.json()

    if not data:
        embed = discord.Embed(
            title="Failed to get daily clues!",
            description="**There are no clues available!**",
            color=discord.Color.from_str("#fab4bc")
        )
        return await ctx.send(embed=embed)

    bugtongClue = data[0]

    # Role and Channel - Variables:
    roleNotifier = 1495465150126493876
    announceChannel = 1495366334081404954

    # Date and Time - Variables:
    rawDate = bugtongClue.get("play_date")
    dayToday = datetime.strptime(rawDate, "%Y-%m-%d").strftime("%A")
    dateToday = datetime.strptime(rawDate, "%Y-%m-%d").strftime("%B %d, %Y")

    # Today's Bugtong - Variables:
    userProfile = bugtongClue.get("profiles") or {}
    displayWriter = userProfile.get("display_name") or "Processing..."
    displayClue = bugtongClue.get("clue_text") or "No clue available!"
    displayAnswer = bugtongClue.get("answer") or ""
    displayAnswerLength = len(displayAnswer.replace(" ", ""))

    embed = discord.Embed(
        title=f"BUGTONG OF THE DAY! · {dayToday} — {dateToday}",
        color=discord.Color.from_str("#c4b5fd")
    )
    embed.set_author(
        name=f"Clue written by: {displayWriter}"
    )
    embed.add_field(
        name=f"{displayClue} ({displayAnswerLength})",
        value="> **How is your experience solving this clue? Rate it below!**",
        inline=False
    )
    embed.set_footer(
        text="Haven't solved it yet? Head to bugtong.online now to solve it.",
        icon_url="https://i.imgur.com/PHDkpkx.png"
    )

    displayChannel = bot.get_channel(announceChannel)
    embedClue = await displayChannel.send(content=f"<@&{roleNotifier}>", embed=embed)
    await embedClue.add_reaction("👍")
    await embedClue.add_reaction("👎")

# =====================================================================================================================
# 🔒 ADMIN COMMAND: PING COMMAND (?ping)
# - Displays the ping latency of the bot.
# =====================================================================================================================

@bot.command()
async def ping(ctx):

    latencyValue = round(bot.latency * 1000)

    # Sets the color based on latency value.
    if latencyValue < 100:
        color = discord.Color.from_str("#a8d0fc")
        status = "Stable"
    elif latencyValue < 200:
        color = discord.Color.from_str("#fce56b")
        status = "Unstable"
    else:
        color = discord.Color.from_str("#fab4bc")
        status = "Critical"

    embed = discord.Embed(
        title="Checking the bot's status...",
        description=f"**Latency:** `{latencyValue} ms`\n**Current Status:** `{status}`",
        color=color
    )

    await ctx.send(embed=embed)

# =====================================================================================================================
# ⚠️ KEEPS THE DISCORD BOT RUNNING (DO NOT MODIFY)
# =====================================================================================================================

bot.run(
    DISCORD_TOKEN,
    log_handler=handler,
    log_level=logging.DEBUG
)