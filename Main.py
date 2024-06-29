import nextcord
from nextcord.ext import commands
import os
import traceback
from database.db import setup
from dotenv import load_dotenv, dotenv_values

# Initialize bot with intents and prefix
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Set up database connection
db_connection, db_cursor = setup()

if db_connection is not None and db_cursor is not None:
    bot.db_connection = db_connection  # Store the connection in the bot instance
    bot.db_cursor = db_cursor          # Store the cursor in the bot instance
else:
    print("Database connection failed. Cannot start the bot.")
    exit(1)  # Exit the script if database connection failed

# Test command
@bot.command()
async def test(ctx):
    await ctx.send("test")

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print("------------")
    print(f"Logged in as {bot.user.name}")
    print("------------")

# Load extensions (cogs) from directories
for folder in os.listdir("cogs"):
    folder_path = os.path.join("cogs", folder)
    if os.path.isdir(folder_path):
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)
            if os.path.isdir(subfolder_path):
                for file in os.listdir(subfolder_path):
                    if file.endswith(".py"):
                        extension_name = f"cogs.{folder}.{subfolder}.{file[:-3]}"
                        try:
                            bot.load_extension(extension_name)
                        except Exception as e:
                            print(f"Failed to load extension {extension_name}:")
                            traceback.print_exc()

load_dotenv(dotenv_path='config.env')
Token = os.getenv("BOTTOKEN")
if Token:
    bot.run(Token)

