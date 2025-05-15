import discord
from discord.ext import commands
import requests
import logging
import os
import asyncio
from dotenv import load_dotenv
from flask import Flask, send_file
import threading

# Load environment variables from .env file (for local testing)
load_dotenv()

# Set up logging to debug errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SlitherBot')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

# Flask app setup
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Country to IP mapping with approximate coordinates for map and server numbers
country_to_ip = {
    # Africa
    "johannesburg": [
        {"ip": "15.204.53.184", "port": "444", "x": "60%", "y": "80%", "number": "9531"},
        {"ip": "15.204.53.184", "port": "443", "x": "61%", "y": "81%", "number": "6845"},
        {"ip": "15.204.53.184", "port": "475", "x": "62%", "y": "82%", "number": "4209"},
    ],
    "lagos": [
        {"ip": "94.72.180.82", "port": "444", "x": "55%", "y": "70%", "number": "2878"},
        {"ip": "94.72.180.82", "port": "443", "x": "56%", "y": "71%", "number": "7751"},
        {"ip": "94.72.180.82", "port": "475", "x": "57%", "y": "72%", "number": "6960"},
    ],

    # Asia
    "hongkong": [
        {"ip": "43.249.37.55", "port": "444", "x": "80%", "y": "40%", "number": "6946"},
        {"ip": "43.249.37.135", "port": "444", "x": "81%", "y": "41%", "number": "3926"},
        {"ip": "43.249.37.55", "port": "443", "x": "82%", "y": "42%", "number": "2838"},
        {"ip": "43.249.37.135", "port": "443", "x": "83%", "y": "43%", "number": "7442"},
        {"ip": "43.249.37.55", "port": "475", "x": "84%", "y": "44%", "number": "7406"},
        {"ip": "43.249.37.135", "port": "475", "x": "85%", "y": "45%", "number": "8231"},
    ],
    "mumbai": [
        {"ip": "148.113.17.83", "port": "444", "x": "70%", "y": "50%", "number": "8828"},
        {"ip": "148.113.17.85", "port": "444", "x": "71%", "y": "51%", "number": "6405"},
        {"ip": "148.113.20.151", "port": "444", "x": "72%", "y": "52%", "number": "8245"},
        {"ip": "148.113.17.83", "port": "475", "x": "73%", "y": "53%", "number": "7265"},
        {"ip": "148.113.17.85", "port": "443", "x": "74%", "y": "54%", "number": "6029"},
        {"ip": "148.113.20.151", "port": "443", "x": "75%", "y": "55%", "number": "5806"},
        {"ip": "148.113.17.83", "port": "443", "x": "76%", "y": "56%", "number": "4817"},
        {"ip": "148.113.17.85", "port": "475", "x": "77%", "y": "57%", "number": "6361"},
        {"ip": "148.113.20.151", "port": "475", "x": "78%", "y": "58%", "number": "3511"},
    ],
    "india": "mumbai",  # Alias for Mumbai
    "ind": "mumbai",  # Alias for Mumbai
    "nihonbashibakurocho": [
        {"ip": "213.183.62.226", "port": "444", "x": "85%", "y": "35%", "number": "9475"},
        {"ip": "213.183.62.226", "port": "443", "x": "86%", "y": "36%", "number": "7864"},
        {"ip": "213.183.62.226", "port": "475", "x": "87%", "y": "37%", "number": "9663"},
    ],
    "japan": "nihonbashibakurocho",  # Alias for Nihonbashi-bakurochō
    "jp": "nihonbashibakurocho",  # Alias for Nihonbashi-bakurochō
    "singapore": [
        {"ip": "15.235.218.24", "port": "444", "x": "75%", "y": "60%", "number": "2220"},
        {"ip": "15.235.216.115", "port": "444", "x": "76%", "y": "61%", "number": "5315"},
        {"ip": "15.235.216.150", "port": "444", "x": "77%", "y": "62%", "number": "4924"},
        {"ip": "15.235.218.24", "port": "443", "x": "78%", "y": "63%", "number": "7460"},
        {"ip": "15.235.216.115", "port": "443", "x": "79%", "y": "64%", "number": "6250"},
        {"ip": "15.235.216.150", "port": "443", "x": "80%", "y": "65%", "number": "8597"},
        {"ip": "15.235.218.24", "port": "475", "x": "81%", "y": "66%", "number": "2065"},
        {"ip": "15.235.216.115", "port": "475", "x": "82%", "y": "67%", "number": "2928"},
        {"ip": "15.235.216.150", "port": "475", "x": "83%", "y": "68%", "number": "6050"},
    ],

    # Europe
    "bexley": [
        {"ip": "66.165.238.34", "port": "444", "x": "50%", "y": "20%", "number": "4371"},
        {"ip": "66.165.238.34", "port": "475", "x": "51%", "y": "21%", "number": "8344"},
        {"ip": "66.165.238.34", "port": "443", "x": "52%", "y": "22%", "number": "3281"},
    ],
    "frankfurt": [
        {"ip": "57.129.37.42", "port": "444", "x": "53%", "y": "23%", "number": "4263"},
        {"ip": "162.19.235.91", "port": "444", "x": "54%", "y": "24%", "number": "8902"},
        {"ip": "57.129.37.44", "port": "444", "x": "55%", "y": "25%", "number": "2407"},
        {"ip": "57.129.37.42", "port": "475", "x": "56%", "y": "26%", "number": "5608"},
        {"ip": "162.19.235.91", "port": "475", "x": "57%", "y": "27%", "number": "2869"},
        {"ip": "57.129.37.44", "port": "475", "x": "58%", "y": "28%", "number": "8255"},
        {"ip": "57.129.37.42", "port": "443", "x": "59%", "y": "29%", "number": "9637"},
        {"ip": "162.19.235.91", "port": "443", "x": "60%", "y": "30%", "number": "5866"},
        {"ip": "57.129.37.44", "port": "443", "x": "61%", "y": "31%", "number": "6934"},
    ],
    "helsinki": [
        {"ip": "198.244.231.35", "port": "444", "x": "50%", "y": "15%", "number": "6622"},
        {"ip": "198.244.228.230", "port": "444", "x": "51%", "y": "16%", "number": "2891"},
        {"ip": "198.244.231.35", "port": "443", "x": "52%", "y": "17%", "number": "5651"},
        {"ip": "198.244.228.230", "port": "443", "x": "53%", "y": "18%", "number": "4620"},
        {"ip": "198.244.231.35", "port": "475", "x": "54%", "y": "19%", "number": "3442"},
        {"ip": "198.244.228.230", "port": "475", "x": "55%", "y": "20%", "number": "5271"},
        {"ip": "95.216.38.155", "port": "444", "x": "56%", "y": "21%", "number": "3215"},
        {"ip": "95.216.39.140", "port": "444", "x": "57%", "y": "22%", "number": "3739"},
        {"ip": "95.216.39.141", "port": "444", "x": "58%", "y": "23%", "number": "3082"},
        {"ip": "95.216.39.140", "port": "475", "x": "60%", "y": "25%", "number": "5188"},
        {"ip": "95.216.39.141", "port": "443", "x": "61%", "y": "26%", "number": "6873"},
        {"ip": "95.216.38.155", "port": "443", "x": "62%", "y": "27%", "number": "3833"},
        {"ip": "95.216.39.140", "port": "443", "x": "63%", "y": "28%", "number": "4617"},
        {"ip": "95.216.39.141", "port": "475", "x": "64%", "y": "29%", "number": "7989"},
    ],
    "lille": [
        {"ip": "135.125.74.228", "port": "444", "x": "48%", "y": "25%", "number": "4369"},
        {"ip": "135.125.74.229", "port": "444", "x": "49%", "y": "26%", "number": "9668"},
        {"ip": "135.125.74.230", "port": "444", "x": "50%", "y": "27%", "number": "8145"},
        {"ip": "135.125.74.228", "port": "475", "x": "51%", "y": "28%", "number": "8908"},
        {"ip": "135.125.74.229", "port": "443", "x": "52%", "y": "29%", "number": "5443"},
        {"ip": "135.125.74.230", "port": "475", "x": "53%", "y": "30%", "number": "2550"},
        {"ip": "135.125.74.228", "port": "443", "x": "54%", "y": "31%", "number": "8678"},
        {"ip": "135.125.74.229", "port": "475", "x": "55%", "y": "32%", "number": "4886"},
        {"ip": "135.125.74.230", "port": "443", "x": "56%", "y": "33%", "number": "9051"},
    ],
    "madrid": [
        {"ip": "107.155.103.54", "port": "444", "x": "45%", "y": "35%", "number": "2260"},
        {"ip": "107.155.103.54", "port": "443", "x": "46%", "y": "36%", "number": "3402"},
        {"ip": "107.155.103.54", "port": "475", "x": "47%", "y": "37%", "number": "7628"},
    ],
    "strasbourg": [
        {"ip": "92.222.100.202", "port": "444", "x": "52%", "y": "30%", "number": "7806"},
        {"ip": "57.128.20.155", "port": "444", "x": "53%", "y": "31%", "number": "2689"},
        {"ip": "92.222.100.203", "port": "444", "x": "54%", "y": "32%", "number": "9893"},
        {"ip": "92.222.100.202", "port": "443", "x": "55%", "y": "33%", "number": "7563"},
        {"ip": "57.128.20.155", "port": "475", "x": "56%", "y": "34%", "number": "3603"},
        {"ip": "92.222.100.203", "port": "443", "x": "57%", "y": "35%", "number": "6596"},
        {"ip": "92.222.100.202", "port": "475", "x": "58%", "y": "36%", "number": "5834"},
        {"ip": "57.128.20.155", "port": "443", "x": "59%", "y": "37%", "number": "3394"},
        {"ip": "92.222.100.203", "port": "475", "x": "60%", "y": "38%", "number": "8039"},
    ],
    "warsaw": [
        {"ip": "181.41.140.146", "port": "444", "x": "55%", "y": "25%", "number": "8848"},
        {"ip": "181.41.140.170", "port": "444", "x": "56%", "y": "26%", "number": "4571"},
        {"ip": "181.41.140.178", "port": "444", "x": "57%", "y": "27%", "number": "8127"},
        {"ip": "181.41.140.146", "port": "475", "x": "58%", "y": "28%", "number": "4219"},
        {"ip": "181.41.140.170", "port": "475", "x": "59%", "y": "29%", "number": "6561"},
        {"ip": "181.41.140.178", "port": "475", "x": "60%", "y": "30%", "number": "9178"},
        {"ip": "181.41.140.146", "port": "443", "x": "61%", "y": "31%", "number": "6041"},
        {"ip": "181.41.140.170", "port": "443", "x": "62%", "y": "32%", "number": "8979"},
        {"ip": "181.41.140.178", "port": "443", "x": "63%", "y": "33%", "number": "7031"},
    ],
    "europe": "frankfurt",  # Alias for Frankfurt
    "eu": "frankfurt",  # Alias for Frankfurt

    # North America
    "ashburn": [
        {"ip": "57.128.202.109", "port": "444", "x": "30%", "y": "30%", "number": "5574"},
        {"ip": "57.128.202.110", "port": "444", "x": "31%", "y": "31%", "number": "7707"},
        {"ip": "57.128.202.111", "port": "444", "x": "32%", "y": "32%", "number": "9163"},
        {"ip": "57.128.202.109", "port": "443", "x": "33%", "y": "33%", "number": "4368"},
        {"ip": "57.128.202.110", "port": "475", "x": "34%", "y": "34%", "number": "6377"},
        {"ip": "57.128.202.111", "port": "443", "x": "35%", "y": "35%", "number": "6117"},
        {"ip": "57.128.202.109", "port": "475", "x": "36%", "y": "36%", "number": "3336"},
        {"ip": "57.128.202.110", "port": "443", "x": "37%", "y": "37%", "number": "4646"},
        {"ip": "57.128.202.111", "port": "475", "x": "38%", "y": "38%", "number": "4622"},
        {"ip": "102.218.213.17", "port": "444", "x": "39%", "y": "39%", "number": "7376"},
        {"ip": "102.218.213.17", "port": "475", "x": "40%", "y": "40%", "number": "7720"},
        {"ip": "102.218.213.17", "port": "443", "x": "41%", "y": "41%", "number": "8492"},
    ],
    "beauharnois": [
        {"ip": "15.235.51.104", "port": "444", "x": "35%", "y": "25%", "number": "3619"},
        {"ip": "15.235.12.98", "port": "444", "x": "36%", "y": "26%", "number": "4916"},
        {"ip": "148.113.153.83", "port": "444", "x": "37%", "y": "27%", "number": "6495"},
        {"ip": "15.235.51.104", "port": "443", "x": "38%", "y": "28%", "number": "7268"},
        {"ip": "15.235.12.98", "port": "475", "x": "39%", "y": "29%", "number": "8419"},
        {"ip": "148.113.153.83", "port": "475", "x": "40%", "y": "30%", "number": "4872"},
        {"ip": "15.235.51.104", "port": "475", "x": "41%", "y": "31%", "number": "6943"},
        {"ip": "15.235.12.98", "port": "443", "x": "42%", "y": "32%", "number": "3536"},
        {"ip": "148.113.153.83", "port": "443", "x": "43%", "y": "33%", "number": "3991"},
    ],
    "dallas": [
        {"ip": "23.227.195.74", "port": "444", "x": "25%", "y": "35%", "number": "4164"},
        {"ip": "23.29.125.178", "port": "444", "x": "26%", "y": "36%", "number": "8400"},
        {"ip": "23.227.195.74", "port": "475", "x": "27%", "y": "37%", "number": "2761"},
        {"ip": "23.29.125.178", "port": "475", "x": "28%", "y": "38%", "number": "7711"},
        {"ip": "23.227.195.74", "port": "443", "x": "29%", "y": "39%", "number": "9566"},
        {"ip": "23.29.125.178", "port": "443", "x": "30%", "y": "40%", "number": "9259"},
    ],
    "losangeles": [
        {"ip": "45.66.247.6", "port": "444", "x": "20%", "y": "40%", "number": "4717"},
        {"ip": "45.66.247.6", "port": "443", "x": "21%", "y": "41%", "number": "8321"},
        {"ip": "45.66.247.6", "port": "475", "x": "22%", "y": "42%", "number": "4475"},
    ],
    "piscataway": [
        {"ip": "172.93.101.248", "port": "444", "x": "35%", "y": "35%", "number": "null"},  # Legacy map
        {"ip": "172.93.101.248", "port": "443", "x": "36%", "y": "36%", "number": "null"},  # 3000 bot storm
        {"ip": "206.221.176.180", "port": "444", "x": "37%", "y": "37%", "number": "null"},  # 3000 bot storm
        {"ip": "206.221.176.180", "port": "443", "x": "38%", "y": "38%", "number": "null"},  # Empty map
        {"ip": "206.221.176.241", "port": "444", "x": "39%", "y": "39%", "number": "null"},  # Super Battledome
        {"ip": "206.221.176.241", "port": "480", "x": "40%", "y": "40%", "number": "null"},  # Super Battledome Event
        {"ip": "206.221.176.211", "port": "444", "x": "41%", "y": "41%", "number": "null"},  # Paper slither
    ],
    "reston": [
        {"ip": "15.204.212.200", "port": "444", "x": "32%", "y": "32%", "number": "7870"},
        {"ip": "15.204.212.200", "port": "475", "x": "34%", "y": "34%", "number": "4863"},
        {"ip": "15.204.213.229", "port": "443", "x": "35%", "y": "35%", "number": "8335"},
        {"ip": "15.204.212.200", "port": "443", "x": "36%", "y": "36%", "number": "6129"},
        {"ip": "15.204.213.229", "port": "475", "x": "37%", "y": "37%", "number": "8472"},
    ],
    "tampa": [
        {"ip": "192.211.52.146", "port": "444", "x": "28%", "y": "38%", "number": "5724"},
        {"ip": "192.211.52.146", "port": "475", "x": "29%", "y": "39%", "number": "7477"},
        {"ip": "192.211.52.146", "port": "443", "x": "30%", "y": "40%", "number": "9437"},
    ],
    "usa": "ashburn",  # Alias for Ashburn
    "us": "ashburn",  # Alias for Ashburn

    # Oceania
    "sydney": [
        {"ip": "51.161.209.120", "port": "444", "x": "85%", "y": "85%", "number": "7531"},
        {"ip": "51.161.208.162", "port": "444", "x": "86%", "y": "86%", "number": "4305"},
        {"ip": "51.161.209.120", "port": "443", "x": "87%", "y": "87%", "number": "6698"},
        {"ip": "51.161.208.162", "port": "475", "x": "88%", "y": "88%", "number": "2292"},
        {"ip": "51.161.209.120", "port": "475", "x": "89%", "y": "89%", "number": "5728"},
        {"ip": "51.161.208.162", "port": "443", "x": "90%", "y": "90%", "number": "9329"},
    ],

    # South America
    "saopaulo": [
        {"ip": "45.158.39.122", "port": "444", "x": "40%", "y": "75%", "number": "5671"},
        {"ip": "45.158.39.98", "port": "444", "x": "41%", "y": "76%", "number": "9119"},
        {"ip": "45.158.39.114", "port": "444", "x": "42%", "y": "77%", "number": "5196"},
        {"ip": "45.158.39.122", "port": "443", "x": "43%", "y": "78%", "number": "5674"},
        {"ip": "45.158.39.98", "port": "443", "x": "44%", "y": "79%", "number": "9121"},
        {"ip": "45.158.39.114", "port": "475", "x": "45%", "y": "80%", "number": "8880"},
        {"ip": "45.158.39.122", "port": "475", "x": "46%", "y": "81%", "number": "2484"},
        {"ip": "45.158.39.98", "port": "475", "x": "47%", "y": "82%", "number": "6564"},
        {"ip": "45.158.39.114", "port": "443", "x": "48%", "y": "83%", "number": "2819"},
    ],
}

# Store user's last selected country to handle server selection
user_selection = {}

# Global variable to store the latest bot.html content
latest_html_content = None

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global latest_html_content
    if message.author.bot:
        return

    # Command: #server list
    if message.content.lower() == "#server list":
        try:
            logger.info("Received command: #server list")
            countries = [key for key in country_to_ip.keys() if not isinstance(country_to_ip[key], str)]  # Exclude aliases
            if not countries:
                await message.channel.send("No servers available.")
                return

            msg = "**Available Server Countries**\n"
            msg += "```\n"
            for idx, country in enumerate(countries, 1):
                msg += f"{idx}. {country.capitalize()}\n"
            msg += "```\n"
            msg += "Use `#server <country>` to see servers in a specific country (e.g., `#server mumbai`)."
            await message.channel.send(msg)
            return
        except Exception as e:
            logger.error(f"Unexpected error in #server list: {str(e)}")
            await message.channel.send(f"Error: {str(e)}")
            return

    if message.content.startswith("#server "):
        try:
            content = message.content.split("#server ")[1].strip().lower()
            logger.info(f"Received command: #server {content}")

            # Handle country aliases (e.g., "ind" -> "mumbai")
            country_key = country_to_ip.get(content)
            if isinstance(country_key, str):
                content = country_key
                country_key = country_to_ip[content]

            if content not in country_to_ip or not isinstance(country_key, list):
                await message.channel.send("Country not found. Use format `#server country` (e.g., `#server mumbai` or `#server ind`). Use `#server list` to see all countries.")
                return

            # Show list of servers for the country
            servers = country_to_ip[content]
            msg = f"**Available Servers in {content.capitalize()}**\n"
            msg += "```\n"
            for idx, server in enumerate(servers, 1):
                msg += f"{idx}. {server['ip']}:{server['port']} ({server['number']})\n"
            msg += "```\n"
            msg += "Type `#select <number>` to choose a server by index (e.g., `#select 1`) or by server number (e.g., `#select 8828`)."
            await message.channel.send(msg)

            # Store the user's selected country for the next command
            user_selection[message.author.id] = {"country": content, "servers": servers}
            return

        except Exception as e:
            logger.error(f"Unexpected error in #server: {str(e)}")
            await message.channel.send(f"Error: {str(e)}")
            return

    if message.content.startswith("#select "):
        try:
            user_id = message.author.id
            if user_id not in user_selection:
                await message.channel.send("Please run `#server <country>` first to select a country.")
                return

            selection = message.content.split("#select ")[1].strip()
            selected_data = user_selection[user_id]
            country = selected_data["country"]
            servers = selected_data["servers"]

            # Check if selection is a server number or an index
            selected_server = None
            if selection.isdigit():
                selection_num = selection
                # Try to match by server number
                for server in servers:
                    if server["number"] == selection_num:
                        selected_server = server
                        break

                # If no match by server number, try by index
                if not selected_server:
                    selection_idx = int(selection) - 1
                    if selection_idx < 0 or selection_idx >= len(servers):
                        await message.channel.send(f"Please select a number between 1 and {len(servers)} or a valid server number.")
                        return
                    selected_server = servers[selection_idx]
            else:
                await message.channel.send("Please enter a valid number (e.g., `#select 1` or `#select 8828`).")
                return

            ip = selected_server["ip"]
            port = selected_server["port"]
            server_number = selected_server["number"]
            logger.info(f"User selected server: {ip}:{port} (Number: {server_number}) in {country}")

            # Fetch leaderboard data
            try:
                url = "https://slither-realtime-leaderboard.pages.dev/api/leaderboard"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch leaderboard data: {str(e)}")
                await message.channel.send("Failed to fetch leaderboard data. API might be down.")
                return

            if "dataList" not in data:
                logger.error("dataList not found in API response")
                await message.channel.send("Failed to fetch leaderboard data. Unexpected API response.")
                return

            server_found = False
            leaderboard_html = ""
            for server in data["dataList"]:
                if not (server.get("ipv4") == ip and str(server.get("po", "")) == port):
                    continue

                server_found = True
                leaderboard = server.get("leaderboard", [])
                # Show top 10 players
                msg = f"**Top 10 Players - Server: {ip}:{port} (Number: {server_number}) ({country.capitalize()})**\n"
                msg += "```\n"
                msg += "🏆 Leaderboard 🏆\n"
                msg += "------------------\n"
                for p in leaderboard[:10]:  # Limit to top 10
                    name = p.get("nk", "Unknown")
                    score = p.get("len", 0)
                    place = p.get("place", "?")
                    msg += f"{place}. {name} - Score: {score}\n"
                msg += "------------------\n"
                msg += "```\n"
                msg += "_Powered by Slither.io Bot_\n"

                # Add map link
                msg += "\n**View Server Map**: [Click Here](https://discord-bot-7ucy.onrender.com/)\n"
                await asyncio.sleep(1)  # Avoid rate limiting
                await message.channel.send(msg)

                # Format for HTML (Leaderboard)
                leaderboard_html = f"<h2>Server: {ip}:{port} (Number: {server_number}) ({country.capitalize()})</h2><ul>"
                for p in leaderboard[:10]:  # Limit to top 10
                    name = p.get("nk", "Unknown")
                    score = p.get("len", 0)
                    place = p.get("place", "?")
                    leaderboard_html += f"<li>{place}. {name} - Score: {score}</li>"
                leaderboard_html += "</ul>"

                # Generate map for HTML
                map_html = "<h2>Slither.io Server Map</h2><div class='map'>"
                added_countries = set()
                for country_name, servers in country_to_ip.items():
                    if isinstance(servers, str):  # Skip aliases
                        continue
                    for server in servers:
                        country_label = country_name.capitalize()
                        if country_label in added_countries:
                            continue
                        added_countries.add(country_label)
                        map_html += f"<div class='server-dot' style='left: {server['x']}; top: {server['y']};' title='{country_label} ({server['ip']}:{server['port']})'>{country_label}</div>"
                map_html += "</div>"

                html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Slither.io Leaderboard Bot</title>
                    <link rel="stylesheet" href="/static/style.css">
                </head>
                <body>
                    <div class="container">
                        <h1>Slither.io Leaderboard Bot</h1>
                        {map_html}
                        <div id="leaderboard">
                            {leaderboard_html if leaderboard_html else "<p>No leaderboard data available.</p>"}
                        </div>
                    </div>
                    <script src="/static/script.js"></script>
                </body>
                </html>
                """
                # Save the latest HTML content to a global variable for Flask to serve
                latest_html_content = html_content

                # Save to /tmp for Render compatibility
                try:
                    with open("/tmp/bot.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    logger.info("Successfully generated bot.html in /tmp")
                except Exception as e:
                    logger.error(f"Failed to write bot.html: {str(e)}")
                    await message.channel.send("Failed to generate `bot.html`. Check bot logs for details.")
                break

            if not server_found:
                logger.warning(f"Server {ip}:{port} not found in API response")
                await message.channel.send(f"Server `{ip}:{port}` not found.")

        except Exception as e:
            logger.error(f"Unexpected error in #select: {str(e)}")
            await message.channel.send(f"Error: {str(e)}")
            return

    await bot.process_commands(message)

# Flask routes
@app.route('/')
def serve_map():
    global latest_html_content
    if latest_html_content:
        return latest_html_content
    return "<h1>No map data available</h1><p>Please use the bot to generate a map first.</p>"

# Function to run Flask app in a separate thread
def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Start Flask in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Start Discord bot
try:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not set. Please set it in environment variables on Render.")
    bot.run(token)
except Exception as e:
    logger.error(f"Failed to start bot: {str(e)}")