import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
Invite = os.getenv("SupportServerInvite")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()

class supportserver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="bot_supportserver",
        description="Get the support server invite link."
    )
    async def supportserver(self, i: nextcord.Interaction):
        embed = nextcord.Embed(
            title="Support Server",
            description="Join our support server for help and updates!",
            color=nextcord.Color.blue()
        )
        embed.add_field(name="Invite Link", value=f"[Click here to join]({Invite})", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await i.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    print("supservdddddddddddddddddddddddd Cog Registered")
    bot.add_cog(supportserver(bot))