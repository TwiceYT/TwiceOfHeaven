import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
Invite = os.getenv("SupportServerInvite")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()

class supportserver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="bot_server",
        description="Fetch an invite to the bots original support server!"
    )
    async def supserv(self, i: nextcord.Interaction):
        await i.response.send_message(Invite)

def setup(bot: commands.Bot):
    print("supserv Cog Registered")
    bot.add_cog(supportserver(bot))