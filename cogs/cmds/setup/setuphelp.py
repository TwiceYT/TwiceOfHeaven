import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")


intents = nextcord.Intents.all()

database = sqlite3.connect(DBFile)
cursor = database.cursor()


class HelpSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup_info",
        description="Help commands"
    )   
    async def helpsetup(self, i: nextcord.Interaction):
        embed = nextcord.Embed(
            title="TwiceOfHeaven Setups",
            description="Short explination about the setups",
            color=nextcord.Color.blue()
        )
        embed.add_field(
            name="What is the setup for?",
            value=f"The setup is another alternative for a dashboard unfortunately TOH is not supported by a dashboard and therefor uses a setup command. This command gives you the ability to choose which channels the bot logs modactions as well as welcome channels and server stats!\n",
            inline=False
        )
        embed.add_field(
            name="Welcome Channel",
            value=f"By setting up this channel, the bot will send out a welcome message when a new members joins the server. You will also be able to setup a custom role to be given automatically when joining\n",
            inline=False
        )
        embed.add_field(
            name="Leaving Channel",
            value=f"This will be the opposite of the welcoming channel, rather the bot sending out message when a user leaves the server.\n",
            inline=False
        )
        embed.add_field(
            name="Welcome Role",
            value=f"Under this option you will be able to choose a custom role to be automatically given to new users.\n",
            inline=False
        )
        embed.add_field(
            name="Stats channels",
            value=f"The bot also supports you creating stats channel such as membercount, amount of unverified members and a role count. Those numbers will be shown in a voice channel which name changes with the stats!\n",
            inline=False
        )
        embed.add_field(
            name="Role Count",
            value=f"Role Count channel will be a voice channel, this voice channel will have the same name as the amount of roles there is in the server, this works like public stats!\n",
            inline=False
        )
        embed.add_field(
            name="MemberCount",
            value=f"The MemberCount channel will show the amount of members there currently are in the server.\n",
            inline=False
        )
        embed.add_field(
            name="Unverified Channel",
            value=f"If you choose to have a verified role to get access to channels, this will be the stats option of it. It will show the amount of members who not yet have the role. This would help you manage the amount of non-verfied members.\n",
            inline=False
        )
        embed.add_field(
            name="Verify Role",
            value=f"This will be the Verify role that the verified channel will count. The bot will also send out a verify button by the command !verify.\n",
            inline=False
        )
        embed.add_field(
            name="Staffrole",
            value=f"This will be the role you wish to be able to view supporttickets, and also a role you would use for all your staffmembers within the server. Will also get certain permission such as locking channels!\n",
            inline=False
        )
        embed.add_field(
            name="TicketSupport Role",
            value=f"This is a extra role for users you want to be able to help with tickets that necessarily aren't staff-members rather outsiders or developers.\n",
            inline=False
        )
        embed.add_field(
            name="\nbirthday channel",
            value=f"This will be the channel the bot sends out birthday messages in, the bot will have a command where users can put in their birthday and will then be tagged in this channel on that day for under members to congratulate.\n",
            inline=False
        )
        embed.add_field(
            name="\nModlogs",
            value=f"This will be the channel that the bot saves all mod data, such as banned users, kicked members, warnings or other staff actions\n",
            inline=False
        )
        embed.add_field(
            name="TicketLogs channel",
            value=f"This is the channel where the transcripts (receipts) of the closed tickets will be stored, giving the staffs a chance to read them after being closed! Note that a transcript will be sent to the regarding user as well!\n",
            inline=False
        )
        embed.add_field(
            name="Server Logs",
            value=f"This will work almost like modlogs however this is rather changes done by users or the bot. For example creation of new channels, edited messages etc\n",
            inline=False
        )
        embed.add_field(
            name="Support Category",
            value=f"This will be the category which the tickets will appear under, you are recommended to create a seperate category for this!\n",
            inline=False
        )
        embed.add_field(
            name="Information",
            value="By not filling in anything in the boxes you are automatically setting it to none, this means that even if you do the setup again you can remove some of the setup by simply not filling the channels out again. Obs, if you run the setup command... Make sure to always fill all the channels again, or they will be set to none and not work as intended. By simply not filling it out, you can ignore those functions you dont wish to have.",
            inline=False
        )
        embed.add_field(
            name="Questions regarding the bot?",
            value="If you by any chance would have any questions regarding this bot, feel free to message the creator! Discord: twiceee",
            inline=False
        )
        await i.response.send_message(embed=embed, ephemeral=True)



    @nextcord.slash_command(
        name="setup_help",
        description="Commands and information about the setup!"
    )
    async def setuphelp(self, i: nextcord.Interaction):
        embed = nextcord.Embed(
            title="Setup Help",
            description="Do you need help with what to setup and and how?",
            color=nextcord.Color.blue()
        )
        embed.add_field(
            name="/setup_welcome", 
            value="You can setup a welcome channel, a onjoin role and a leave channel. Here you choose which channels welcome & leave messages should come to and if any roles should be given when they join. You can also remove those channels by making the command again and simply not adding a value, this will make it being set to null!")
        embed.add_field(
            name="/setup_logs",
            value="There are modlogs and serverlogs, modlogs are logs that saves moderational actions such as bans made by the bot and other commands that are used for moderational purposes by the bot! Serverlogs on the other hand logs that is about the server, members joining vc, channels being created etc."
        )
        embed.add_field(
            name="setup_verify",
            value="The Verify setup contains selecting a channel and a role. The role will be the official verify role, you can make members obtain it by using selfroles or onjoin role being given. You will have to make channels restricted to only allow the verify role yourself. The voice channel on the otherhand will change name to Unverified: number. It will essentially show how many users there currently are who have not obtained this role and help you manage those members. If you dont wish to have this channel feel free to leave it."
        )
        embed.add_field(
            name="/setup_statschannels",
            value="There are 2 different stats, membercount and rolecount. When setting those two you will select 2 voice channels which will similiarly to unverfied number show membercount and rolecount by having the voice channels names changed!"
        )
        embed.add_field(
            name="/setup_support",
            value="Here you can setup a support category as where all ticket channels will appear/created. You will also be able to select ticketlog channels where a transcript of all tickets will be stored! Nonetheless you will setup a support role who have perms to view and moderate the tickets."
        )
        embed.add_field(
            name="/setup_staff",
            value="You can setup staffrole, this role will be able to handle smaller moderational tasks like locking channels etc!"
        )
        embed.add_field(
            name="/setup_birthday",
            value="This contains a function where users can add their birthday by typing birthday-set and on their birthday in this specific channel they will be pinged and congratulated by the bot and perhaps other users seeing this birthday."
        )
        embed.add_field(
            name="/setup_report",
            value="This contains a function where users can report other members! Set a channel up and reports will be sent into this channel by users writing /report"
        )
        embed.add_field(
            name="Wish to remove channel?",
            value="If you have setup a channel and wish to remove the sync, please write the command again and simply dont fill out the values. By not setting a value the channel will be set to null and the function will be disabled."
        )
        await i.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    print("Help Cog Registered")
    bot.add_cog(HelpSetup(bot))