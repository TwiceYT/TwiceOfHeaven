import nextcord
from nextcord.ext import commands
import os
import traceback
import sqlite3

# Setup bot with intents and prefix
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

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


#
#
#
#
# Function to set up the database connection
def setup_database():
    try:
        # Connect to the database
        db_connection = sqlite3.connect('toh.db')
        db_cursor = db_connection.cursor()
        return db_connection, db_cursor
    except Exception as e:
        print("Failed to set up the database:")
        traceback.print_exc()
        return None, None

# Set up database connection
db_connection, db_cursor = setup_database()
if db_connection is not None and db_cursor is not None:
    bot.db_connection = db_connection  # Store the connection in the bot instance
    bot.db_cursor = db_cursor          # Store the cursor in the bot instance
else:
    print("Database connection failed. Cannot start the bot.")
    exit(1)  # Exit the script if database connection failed




#
#
#
# Function to get the bot token from the database
def get_bot_token():
    if not hasattr(bot, 'db_cursor') or bot.db_cursor is None:
        raise Exception("Database cursor is None")
    
    bot.db_cursor.execute('SELECT token FROM config')
    result = bot.db_cursor.fetchone()
    if result:
        return result[0]
    else:
        raise Exception("Bot token not found in the database")

# Get the bot token from the database
try:
    token = get_bot_token()
except Exception as e:
    print("Failed to get the bot token:")
    traceback.print_exc()
    token = None

if token:
    # Run the bot
    bot.run(token)
else:
    print("Bot token is missing. Cannot start the bot.")
