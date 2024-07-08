import nextcord
from nextcord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


def get_vlogs(guild_id: int):
    cursor.execute('SELECT serverlogs FROM guildinfo WHERE guild_id = ?', (guild_id,))
    VcLogs = cursor.fetchone()
    if VcLogs:
        return VcLogs[0]
    else:
        return None



class VoiceChannelLogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def log_voice_change(self, member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
        if before.channel != after.channel:
            if before.channel:
                action = "left"
                channel = before.channel.name
            else:
                action = "joined"
                channel = after.channel.name


        vclogID = get_vlogs(member.guild.id)
        if vclogID is None:
            print("Channel log ID is none")
            return

        VcLog_channel = member.guild.get_channel(vclogID)
        if VcLog_channel is None:
            print("Log channel not found")
            return
        embed = nextcord.Embed(
            title=f"{action.capitalize()} Voice",
            description=f"{member.mention} {action} the voice channel {channel}",
            color=nextcord.Color.dark_orange()
        )
        embed.timestamp = nextcord.utils.utcnow()
        await VcLog_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
        """Listen for voice state updates (e.g., join/leave voice channels)"""
        await self.log_voice_change(member, before, after)

def setup(bot: commands.Bot):
    print("VoiceChannelLogs Cog Registered")
    bot.add_cog(VoiceChannelLogs(bot))
