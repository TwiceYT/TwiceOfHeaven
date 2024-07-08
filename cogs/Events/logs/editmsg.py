import nextcord
from nextcord.ext import commands
import sqlite3
from datetime import datetime
import api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()


def get_editlogs(guild_id: int):
    cursor.execute('SELECT serverlogs FROM guildinfo WHERE guild_id = ?', (guild_id,))
    EditLogs = cursor.fetchone()
    if EditLogs:
        return EditLogs[0]
    else:
        return None

class EditMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def log_edit(self, before: nextcord.Message, after: nextcord.Message):
        # Check if the message author is not the bot
        if before.author != self.bot.user:
            try:
                old_content = before.content or "Bot message"
                new_content = after.content or "Bot message"

                # Insert edit log into editlog table
                cursor.execute("""
                    INSERT INTO editlog (user_id, user, old_content, new_content, message_id, edit_date) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (after.author.id, str(after.author), old_content, new_content, after.id, datetime.now()))
                database.commit()
                print(f"Edit log for message with ID {after.id} inserted successfully.")
            except Exception as e:
                print(f"Failed to insert edit log for message with ID {after.id}: {e}")



            EditLogID = get_editlogs(before.guild.id)
            if EditLogID is None:
                print("Channel log ID is none")
                return

            log_channel = before.guild.get_channel(EditLogID)
            if log_channel is None:
                print("Log channel not found")
                return
            
            embed = nextcord.Embed(
                title="Message Edited",
                description=f"{after.author.mention} has edited a message",
                color=nextcord.Color.dark_magenta()
            )
            embed.add_field(name="Old Content", value=f"```\n{old_content}\n```", inline=False)
            embed.add_field(name="New Content", value=f"```\n{new_content}\n```", inline=False)
            embed.timestamp = nextcord.utils.utcnow()
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        """Listen for message edits"""
        await self.log_edit(before, after)

def setup(bot: commands.Bot):
    print("EditMessage Cog Registered")
    bot.add_cog(EditMessage(bot))