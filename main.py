import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

SUPABASE_URL = "https://pxjerucwrtluerlccmdn.supabase.co/rest/v1/announcements"

HEADERS = {
    "apikey": "",  # optional (leave blank if it works without it)
    "Authorization": ""  # optional
}

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.command()
async def announcements(ctx):
    try:
        # API request
        url = SUPABASE_URL + "?select=message,link_url&is_visible=eq.true&order=id.desc"
        res = requests.get(url, headers=HEADERS)

        if res.status_code != 200:
            await ctx.send("❌ Failed to fetch announcements.")
            return

        data = res.json()

        if not data:
            await ctx.send("📭 No announcements found.")
            return

        # Build message
        embed = discord.Embed(
            title="📢 Latest Announcements",
            color=discord.Color.blue()
        )

        # Show only latest 5 to avoid spam
        for item in data[:5]:
            message = item.get("message", "No message")
            link = item.get("link_url")

            if link:
                embed.add_field(
                    name="📝 Announcement",
                    value=f"{message}\n🔗 {link}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📝 Announcement",
                    value=message,
                    inline=False
                )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"⚠️ Error: {str(e)}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)