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


def get_welcome_channel(guild_id):
    cursor.execute('SELECT welcome_channel_id FROM guildinfo WHERE guild_id = ?', (guild_id,))
    welcome = cursor.fetchone()
    if welcome:
        return welcome[0]
    else:
        return None

def get_welcome_color(guild_id):
    cursor.execute('SELECT welcome_color FROM guildinfo WHERE guild_id = ?', (guild_id,))
    color = cursor.fetchone()
    if color and color[0]:
        return int(color[0], 16)  # Convert from hex string to integer
    else:
        return 0x00ff00  # Default color (green)

class MemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel_id = get_welcome_channel(member.guild.id)
        if welcome_channel_id is None:
            return
        
        channel = member.guild.get_channel(welcome_channel_id)
        if channel:
            # Get the stored color or use the default
            color = get_welcome_color(member.guild.id)
            
            embed = nextcord.Embed(
                title="Welcome!",
                description=f"We're glad to have you here, {member.mention}!",
                color=color
            )
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"Joined at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", icon_url=member.avatar.url)
            
            await channel.send(f"Welcome to the server, {member.mention}!")
            await channel.send(embed=embed)

class SetupWelcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="setup_welcome_channel", description="Set up a welcome channel")
    async def setup_welcome_channel(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        cursor.execute('UPDATE guildinfo SET welcome_channel_id = ? WHERE guild_id = ?', (channel.id, interaction.guild.id))
        database.commit()

        await interaction.response.send_message(f"Welcome channel has been set to {channel.mention}", ephemeral=True)

    @nextcord.slash_command(name="welcome_color", description="Set the color for the welcome message")
    async def welcome_color(self, interaction: nextcord.Interaction, color: str):
        # Validate and convert the color input (expecting a hex string)
        if not color.startswith('#') or len(color) != 7:
            await interaction.response.send_message("Please provide a valid hex color code in the format #RRGGBB.", ephemeral=True)
            return

        try:
            int(color[1:], 16)  # This checks if the color is a valid hex
        except ValueError:
            await interaction.response.send_message("Invalid hex color code. Please try again.", ephemeral=True)
            return

        # Store the color in the database
        cursor.execute('UPDATE guildinfo SET welcome_color = ? WHERE guild_id = ?', (color[1:], interaction.guild.id))
        database.commit()

        await interaction.response.send_message(f"Welcome message color has been set to {color}.", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(MemberJoin(bot))
