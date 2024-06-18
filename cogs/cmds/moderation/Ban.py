import nextcord
from nextcord.ext import commands, application_checks
import api as api
import sqlite3
from datetime import datetime

intents = nextcord.Intents.all()

database = sqlite3.connect('toh.db')
cursor = database.cursor()


class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_guild_permissions(ban_members=True)    
    @nextcord.slash_command(
        name="ban",
        description="Bans a user from the server.",
        guild_ids=[api.GuildID]
    )
    async def ban(self, i: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason specified."):
        try:
            await member.ban(reason=reason)

            cursor.execute("""
                INSERT INTO bans (serverid, banned_user, ban_reason, banned_by, ban_timestamp, user_id, bannedby_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (i.guild_id, member.name, reason, i.user.name, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), member.id, i.user.id))
            database.commit()

            await i.response.send_message(f"{member.mention} has been banned successfully!", ephemeral=True)
        except nextcord.Forbidden:
            await i.response.send_message("You don't have the necessary permissions to ban that user.")

        channel = i.guild.get_channel(api.BanLog)
        if channel:
            print(f"User {member.name} was banned by {i.user.name}")
            embed = nextcord.Embed(
                title="Ban has been issued",
                description=f"{member.mention} has been banned from the server",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Banned issued by {i.user.name}", icon_url=i.user.avatar.url)
            await channel.send(embed=embed)
            

def setup(bot: commands.Bot):
    print("Ban Cog Registered")
    bot.add_cog(Ban(bot))
