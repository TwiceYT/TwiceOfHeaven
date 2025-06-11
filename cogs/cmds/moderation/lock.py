import nextcord
from nextcord.ext import commands, application_checks
import sqlite3

intents = nextcord.Intents.all()

#Get the lockchannel from DB to be retreived to send out a message to logchannel
def get_locklog_channel(i: nextcord.Interaction):
    with sqlite3.connect('toh.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT modlogs FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
        locklog = cursor.fetchone()
        if locklog:
            return locklog[0]
        else:
            i.response.send_message("You need to set up your banlogs using /setup", ephemeral=True)
            return None

#Get the staffrole from DB to be retreived later in the command
def get_staffrole(i: nextcord.Interaction):
    with sqlite3.connect('toh.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT staffrole_id FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
        staffrole = cursor.fetchone()
        if staffrole:
            return staffrole[0]
        else:
            i.response.send_message("You need to set up your kick logs using /setup", ephemeral=True)
            return None

#Function check if staff or admin to set the permissions
def is_staff_or_admin():
    async def predicate(i: nextcord.Interaction):
        #Checks if user has the administration perm
        if i.user.guild_permissions.administrator:
            return True
        

        #Check if user has the staffrole from DB
        staff_role_id = get_staffrole(i)
        if staff_role_id is None:
            return False
        
        staff_role = i.guild.get_role(staff_role_id)
        if staff_role in i.user.roles:
            return True
        
        await i.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return False
    
    return application_checks.check(predicate)
                                    

                            
class Lock(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

#
##
###
#### Locked COMMAND
###
##
#

    @is_staff_or_admin()
    @nextcord.slash_command(
        name="lock",
        description="Lock the channel"
    )
    async def lock(self, i: nextcord.Interaction):
        # Check if the command is used in a guild
        if i.guild is None:
            await i.response.send_message("This command can only be used in a server (guild).", ephemeral=True)
            return


        # Check if the user has the necessary permissions
        if not i.user.guild_permissions.manage_channels:
            await i.response.send_message("You don't have permission to manage channels.", ephemeral=True)
            return

        # Get the current channel
        channel = i.channel

        # Retrieve the staff role
        staffrole = get_staffrole(i)
        if staffrole is None:
            return  
        
        # Ensure staffrole is a list
        staff_role_ids = [staffrole]

        # Set permissions to deny everyone and allow the owner and staff roles
        await channel.set_permissions(i.guild.default_role, read_messages=False)
        await channel.set_permissions(i.guild.owner, read_messages=True, manage_channels=True)


        for role in i.guild.roles:
            if role.id in staff_role_ids:
                await channel.set_permissions(role, read_messages=True, manage_channels=True)

        await i.response.send_message(f"{channel.mention} has been locked. Only the owner and specified staff roles have full permissions.", ephemeral=True)


        # Retrieve the locklog channel
        locklog = get_locklog_channel(i)
        if locklog is None:
            return  

        log_channel = i.guild.get_channel(locklog)
        if log_channel:
            LockLogEmbed = nextcord.Embed(
                title="Channel Locked",
                description=f"{channel.mention} has been locked.",
                color=nextcord.Color.red()
            )
            LockLogEmbed.set_footer(text=f"Locked by {i.user.name}", icon_url=i.user.avatar.url)
            await log_channel.send(embed=LockLogEmbed)

#
##
###
#### Unlocked COMMAND
###
##
#

    @is_staff_or_admin()
    @nextcord.slash_command(
        name="unlock",
        description="Unlock the channel"
    )
    async def unlock(self, i: nextcord.Interaction):
        # Check if the command is used in a guild
        if i.guild is None:
            await i.response.send_message("This command can only be used in a server (guild).", ephemeral=True)
            return


        # Check if the user has the necessary permissions
        if not i.user.guild_permissions.manage_channels:
            await i.response.send_message("You don't have permission to manage channels.", ephemeral=True)
            return


        # Get the current channel
        channel = i.channel


        # Set permissions to deny everyone and allow the owner and staff roles
        await channel.set_permissions(i.guild.default_role, read_messages=True)
        await channel.set_permissions(i.guild.owner, read_messages=True, manage_channels=True)
        await i.response.send_message(f"{channel.mention} has been unlocked. Everyone has now gotten their permissions to the channel!", ephemeral=True)


        embed = nextcord.Embed(
            title="Channel got unlocked",
            description=f"{channel.mention} Has been unlocked. Now everyone have the permissions again!",
        )
        embed.set_footer(text=f"channel unlocked by {i.user.name}", icon_url=i.user.avatar.url)


##Send out a log message

        # Retrieve the locklog channel
        locklog = get_locklog_channel(i)
        if locklog is None:
            return
        print("Unlock", locklog)  

        log_channel = i.guild.get_channel(locklog)
        if log_channel:
            print(f"{i.user.name} unlocked a channel")
            LockLogEmbed = nextcord.Embed(
                title="Channel Unlocked",
                description=f"A channel got unlocked!",
                color= nextcord.Color.green()
            )
            LockLogEmbed.set_footer(text=f"Unlocked by {i.user.name}", icon_url=i.user.avatar.url)
            await log_channel.send(embed=LockLogEmbed)




def setup(bot: commands.Bot):
    bot.add_cog(Lock(bot))