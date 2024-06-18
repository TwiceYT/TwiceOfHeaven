import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3

intents = nextcord.Intents.all()

database = sqlite3.connect('toh.db')
cursor = database.cursor()



class Example(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot: commands.Bot):
    print("Example Cog Registered")
    bot.add_cog(Example(bot))