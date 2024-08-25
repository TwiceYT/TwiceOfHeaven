import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()

class Example(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot: commands.Bot):
    print("Example Cog Registered")
    bot.add_cog(Example(bot))