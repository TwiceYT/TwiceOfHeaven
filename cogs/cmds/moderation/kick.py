import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


intents = nextcord.Intents.all()


def get_kicklog_channel(i: nextcord.Interaction):
    cursor.execute('SELECT modlogs FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
    kicklog = cursor.fetchone()
    if kicklog:
        return kicklog[0]
    else:
        i.response.send_message("You will have setup your own  modlogs by using /setup", ephemeral=True)
        return None
    

class kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_guild_permissions(kick_members=True)    
    @nextcord.slash_command(
            name="kick",
            description="Kick a user from the server.",
            guild_ids=[api.GuildID]
    )
    async def kick(self, i: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason specified."):
        print(f"{member.name} got kicked by {i.user.name}")
        await member.kick(reason=reason)
        await i.response.send_message(f"User {member.mention} got kicked successfully!", ephemeral=True)

        kicklog = get_kicklog_channel(i)
        if kicklog is None:
            return  
        print(kicklog)

        channel = i.guild.get_channel(kicklog)
        if channel:
            embed = nextcord.Embed(
                title="User Kicked",
                description=f"User {member} has been kicked!",
                color=nextcord.Color.red() 
            )
            embed.add_field(name="Reason", value=reason, inline=True)
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"Kicked by {i.user.name}", icon_url=i.user.avatar.url)
            await channel.send(embed=embed)

def setup(bot: commands.Bot):
    print("Kick Cog Registered")
    bot.add_cog(kick(bot))