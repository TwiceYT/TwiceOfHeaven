import nextcord
from nextcord.ext import commands, tasks
import sqlite3
import asyncio
from dotenv import load_dotenv
import os

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

update_lock = asyncio.Lock()  # Global lock


def get_membercount_channel(guild_id):
    cursor.execute('SELECT membercount_channel FROM guildinfo WHERE guild_id = ?', (guild_id,))
    memchannel = cursor.fetchone()
    if memchannel:
        return memchannel[0]
    else:
        return None


class Membercount(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_counts_task.start()

    async def update_member_count_channel(self, guild):
        try:
            await self.bot.wait_until_ready()  # Wait until the bot is fully connected
            channel_id = get_membercount_channel(guild.id)
            if channel_id is not None:
                channel = guild.get_channel(channel_id)
                if channel and isinstance(channel, nextcord.VoiceChannel):
                    await asyncio.sleep(2)  # Introduce a delay before updating the channel
                    await channel.edit(name=f"Members: {guild.member_count}")
        except nextcord.errors.Forbidden:
            print(f"Bot does not have permission to edit the channel in {guild.name}")
        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Failed processing {guild.name}")

    @tasks.loop(minutes=1)
    async def update_counts_task(self):
        print("Executing update_counts_task")
        try:
            for guild in self.bot.guilds:
                try:
                    async with update_lock:
                        await self.update_member_count_channel(guild)
                except Exception as e:
                    print(f"Error processing {guild.name}: {e}")
        except Exception as loop_exception:
            print(f"Error in update_counts_task loop: {loop_exception}")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            async with update_lock:
                await self.update_member_count_channel(guild)


def setup(bot: commands.Bot):
    print("Membercount Cog Registered")
    bot.add_cog(Membercount(bot))
