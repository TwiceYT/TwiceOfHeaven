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

#Load env file
load_dotenv(dotenv_path='config\config.env')
#Load custom Prefix
BotID = os.getenv("BotID")


class MessageLed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
    name="msg-led",
    description="Check the message leaderboard"  
    )
    async def leaderboard(self, i: nextcord.Interaction):
        cursor.execute("""
        SELECT user, msg FROM msgstats WHERE user_id!=? AND guild_id = ?
        """, (BotID, i.guild.id,))
        result = cursor.fetchall()

        # Sort the result list based on the bank amount
        result.sort(key=lambda x: x[1], reverse=True)

        # Slice the result list to show only the top 10 users
        result = result[:10]

        if result:
            embed = nextcord.Embed(title="Message Leaderboard", color=nextcord.Color.red())
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/859111111111111111/859111111111111111/economy.png")
            embed.add_field(name="Nr", value="\n".join([f"{index+1}" for index, user in enumerate(result)]), inline=True)
            embed.add_field(name="User", value="\n".join([f"{user[0]}" for index, user in enumerate(result)]), inline=True)
            embed.add_field(name="Msgs", value="\n".join([f"{user[1]}" for index, user in enumerate(result)]), inline=True)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(content="There are no users in the economy leaderboard")
            

def setup(bot: commands.Bot):
    print("MessageLed Cog Registered")
    bot.add_cog(MessageLed(bot))