import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3
from datetime import datetime

intents = nextcord.Intents.all()

database = sqlite3.connect('toh.db')
cursor = database.cursor()


def get_banlog_channel(i: nextcord.Interaction):
    cursor.execute('SELECT modlogs FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
    banlog = cursor.fetchone()
    if banlog:
        return banlog[0]
    else:
        i.response.send_message("You will have setup your own banlogs", ephemeral=True)
        return None
    

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot



#
##
###
#### BAN COMMAND
###
##
#

    @application_checks.has_guild_permissions(ban_members=True)    
    @nextcord.slash_command(
        name="ban",
        description="Bans a user from the server.",
        guild_ids=[api.GuildID]
    )
    async def ban(self, i: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason specified."):
        banlogID = get_banlog_channel(i)
        if banlogID is None:
            return  # Exit if no ban log channel is set up
        print(banlogID)

        try:
            await member.ban(reason=reason)


            cursor.execute("""
                INSERT INTO bans (guild_id, banned_user, ban_reason, banned_by, ban_timestamp, user_id, bannedby_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (i.guild_id, member.name, reason, i.user.name, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), member.id, i.user.id))
            database.commit()

            await i.response.send_message(f"{member.mention} has been banned successfully!", ephemeral=True)
        except nextcord.Forbidden:
            await i.response.send_message("You don't have the necessary permissions to ban that user.")

        # Fetch the channel object using the ID
        channel = i.guild.get_channel(banlogID)
        if channel is None:
            await i.response.send_message("Ban log channel not found.", ephemeral=True)
            print(f"Ban log channel with ID {banlogID} not found.")
            return

        print(f"Ban log channel found: {channel.name}")

        embed = nextcord.Embed(
            title="Ban Issued",
            description=f"{member.mention} has been banned from the server",
            color=nextcord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Ban issued by {i.user.name}", icon_url=i.user.avatar.url)

        try:
            await channel.send(embed=embed)
            print(f"Message sent to ban log channel: {channel.name}")
        except Exception as e:
            print(f"Failed to send message to ban log channel: {e}")
    #            



#
##
###
#### UNBAN COMMAND
###
##
#

    @application_checks.has_guild_permissions(ban_members=True)
    @nextcord.slash_command(
        name="unban",
        description="unbans a user for the guild.",
        guild_ids=[api.GuildID]
    )
    async def unban(self, i: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason specified."):
        try:
            ban_entry = await i.guild.fetch_ban(nextcord.Object(id=member.id))
            await i.guild.unban(ban_entry.user, reason=reason)

            cursor.execute("DELETE FROM bans WHERE user_id = ? AND guild_id = ?", (member.id, i.guild.id))
            database.commit()

            banlogID = get_banlog_channel(i)
            if banlogID is None:
                return  
            print(banlogID)

            channel = i.guild.get_channel(banlogID)
            if channel:
                print(f"**{member.name}** was unbanned by {i.user.name}")
                embed = nextcord.Embed(
                    title="User Unbanned",
                    description=f"Member **{member.name}** has been unbanned",
                    color=nextcord.Color.green()             
                )
                embed.add_field(name=f"Reason", value=reason, inline=False)
                embed.set_thumbnail(url=member.avatar.url)
                embed.set_footer(text=f"Unbanned by {i.user.name}", icon_url=i.user.avatar.url)
                await channel.send(embed=embed)

            await i.response.send_message(f"User with ID {member.id} has been unbanned successfully.", ephemeral=True)
        except nextcord.errors.NotFound:
            await i.response.send_message(f"User with ID {member.id} is not currently banned.", ephemeral=True)
        except nextcord.errors.Forbidden:
            await i.response.send_message("You don't have the necessary permissions to unban that user.", ephemeral=True)


#
##
###
#### BANLIST COMMAND
###
##
#

    @application_checks.has_guild_permissions(ban_members=True) 
    @nextcord.slash_command(
        name="banlist",
        description="Displays all information of every banned user",
        guild_ids=[api.GuildID]
    )
    async def banlist(self, i: nextcord.Interaction):
        cursor.execute("SELECT * FROM bans WHERE guild_id = ?", (i.guild.id,))
        banslist = cursor.fetchall()

        if banslist:  # Fix the variable name
            ban_info_embed = nextcord.Embed(
                title="Ban information",
                color=nextcord.Color.red()
            )

            for ban in banslist:
                serverid, user_name, ban_reason, banned_by, ban_timestamp, user_id, bannedby_id = ban
                ban_info_embed.add_field(
                    name=f"",
                    value=f"User Name: {user_name}\nReason: {ban_reason}\nBanned by: {banned_by}\nTimestamp: {ban_timestamp}",
                    inline=False
                )

            await i.response.send_message(embed=ban_info_embed)
        else:
            await i.response.send_message("No users have been banned.")

def setup(bot: commands.Bot):
    print("Ban Cog Registered")
    bot.add_cog(Ban(bot))
