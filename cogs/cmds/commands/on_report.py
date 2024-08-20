import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
SupportID = os.getenv("SupportServerID")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()


def get_bugreport_channel():
    with sqlite3.connect('toh.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT channel_id FROM bugreport WHERE guild_id = ?', (SupportID,))
        channel = cursor.fetchone()
        if channel:
            return channel[0]
        else:
            return None
        


def get_report_channel(i: nextcord.Interaction):
    with sqlite3.connect('toh.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT report_channel FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
        repchannel = cursor.fetchone()
        if repchannel:
            return repchannel[0]
        else:
            return None


class BugReportModal(nextcord.ui.Modal):
    def __init__(self, closesbug_view):
        super().__init__("Bot Bugreport", custom_id="bugrepmodal", timeout=100.0)
        self.closesbug_view = closesbug_view
        self.server = nextcord.ui.TextInput(
            label="What is the name of the current server?",
            placeholder="Please provide a the server name you are reporting from or recieve the issue.",
            required=True,
            max_length=100,
        )
        self.add_item(self.server)
        self.command = nextcord.ui.TextInput(
            label="Which command or function?",
            placeholder="Please enter which command or function you had issues with.",
            required=True,
            max_length=100
        )
        self.add_item(self.command)
        self.description = nextcord.ui.TextInput(
            label="Please give us a description of the issue",
            placeholder="Please provide a detailed explanation of what is not working and what happens.",
            required=True,
            max_length=2048,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.description)
        self.on_error = nextcord.ui.TextInput(
            label="If any errors message:",
            placeholder="Copy paste the error you recieved in here!",
            required=True,
            max_length=2048,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.on_error)

    async def callback(self, interaction: nextcord.Interaction):
        await self.callbackbugreport(interaction)

    async def callbackbugreport(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        server = self.server.value
        description = self.description.value
        command = self.command.value
        error = self.on_error.value

        embed = nextcord.Embed(
            title="Bot Bug Report",
            color=nextcord.Colour.gold()
        )
        embed.add_field(name="Server", value=server, inline=False)
        embed.add_field(name="Bot Command", value=command, inline=False)
        embed.add_field(name="Description:", value=description, inline=False)
        embed.add_field(name="Error message", value=error, inline=False)
        embed.set_footer(text="Sent in by: " + interaction.user.display_name, icon_url=interaction.user.avatar.url)


        channelid = get_bugreport_channel()
        if channelid is None:
            return  

        channel = interaction.guild.get_channel(channelid)
        if channel:
            await channel.send(embed=embed)
            await interaction.followup.send("Your report has been sent to the Dev-Team.", ephemeral=True)


class BugReport(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="bot-bugreport",
        description="Report any bugs you are experiencing to the Bot-Developer of the bot",
        guild_ids=[api.GuildID]
    )
    async def bugreport(self, i: nextcord.Interaction):
        modal = BugReportModal(closesbug_view=None)
        await i.response.send_modal(modal)



#
##
###
##
#


class ReportModal(nextcord.ui.Modal):
    def __init__(self, closesrep_view):
        super().__init__("report", custom_id="reportmodal", timeout=100.0)
        self.closesbug_view = closesrep_view
        self.name = nextcord.ui.TextInput(
            label="What is the name of the user?",
            placeholder="Please provide a the name of the user you wish to report!",
            required=True,
            max_length=100,
        )
        self.add_item(self.name)
        self.explaination = nextcord.ui.TextInput(
            label="Report Reason",
            placeholder="Please provide a detailed explanation of this user did that you wish to report",
            required=True,
            max_length=2048,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.explaination)
        self.notes = nextcord.ui.TextInput(
            label="Any extra notes?",
            placeholder="Is there anything else you want us to know besides their actions you wish to report",
            required=True,
            max_length=2048,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.notes)

    async def callback(self, interaction: nextcord.Interaction):
        await self.callbackreport(interaction)

    async def callbackreport(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        name = self.name.value
        reason = self.explaination.value
        notes = self.notes.value

        embed = nextcord.Embed(
            title="Bot Bug Report",
            color=nextcord.Colour.gold()
        )
        embed.add_field(name="Reported User:", value=name, inline=False)
        embed.add_field(name="Report Reason", value=reason, inline=False)
        embed.add_field(name="Notes:", value=notes, inline=False)
        embed.set_footer(text="Sent in by: " + interaction.user.display_name, icon_url=interaction.user.avatar.url)


        repchannel = get_report_channel(interaction)
        if repchannel is None:
            return  

        channel = interaction.guild.get_channel(repchannel)
        if channel:
            await channel.send(embed=embed)
            await interaction.followup.send("Your report has been sent to the staff team!", ephemeral=True)

class Report(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="report",
        description="Report any bug user on the server",
        guild_ids=[api.GuildID]
    )
    async def report(self, i: nextcord.Interaction):
        modal = ReportModal(closesrep_view=None)
        await i.response.send_modal(modal)


def setup(bot: commands.Bot):
    print("Report Cog Registered")
    bot.add_cog(BugReport(bot))
    bot.add_cog(Report(bot))