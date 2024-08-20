import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3
import os
from dotenv import load_dotenv


# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


class SetupWelcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(name="setup_welcome", description="Set up a welcome channel")
    async def setup_welcome_channel(self, interaction: nextcord.Interaction, welcome_channel: nextcord.TextChannel = None, on_join_role: nextcord.Role = None, leave_channel: nextcord.TextChannel = None):
        # Use `NULL` to represent no channel or role set
        welcome_channel_id = welcome_channel.id if welcome_channel else None
        join_role_id = on_join_role.id if on_join_role else None
        leave_channel_id = leave_channel.id if leave_channel else None

        cursor.execute(
            'UPDATE guildinfo SET welcome_channel_id = ?, join_role_id = ?, leave_channel_id = ? WHERE guild_id = ?',
            (welcome_channel_id, join_role_id, leave_channel_id, interaction.guild.id)
        )
        database.commit()

        await interaction.response.send_message("Welcome function has been setup! If you wish to remove all this please do the command again without filling out values!", ephemeral=True
        )


class SetupLogs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(name="setup_logs", description="Setup the logs for the server!", guild_ids=[api.GuildID])
    async def logssetup(self, interaction: nextcord.Interaction, modlogs: nextcord.TextChannel = None, serverlogs: nextcord.TextChannel = None, ticketlogs: nextcord.TextChannel = None):
        # Use `NULL` to represent no log channel set
        modlogs_id = modlogs.id if modlogs else None
        serverlogs_id = serverlogs.id if serverlogs else None

        cursor.execute(
            'UPDATE guildinfo SET modlogs = ?, serverlogs = ?WHERE guild_id = ?',
            (modlogs_id, serverlogs_id, interaction.guild.id)
        )
        database.commit()

        await interaction.response.send_message("The logs have been set up! If you wish to remove all this please do the command again without filling out values!", ephemeral=True)


class SetupStats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(name="setup_verify", description="Setup channels like Unverified Stats with a specific verify role!", guild_ids=[api.GuildID])
    async def verified(self, interaction: nextcord.Interaction, verifyrole: nextcord.Role = None, unverified_channel: nextcord.VoiceChannel = None):
        # Use `NULL` to represent no verify role or channel set
        verifyrole_id = verifyrole.id if verifyrole else None
        unverified_channel_id = unverified_channel.id if unverified_channel else None

        cursor.execute(
            'UPDATE guildinfo SET verify_role = ?, unverified_channel = ? WHERE guild_id = ?',
            (verifyrole_id, unverified_channel_id, interaction.guild.id)
        )
        database.commit()

        await interaction.response.send_message("The verified role and unverified channel have been set up! If you wish to remove all this please do the command again without filling out values!", ephemeral=True)


    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(name="setup_statschannels", description="Setup stats-channels like rolecounts & membercount showing as a number on a voice channel! ", guild_ids=[api.GuildID])
    async def statschannels(self, interaction: nextcord.Interaction, membercount: nextcord.VoiceChannel = None, rolecount: nextcord.VoiceChannel = None):
        # Use `NULL` to represent no stats channels set
        membercount_id = membercount.id if membercount else None
        rolecount_id = rolecount.id if rolecount else None

        cursor.execute(
            'UPDATE guildinfo SET membercount_channel = ?, rolecount_channel = ? WHERE guild_id = ?',
            (membercount_id, rolecount_id, interaction.guild.id)
        )
        database.commit()

        await interaction.response.send_message("Stats channels have been set up! If you wish to remove all this please do the command again without filling out values!", ephemeral=True)



class SetupSupport(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(
        name="setup_support",
        description="Setup the support feature enabling support-tickets!",
        guild_ids=[api.GuildID]
    )
    async def support(self, i: nextcord.Interaction, ticketstaff: nextcord.Role = None, ticketlogs: nextcord.TextChannel = None, ticket_category: nextcord.CategoryChannel = None):
        ticketstaff.id = ticketstaff.id if ticketstaff else None
        ticketlogs.id = ticketlogs.id if ticketlogs else None
        ticket_category.id = ticket_category.id if ticket_category else None

        cursor.execute('UPDATE guildinfo SET ticketsupport_role_id = ?, ticketlogs = ?, supportcategory = ? WHERE guild_id = ?', (ticketstaff.id, ticketlogs.id, ticket_category.id, i.guild.id))
        await i.response.send_message("Tickets have been setuped on your server, if you wish to set to remove all this please do the command again without filling out values!", ephemeral=True)



class SetupStaffnBirthday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(
        name="setup_staff",
        description="Setup a specific staff role who can see tickets and do smaller moderation tasks!",
        guild_ids=[api.GuildID]
    )
    async def staffsetup(self, i: nextcord.Interaction, staffrole: nextcord.Role = None):
        staffrole.id = staffrole.id if staffrole else None

        cursor.execute('UPDATE guildinfo SET staffrole_id = ? WHERE guild_id = ?', (staffrole.id, i.guild.id))
        await i.response.send_message("Staff Role has been setup! If you wish to remove all this please do the command again without filling out values!")

    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(
        name="setup_birthday",
        description="Setup a birthday channel where users get pinged on their birthday!",
        guild_ids=[api.GuildID]
    )
    async def birthdaysetup(self, i: nextcord.Interaction, birthdaychannel: nextcord.TextChannel):
        birthdaychannel.id = birthdaychannel.id if birthdaychannel else None       

        cursor.execute('UPDATE guildinfo SET birthday_channel_id = ? WHERE guild_id = ?', (birthdaychannel.id, i.guild.id))
        await i.response.send_message("Birthdaychannel has been setup! If you wish to remove all this please do the command again without filling out values!")



    @application_checks.has_permissions(administrator=True)
    @nextcord.slash_command(
        name="setup_report",
        description="Setup a report channel where users get report other members!",
        guild_ids=[api.GuildID]
    )
    async def birthdaysetup(self, i: nextcord.Interaction, reportchannel: nextcord.TextChannel):
        reportchannel.id = reportchannel.id if reportchannel else None       

        cursor.execute('UPDATE guildinfo SET report_channel = ? WHERE guild_id = ?', (reportchannel.id, i.guild.id))
        await i.response.send_message("report channel has been setup! If you wish to remove all this please do the command again without filling out values!")

def setup(bot: commands.Bot):
    print("Setup Cog Registered")
    bot.add_cog(SetupWelcome(bot))
    bot.add_cog(SetupLogs(bot))
    bot.add_cog(SetupStats(bot))
    bot.add_cog(SetupSupport(bot))
    bot.add_cog(SetupStaffnBirthday(bot))
