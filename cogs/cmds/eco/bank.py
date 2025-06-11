import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()

class bank(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #Check how much a user has in his bank
    @nextcord.slash_command(
        name="bank",
        description="Check how much a user has in his bank account"
    )
    async def bank(self, i: nextcord.Interaction, member: nextcord.Member):

        cursor.execute(f"SELECT bank FROM economy WHERE user_id = ? AND guild_id = ?", (member.id, i.guild_id,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("""
                INSERT INTO minigames(guild_id,user_id, user, bank) VALUES (?,?, ?, ?)
                """, (i.guild_id, member.id, member.name, 0))
            database.commit()
        
        amount = result[0]


        embed = nextcord.Embed(
            title="Bank Amount",
            description=f"You are now checking {member.name}'s bank account!"
        )
        embed.add_field(name="Amount", value=f"${amount}", inline=False)
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.avatar.url)
        await i.send(embed=embed)

def setup(bot: commands.Bot):
    print("Bank Cog Registered")
    bot.add_cog(bank(bot))