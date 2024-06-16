import nextcord
from nextcord.ext import commands
import api
import os
import database.db
import traceback

# Setup bot with intents and prefix
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or(api.Prefix), intents=intents)

# Test command
@bot.command()
async def test(ctx):
    await ctx.send("test")

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print("------------")
    print("Logged in as " + bot.user.name)
    print("------------")

# Initialize counters
cmds = 0
events = 0
buttons = 0
imgs = 0
os.system(f"title TwiceOfHeaven - Commands [{cmds}] - Events [{events}]")

# Set up database connection
try:
    db, cursor = database.db.setup()
    if db is None or cursor is None:
        raise Exception("Database setup failed, returned None")
except Exception as e:
    print("Failed to set up the database:")
    traceback.print_exc()
    db, cursor = None, None

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
                            if folder == "cmds":
                                cmds += 1
                            elif folder == "Events":
                                events += 1
                            elif folder == "imgs":
                                imgs += 1
                            os.system(f"title TwiceOfGods - Commands [{cmds}] - Events [{events}]")
                        except Exception as e:
                            print(f"Failed to load extension {extension_name}:")
                            traceback.print_exc()

    if database is not None and cursor is not None:
        bot.database = database
        bot.cursor = cursor

# Run the bot
bot.run(api.Token)
