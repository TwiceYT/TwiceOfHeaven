import nextcord
from nextcord.ext import commands, tasks
import sqlite3
import api
from dotenv import load_dotenv
import os

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


intents = nextcord.Intents.all()


def get_rolecount_channel(guild_id):
    cursor.execute('SELECT rolecount_channel FROM guildinfo WHERE guild_id = ?', (guild_id,))
    rolechannel = cursor.fetchone()
    if rolechannel:
        return rolechannel[0]
    else:
        return None


class rolecount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_counts_task.start()  # Start the background task when the cog is loaded

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_role_count()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.update_role_count()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.update_role_count()

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if len(before.roles) != len(after.roles):
            await self.update_role_count(after)

    @tasks.loop(minutes=10)  # Set the interval for the background task
    async def update_counts_task(self):
        print("Executing update_counts_task")
        await self.update_role_count()
        print("Updated role count")

    async def update_role_count(self, guild=None):
        if guild is None:
            for guild in self.bot.guilds:
                await self.update_role_count(guild)
            return

        total_roles = len(guild.roles)



        channel_id = get_rolecount_channel(guild.id)
        if channel_id is not None:
            channel = guild.get_channel(channel_id)
            if channel and isinstance(channel, nextcord.VoiceChannel):
                await channel.edit(name=f'Total Roles: {total_roles-1}')

def setup(bot: commands.Bot):
    bot.add_cog(rolecount(bot))
    print("Rolescount Cog Registered")
