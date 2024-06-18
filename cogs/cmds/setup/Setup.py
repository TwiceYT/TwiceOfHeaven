import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3

intents = nextcord.Intents.all()

database = sqlite3.connect('toh.db')
cursor = database.cursor()


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup",
        description="Setup the bot",
        guild_ids=[api.GuildID]
    )
    async def setup(self, i: nextcord.Interaction):
        print("Setting up")
        
def setup(bot: commands.Bot):
    print("Setup Cog Registered")
    bot.add_cog(Setup(bot))