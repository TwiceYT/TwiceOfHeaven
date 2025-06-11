import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

def get_msglogs(guild_id: int):
    cursor.execute('SELECT serverlogs FROM guildinfo WHERE guild_id = ?', (guild_id,))
    MsgLogs = cursor.fetchone()
    if MsgLogs:
        return MsgLogs[0]
    else:
        return None


class delmsg(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    async def log_delete(self, message: nextcord.Message):
        try:
            cursor.execute("""
                INSERT INTO delmsglog (guild_id, user_id, user, content, message_id) 
                VALUES (?, ?, ?, ?, ?)
            """, (message.guild.id, message.author.id, str(message.author), message.content, message.id))
            database.commit()
            print(f"Delete log for message with ID {message.id} inserted successfully.")
        except Exception as e:
            print(f"Failed to insert delete log for message with ID {message.id}: {e}")

        delmsglogID = get_msglogs(message.guild.id)
        if delmsglogID is None:
            print("Channel log ID is none")
            return

        log_channel = message.guild.get_channel(delmsglogID)
        if log_channel is None:
            print("Log channel not found")
            return
        
        embed = nextcord.Embed(
                title="Message Deleted",
                description=f"{message.author.mention} has deleted a message",
                color=nextcord.Color.dark_magenta()
            )
        embed.add_field(name="Deleted Content:", value=f"{message.content}", inline=False)
        embed.timestamp = nextcord.utils.utcnow()
        await log_channel.send(embed=embed)  



    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        """Listen for message deletions"""
        await self.log_delete(message)



def setup(bot: commands.Bot):
    print("DelMSG Cog Registered")
    bot.add_cog(delmsg(bot))