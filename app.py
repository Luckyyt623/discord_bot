import discord
from discord.ext import commands
import requests
from flask import Flask
from threading import Thread
import os

# Web server for uptime pinging
app = Flask('')

@app.route('/')
def home():
    return "Slither.io Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="#", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("#server "):
        try:
            content = message.content.split("#server ")[1].strip()
            if ':' not in content:
                await message.channel.send("Please use format `#server ip:port`.")
                return

            ip, port = content.split(":")

            url = "https://slither-realtime-leaderboard.pages.dev/api/leaderboard"
            response = requests.get(url)
            data = response.json()

            if "dataList" not in data:
                await message.channel.send("Failed to fetch leaderboard data.")
                return

            for server in data["dataList"]:
                if server["ipv4"] == ip and str(server["po"]) == port:
                    leaderboard = server.get("leaderboard", [])
                    msg = f"**Slither.io Leaderboard - Server: {ip}:{port}**\n"
                    msg += "```\n"
                    msg += "🏆 Leaderboard 🏆\n"
                    msg += "------------------\n"
                    for p in leaderboard:
                        name = p.get("nk", "Unknown")
                        score = p.get("len", 0)
                        place = p.get("place", "?")
                        msg += f"{place}. {name} - Score: {score}\n"
                    msg += "------------------\n"
                    msg += "```\n"
                    msg += "_Powered by Slither.io Bot_"
                    await message.channel.send(msg)
                    return

            await message.channel.send(f"Server `{ip}:{port}` not found.")
        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

    await bot.process_commands(message)

# Start web server and bot
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))  