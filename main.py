# =====================================================================================================================
# 🧠 BUGTONGCRYPTIC'S BUGTONG BOT
# Developed by: Sean Martin Tabelisma (@marktinthb)

versionValue = "v0.3.9"
botDeveloper = "MarktinTHB"

# =====================================================================================================================

import os
import re
import discord
import logging
import requests
from datetime import time
from discord.ext import tasks
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime

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
    print(f"✅ {bot.user} is online!")

    if not hasattr(bot, "dailyStarted"):
        dailyBugtong.start()
        bot.dailyStarted = True
        print(f"» dailyBugtong.seq has been initialized.")

    botActivity = discord.Activity(
        type=discord.ActivityType.playing,
        name=f"🧠 bugtong.online | [{versionValue}]",
        state="Try to solve our bugtong of the day!"
    )
    await bot.change_presence(activity=botActivity, status=discord.Status.online)
    print(f"» botActivity.seq has been initialized.")

# =====================================================================================================================
# 📁 ACTION: AUTOCREATES A THREAD (clueThread.seq)
# - Creates a thread in the share your bugtong channel.
# =====================================================================================================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    targetChannel = 1504680610411712562
    print(f"» clueThread.seq has been initialized.")

    if message.channel.id == targetChannel:
        print(f"[CLUE THREAD DEBUGGER] Checking message content: '{message.content}'")

        # Regex: matches (5) or (6, 4, 2) at end of message.
        matchClue = re.search(r'\((.*?)\)', message.content.strip())

        if matchClue:
            thread_name = f"{message.content}・{message.author.display_name}"

            try:
                await message.create_thread(
                    name=thread_name[:100],
                    auto_archive_duration=10080
                )
                print(f"[CLUE THREAD DEBUGGER] Thread '{thread_name}' has been created!")
            except Exception as e:
                print(f"[CLUE THREAD DEBUGGER] Thread creation error: {e}")
        else:
            try:
                await message.delete()
                invalid_msg = f"❌ **Invalid format!** {message.author.mention} Please use `(5)` or `(6, 4, 2)` for your answer length at the end!"
                await message.channel.send(invalid_msg, delete_after=5)
            except Exception as e:
                print(f"[CLUE THREAD DEBUGGER] Invalid format error: {e}")

    await bot.process_commands(message)

# =====================================================================================================================
# 🕓 SCHEDULED POST: SHOW THE BUGTONG OF THE DAY! (dailyBugtong.seq)
# - Displays today's bugtong from #🧠｜bugtong-today.
# =====================================================================================================================

@tasks.loop(time=time(hour=16, minute=00))  # Time is set to: 4:00 PM (UTC) = 12:00 AM (PHT)
async def dailyBugtong():
    try:
        url = (
            f"{BASE_URL}/daily_clues"
            "?select=clue_text,play_date,answer,profiles(display_name)"
            "&order=play_date.desc"
            "&limit=1"
        )

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()

        if not data:
            print("No bugtong data available")
            return

        bugtongClue = data[0]

        # Role and Channel - Variables:
        roleNotifier = 1495465150126493876
        announceChannel = 1495463620082012240

        # Date and Time - Variables:
        rawDate = bugtongClue.get("play_date")
        if not rawDate:
            print("No play_date found in data")
            return

        dayToday = datetime.strptime(rawDate, "%Y-%m-%d").strftime("%A")
        dateToday = datetime.strptime(rawDate, "%Y-%m-%d").strftime("%B %d, %Y")

        # Today's Bugtong - Variables:
        userProfile = bugtongClue.get("profiles", {})
        displayWriter = userProfile.get("display_name", "Unknown Author")
        displayClue = bugtongClue.get("clue_text", "No clue available!")
        displayAnswer = bugtongClue.get("answer", "")
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
        if not displayChannel:
            print(f"Channel {announceChannel} not found!")
            return

        embedClue = await displayChannel.send(content=f"<@&{roleNotifier}>", embed=embed)
        await embedClue.add_reaction("👍")
        await embedClue.add_reaction("👎")
        print(f"✅ Daily bugtong posted successfully for {dateToday}!")

    except requests.RequestException as e:
        print(f"❌ API Error in dailyBugtong: {e}")
    except ValueError as e:
        print(f"❌ Date parsing error: {e}")
    except discord.HTTPException as e:
        print(f"❌ Discord API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error in dailyBugtong: {e}")

# =====================================================================================================================
# 🔒 ADMIN COMMAND: SHOW DAILY BUGTONG COMMAND (?testdaily [channel])
# - Forcefully displays today's bugtong. Use ?testdaily #channel or ?testdaily 123456 to specify channel.
# =====================================================================================================================

@bot.command()
async def testdaily(ctx, channel: discord.TextChannel = None):

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

    if not BASE_URL:
        embed = discord.Embed(
            title="Configuration error!",
            description="**BASE_URL is not configured.**",
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
    defaultChannel = 1495366334081404954

    # Use provided channel or default
    displayChannel = channel or bot.get_channel(defaultChannel)

    if displayChannel is None:
        return await ctx.send("**Target channel not found!**")

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

    embedClue = await displayChannel.send(content=f"<@&{roleNotifier}>", embed=embed)
    await embedClue.add_reaction("👍")
    await embedClue.add_reaction("👎")

# =====================================================================================================================
# 🔒 ADMIN COMMAND: PING COMMAND (?ping)
# - Displays the ping latency of the bot.
# =====================================================================================================================

@bot.command()
async def ping(ctx):

    allowed_roles = [
        1495366331904688230,
        1495366331904688231
    ]

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