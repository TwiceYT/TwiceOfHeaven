import nextcord
from nextcord.ext import commands, tasks
import sqlite3
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

def get_unverified_channel(guild_id):
    cursor.execute('SELECT unverified_channel FROM guildinfo WHERE guild_id = ?', (guild_id,))
    unverified_channel = cursor.fetchone()
    if unverified_channel:
        return unverified_channel[0]
    else:
        return None
    
def get_verified_role(guild_id):
    cursor.execute('SELECT verify_role FROM guildinfo WHERE guild_id = ?', (guild_id,))
    verify_role = cursor.fetchone()
    if verify_role:
        return verify_role[0]
    else:
        return None

class Unverified(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_counts_task.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready')
        await self.update_role_count()

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if len(before.roles) != len(after.roles):
            await self.update_role_count(after)

    @tasks.loop(minutes=1) 
    async def update_counts_task(self):
        print("Executing update_unverified")
        await self.update_role_count()

    async def update_role_count(self, guild=None):
        if guild is None:
            for guild in self.bot.guilds:
                await self.update_role_count(guild)
            return

        # Fetch the target role ID and voice channel ID from the database
        target_role_id = get_verified_role(guild.id)
        voice_channel_id = get_unverified_channel(guild.id)

        if not target_role_id:
            #print(f"Error: Target role ID not found in guild '{guild.name}'")
            return

        target_role = guild.get_role(target_role_id)

        if not target_role:
            return None

        # Count members without the target role
        members_without_role = sum(1 for member in guild.members if target_role not in member.roles)

        # Get the target voice channel
        voice_channel = guild.get_channel(voice_channel_id)

        if voice_channel and isinstance(voice_channel, nextcord.VoiceChannel):
            await voice_channel.edit(name=f'Unverified: {members_without_role}')

def setup(bot: commands.Bot):
    bot.add_cog(Unverified(bot))
    print("Unverified Cog Registered")
