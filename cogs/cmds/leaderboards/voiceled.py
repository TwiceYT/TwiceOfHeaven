import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
BotID = os.getenv("BotID")

database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

class VoiceLed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
    name="voice-led",
    description="Check the voice leaderboard"  
    )
    async def leaderboard(self, i: nextcord.Interaction):
        cursor.execute("""
        SELECT name, total FROM voicestat WHERE user_id!=? AND guild_id = ?
        """, (BotID, i.guild_id,))
        result = cursor.fetchall()

        result.sort(key=lambda x: x[1], reverse=True)

        # Slice the result list to show only the top 10 users
        result = result[:10]

        if result:
            embed = nextcord.Embed(title="Voice Leaderboard", color=nextcord.Color.red())
            embed.add_field(name="Nr", value="\n".join([f"{index+1}" for index, user in enumerate(result)]), inline=True)
            embed.add_field(name="User", value="\n".join([f"{user[0]}" for index, user in enumerate(result)]), inline=True)
            embed.add_field(name="Hours", value="\n".join([f"{user[1]/3600:.1f}" for index, user in enumerate(result)]), inline=True)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(content="There are no users in the level leaderboard")
            

def setup(bot: commands.Bot):
    print("VoiceLed Cog Registered")
    bot.add_cog(VoiceLed(bot))