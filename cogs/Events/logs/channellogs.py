import nextcord
from nextcord.ext import commands
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

def get_channelogs(guild_id: int):
    cursor.execute('SELECT serverlogs FROM guildinfo WHERE guild_id = ?', (guild_id,))
    ChannelLogs = cursor.fetchone()
    if ChannelLogs:
        return ChannelLogs[0]
    else:
        return None

class ChannelLogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: nextcord.abc.GuildChannel):
        action = "Created"
        await self.log_channel_change(action, channel)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: nextcord.abc.GuildChannel):
        action = "Deleted"
        await self.log_channel_change(action, channel)

    async def log_channel_change(self, action: str, channel: nextcord.abc.GuildChannel):
        user_id = channel.guild.owner_id if channel.guild else None
        user = channel.guild.owner.name if channel.guild else None
        channel_name = channel.name
        channel_id = channel.id

        cursor.execute("""
            INSERT INTO Channellog (guild_id, user_id, user, action, channel_name, channel_id) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (channel.guild.id, user_id, user, action, channel_name, channel_id))
        database.commit()
        print(f"Channel {action} log inserted successfully.")

        clogID = get_channelogs(channel.guild.id)
        if clogID is None:
            print("Channel log ID is none")
            return

        log_channel = channel.guild.get_channel(clogID)
        if log_channel is None:
            print("Log channel not found")
            return

        embed = nextcord.Embed(
            title=f"A Channel has been {action}",
            description="",
            color=nextcord.Color.dark_magenta()
        )
        embed.add_field(name=f"{action} Channel:", value=f"```\n{channel_name}\n```", inline=False)
        embed.add_field(name=f"{action} by", value=f"```\n{user}\n```", inline=False)
        embed.timestamp = nextcord.utils.utcnow()
        await log_channel.send(embed=embed)

def setup(bot: commands.Bot):
    print("ChannelLogs Cog Registered")
    bot.add_cog(ChannelLogs(bot))