import nextcord
from nextcord.ext import commands, application_checks
import os
import asyncio
import sqlite3
from dotenv import load_dotenv
import api

# Load environment variables
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

def get_staffID(guild_id):
    cursor.execute('SELECT staffrole_id FROM guildinfo WHERE guild_id = ?', (guild_id,))
    staff_role = cursor.fetchone()
    if staff_role:
        return staff_role[0]
    else:
        return None

def get_ticketsupportID(guild_id):
    cursor.execute('SELECT ticketsupport_role_id FROM guildinfo WHERE guild_id = ?', (guild_id,))
    support_role = cursor.fetchone()
    if support_role:
        return support_role[0]
    else:
        return None

def get_supportcategory(guild_id):
    cursor.execute('SELECT supportcategory FROM guildinfo WHERE guild_id = ?', (guild_id,))
    category = cursor.fetchone()
    if category:
        return category[0]
    else:
        return None

def get_supportlogs(guild_id):
    cursor.execute('SELECT ticketlogs FROM guildinfo WHERE guild_id = ?', (guild_id,))
    ticketlog = cursor.fetchone()
    if ticketlog:
        return ticketlog[0]
    else:
        return None

class SupportModal(nextcord.ui.Modal):
    def __init__(self, closeticket_view, guild_id):
        super().__init__("Support Ticket", custom_id="support_modal", timeout=60.0)
        self.closeticket_view = closeticket_view
        self.guild_id = guild_id
        self.topic = nextcord.ui.TextInput(
            label="Topic",
            placeholder="Enter the topic of your issue",
            required=True,
            max_length=100
        )
        self.add_item(self.topic)
        self.embed_description = nextcord.ui.TextInput(
            label="What is your issue?",
            placeholder="Please provide a detailed explanation of the issues you're experiencing.",
            required=True,
            max_length=2048,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.embed_description)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer()  # Defer the interaction response

        embed = nextcord.Embed(
            title="Support Ticket",
            color=nextcord.Colour.gold()
        )
        embed.add_field(name="Topic", value=self.topic.value, inline=False)
        embed.add_field(name="Description", value=self.embed_description.value, inline=False)
        embed.set_footer(text="Please be as detailed as possible, and you will get a response as soon as possible.")

        user = interaction.user
        guild = interaction.guild
        ticket_channel_name = f"ticket-{user.name}"

        STAFF_ROLE_ID = get_staffID(self.guild_id)
        TICKET_SUPPORT_ID = get_ticketsupportID(self.guild_id)
        SUPPORT_CATEGORY_ID = get_supportcategory(self.guild_id)

        StaffRole = guild.get_role(STAFF_ROLE_ID)
        SupportRole = guild.get_role(TICKET_SUPPORT_ID)

        if StaffRole is None or SupportRole is None:
            await interaction.followup.send("Error: Required role not found. Please contact an administrator.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            guild.me: nextcord.PermissionOverwrite(read_messages=True),
            user: nextcord.PermissionOverwrite(read_messages=True),
            StaffRole: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
            SupportRole: nextcord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        category = guild.get_channel(SUPPORT_CATEGORY_ID)
        if category is None:
            await interaction.followup.send("Error: Support category not found. Please contact an administrator.", ephemeral=True)
            return

        ticket_channel = await guild.create_text_channel(ticket_channel_name, overwrites=overwrites, category=category)
        view = Closeticket(closeticket_view=self.closeticket_view, guild_id=self.guild_id)

        await ticket_channel.send(content=f"{user.mention}, your ticket has been created.", embed=embed, view=view)
        await user.send(f"Your support ticket has been created. Please use the channel {ticket_channel.mention} for further communication.")



class CreateSupportButton(nextcord.ui.View):
    def __init__(self, closeticket_view=None, guild_id=None):
        super().__init__(timeout=None)
        self.closeticket_view = closeticket_view
        self.guild_id = guild_id

    @nextcord.ui.button(label="🎫 Support Ticket", style=nextcord.ButtonStyle.green, custom_id="create_ticket")
    async def createbtn(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = SupportModal(self.closeticket_view, guild_id=self.guild_id)
        await interaction.response.send_modal(modal)


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def btncreatesup(self, ctx: commands.Context):
        view = CreateSupportButton(guild_id=ctx.guild.id)
        await ctx.send("Click the button below to create a Support-Ticket:", view=view)

    @application_checks.has_guild_permissions(administrator=True)
    @nextcord.slash_command(name="support", description="Create a Support-Ticket", guild_ids=[api.GuildID])
    async def support(self, interaction: nextcord.Interaction):
        STAFF_ROLE_ID = get_staffID(interaction.guild.id)
        TICKET_SUPPORT_ID = get_ticketsupportID(interaction.guild.id)
        user_roles = [role.id for role in interaction.user.roles]

        if STAFF_ROLE_ID in user_roles or TICKET_SUPPORT_ID in user_roles:
            view = CreateSupportButton(guild_id=interaction.guild.id)
            await interaction.response.send_message("Click the button below to create a Support-Ticket:", view=view)
        else:
            await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)


class Closeticket(nextcord.ui.View):
    def __init__(self, closeticket_view, guild_id, **kwargs):
        super().__init__(**kwargs)
        self.closeticket_view = closeticket_view
        self.guild_id = guild_id

    @nextcord.ui.button(label="🔒 Close Ticket", style=nextcord.ButtonStyle.danger, custom_id="close_ticket")
    async def closebtn(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.close(interaction)

    async def close(self, interaction: nextcord.Interaction):
        user = interaction.user
        channel = interaction.channel

        if self.is_support_channel(channel):
            await self.close_support_ticket(channel, user)
        else:
            await interaction.response.send_message("This command can only be used in a Support channel.", ephemeral=True)

    def is_support_channel(self, channel):
        return isinstance(channel, nextcord.TextChannel) and channel.category_id == get_supportcategory(self.guild_id)

    async def close_support_ticket(self, ticket_channel, user):
        try:
            messages = await ticket_channel.history(limit=None).flatten()
            transcript = "\n".join([f"{msg.author.display_name}: {msg.content}" for msg in messages])

            transcripts_dir = "transcripts"
            os.makedirs(transcripts_dir, exist_ok=True)

            file_name = f"transcript_{ticket_channel.id}.txt"
            file_path = os.path.join(transcripts_dir, file_name)

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(transcript)

            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()

            await user.send(f"Here is the transcript of your Support-Ticket:", file=nextcord.File(file_path))
            TICKET_LOGS_CHANNEL_ID = get_supportlogs(self.guild_id)
            log_channel = ticket_channel.guild.get_channel(TICKET_LOGS_CHANNEL_ID)
            await log_channel.send(content=f"Support Ticket Closed by {user.mention} in {ticket_channel.name}. Transcript file:", file=nextcord.File(file_path))

            await asyncio.sleep(2)
            os.remove(file_path)
            await ticket_channel.delete()

        except Exception as e:
            print(f"An error occurred while closing the support ticket: {e}")


class PersistentViewSupports(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.setup_done = False

    async def setup_hook(self) -> None:
        if not self.setup_done:
            closeticket_view = Closeticket(closeticket_view=None, guild_id=None)
            createsupportbutton_view = CreateSupportButton(closeticket_view, guild_id=None)
            self.bot.add_view(createsupportbutton_view)
            self.bot.add_view(closeticket_view)
            self.setup_done = True

    @commands.Cog.listener()
    async def on_ready(self):
        await self.setup_hook()


def setup(bot):
    bot.add_cog(Support(bot))
    bot.add_cog(PersistentViewSupports(bot))