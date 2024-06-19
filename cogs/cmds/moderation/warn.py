import nextcord
from nextcord.ext import commands
from datetime import datetime
import api as api
import sqlite3

database = sqlite3.connect('toh.db')
cursor = database.cursor()

def get_warnlog_channel(guild_id: int):
    cursor.execute('SELECT modlogs FROM guildinfo WHERE guild_id = ?', (guild_id,))
    warnlog = cursor.fetchone()
    if warnlog:
        return warnlog[0]
    else:
        return None

def get_warn_role(guild_id: int):
    cursor.execute('SELECT staffrole_id FROM guildinfo WHERE guild_id = ?', (guild_id,))
    warnrole = cursor.fetchone()
    if warnrole:
        return nextcord.Object(id=warnrole[0])
    return None

class Warn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.warnings = {}

        self.load_warnings()

    def load_warnings(self):
        self.warnings.clear()  # Clear any existing warnings
        for guild in self.bot.guilds:
            guild_id = guild.id
            self.warnings[guild_id] = self.load_warnings_from_db(guild_id)

    def load_warnings_from_db(self, guild_id: int):
        warnings = {}
        cursor.execute("SELECT user_id, warnings FROM warns WHERE guild_id = ?", (guild_id,))
        rows = cursor.fetchall()
        for user_id, warnings_count in rows:
            warnings[user_id] = warnings_count
        return warnings

    @commands.Cog.listener()
    async def on_ready(self):
        # Ensure warnings are loaded when the bot connects to Discord
        self.load_warnings()


#
##
###
#### WARN COMMAND
###
##
#


    @nextcord.slash_command(
        name="warn",
        description="Warn a user",
        guild_ids=[api.GuildID]
    )
    async def warn(self, i: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason specified."):
        guild_id = i.guild.id

        # Check if the user already has warnings in the database
        cursor.execute("SELECT * FROM warns WHERE guild_id = ? AND user_id = ?", (guild_id, member.id))
        result = cursor.fetchone()

        if result:
            # User already exists in the database, update the existing record
            current_warnings = result[7]  # Assuming the seventh column is warnings, adjust accordingly
            num_warnings = current_warnings + 1
            cursor.execute("UPDATE warns SET warnings = ?, warned_user = ?, warn_reason = ?, warned_by = ?, warnedby_id = ?, warn_timestamp = ? WHERE guild_id = ? AND user_id = ?", (num_warnings, member.name, reason, i.user.name, i.user.id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), guild_id, member.id))
        else:
            # User does not exist in the database, insert a new record
            num_warnings = 1
            cursor.execute("INSERT INTO warns (guild_id, warned_user, warn_reason, warned_by, user_id, warnedby_id, warn_timestamp, warnings) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (guild_id, member.name, reason, i.user.name, member.id, i.user.id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), num_warnings))

        database.commit()

        # Update self.warnings dictionary
        self.load_warnings()

        # Send embed response
        embed = nextcord.Embed(
            title="User Warned",
            description=f"{member.mention} has been warned.",
            color=nextcord.Color.dark_red()
        )
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.add_field(name="Total Warnings:", value=num_warnings, inline=False)
        embed.set_footer(text=f"Warned by {i.user.name}", icon_url=i.user.avatar.url)
        await i.response.send_message(embed=embed, ephemeral=True)

        # Send warn log message
        warnlog = get_warnlog_channel(guild_id)
        if warnlog is not None:
            channel = i.guild.get_channel(warnlog)
            if channel:
                warn_log_embed = nextcord.Embed(
                    title="User Warned",
                    description=f"{member.mention} has been warned.",
                    color=nextcord.Color.red()
                )
                warn_log_embed.add_field(name="Total Warnings:", value=num_warnings, inline=False)
                warn_log_embed.set_thumbnail(url=member.avatar.url)
                warn_log_embed.set_footer(text=f"Warned by {i.user.name}", icon_url=i.user.avatar.url)
                await channel.send(embed=warn_log_embed)

#
##
###
#### UNWARN COMMAND
###
##
#

    @nextcord.slash_command(
        name="delwarn",
        description="Remove warnings from a user",
        guild_ids=[api.GuildID]
    )
    async def unwarn(self, i: nextcord.Interaction, member: nextcord.Member, num_warnings: int = 1):
        guild_id = i.guild.id

        user_id = member.id

        # Retrieve current warnings from the database, ordered by the correct timestamp column in descending order
        cursor.execute("SELECT * FROM warns WHERE user_id = ? AND guild_id = ? ORDER BY warn_timestamp DESC", (user_id, guild_id,))
        result = cursor.fetchone()

        print("Before update - Result:", result)

        if result:
            current_warnings = int(result[7])  # Assuming that the seventh column represents warnings, adjust accordingly

            # Ensure we don't go below 0 warnings
            new_warnings = max(current_warnings - num_warnings, 0)

            try:
                # Update the warn data in the database
                cursor.execute("UPDATE warns SET warnings = ? WHERE user_id = ? AND guild_id = ?", (new_warnings, member.id, i.guild.id))
                database.commit()

                # Reload warnings from the database after performing an unwarn
                self.load_warnings()

                # Send out an embed if remove warning was successful
                embed = nextcord.Embed(
                    title="Removed warnings from a user",
                    description=f"{num_warnings} warning(s) have been removed from {member.mention}!",
                    color=nextcord.Color.green()
                )
                embed.set_footer(text=f"Removed by {i.user.name}", icon_url=i.user.avatar.url)
                await i.response.send_message(embed=embed, ephemeral=True)

                # Send warn log message
                warnlog = get_warnlog_channel(guild_id)
                if warnlog is not None:
                    channel = i.guild.get_channel(warnlog)
                    if channel:
                        print(f"User {member.name} was unwarned by {i.user.name}")
                        warn_log_embed = nextcord.Embed(
                            title="User Unwarned",
                            description=f"{member.mention} has been unwarned.",
                            color=nextcord.Color.green()
                        )
                        warn_log_embed.add_field(name="Removed Warnings:", value=num_warnings, inline=False)
                        warn_log_embed.add_field(name="Current Warnings:", value=new_warnings, inline=False)
                        warn_log_embed.set_footer(text=f"Unwarned by {i.user.name}", icon_url=i.user.avatar.url)
                        await channel.send(embed=warn_log_embed)
            
            except Exception as e:
                print(f"Error during update: {e}")
                await i.response.send_message("Error during update. Please check logs.", ephemeral=True)
                return

        else:
            # If the user is not found in the database, print an error message
            print(f"Error: User {user_id} not found in the database.")
            await i.response.send_message("User not found in the database.", ephemeral=True)
            return


#
##
###
#### WARNINGS COMMAND
###
##
#


    

    @nextcord.slash_command(
        name="warnings",
        description="See the amount of warnings the user has",
        guild_ids=[api.GuildID]
    )
    async def warnings(self, i: nextcord.Interaction, member: nextcord.Member):
        guild_id = i.guild.id
        user_id = member.id

        cursor.execute("SELECT warnings FROM warns WHERE guild_id = ? AND user_id = ?", (guild_id, user_id,))
        result = cursor.fetchone()

        if result:
            current_warnings = result[0]
        else:
            current_warnings = 0  

        embed = nextcord.Embed(
            title="User Warnings",
            description=f"{member.mention} currently has {current_warnings} warnings.",
            color=nextcord.Color.red()
        )
        await i.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    print("Warn Cog Registered")
    bot.add_cog(Warn(bot))
