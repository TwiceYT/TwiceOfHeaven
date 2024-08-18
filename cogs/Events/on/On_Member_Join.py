import nextcord
from nextcord.ext import commands
import api as api
from datetime import datetime
import random
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


def get_welcome_channel(i: nextcord.Interaction):
    cursor.execute('SELECT welcome_channel_id FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
    welcome = cursor.fetchone()
    if welcome:
        return welcome[0]
    else:
        i.response.send_message("You will have setup your own welcome channel by using /setup", ephemeral=True)
        return None


class MemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member, i: nextcord.Interaction):
        # Perform actions when a member joins
        # For example, send a welcome message as an embed to a specific channel
        welcome = get_welcome_channel(i)
        if welcome is None:
            return  
        print(welcome)

        channel = i.guild.get_channel(welcome)
        if channel:
            # Create an embed for the welcome message
            embed = nextcord.Embed(
                title=f"Welcome to the server, {member.name}!",
                description=f"We're glad to have you here. Enjoy your stay!",
                color=0x00ff00
            )
            embed.set_thumbnail(url=member.avatar.url)  # Display member's avatar
            embed.set_footer(icon_url=i.user.avatar, text=f"{datetime.now}")

            await channel.send(embed=embed)

def setup(bot: commands.Bot):
    print("MemberJoin Cog Registered")
    bot.add_cog(MemberJoin(bot))