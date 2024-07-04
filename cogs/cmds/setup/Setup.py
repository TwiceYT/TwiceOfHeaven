import nextcord
from nextcord.ext import commands, application_checks
import api
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
intents = nextcord.Intents.all()

database = sqlite3.connect(DBFile)
cursor = database.cursor()

class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup",
        description="Setup the bot",
        guild_ids=[api.GuildID]
    )
    async def setup(self, i: nextcord.Interaction):
        guild = i.guild

        # Create select menus for channels and roles
        voice_channels = [nextcord.SelectOption(label=channel.name, value=str(channel.id)) for channel in guild.voice_channels]
        channels = [nextcord.SelectOption(label=channel.name, value=str(channel.id)) for channel in guild.text_channels]
        roles = [nextcord.SelectOption(label=role.name, value=str(role.id)) for role in guild.roles]
        categories = [nextcord.SelectOption(label=category.name, value=str(category.id)) for category in guild.categories]

        class SetupViewStep1(nextcord.ui.View):
            def __init__(self, data=None):
                super().__init__()
                self.data = data or {}

            @nextcord.ui.select(
                placeholder="Select welcome channel...",
                min_values=1,
                max_values=1,
                options=channels
            )
            async def select_welcome(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['welcome_channel_id'] = int(select.values[0])
                await i.response.send_message(f"Selected welcome channel: {self.data['welcome_channel_id']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select leave channel...",
                min_values=1,
                max_values=1,
                options=channels
            )
            async def select_leave(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['leave_channel_id'] = int(select.values[0])
                await i.response.send_message(f"Selected leave channel: {self.data['leave_channel_id']}", ephemeral=True)
            
            @nextcord.ui.select(
                placeholder="Select welcome role...",
                min_values=1,
                max_values=1,
                options=roles
            )
            async def select_join_role_id(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['join_role_id'] = int(select.values[0])
                await i.response.send_message(f"Selected leave channel: {self.data['join_role_id']}", ephemeral=True)            


            @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.green)
            async def next(self, button: nextcord.ui.Button, i: nextcord.Interaction):
                await i.response.send_message("Next step", view=SetupViewStep2(self.data), ephemeral=True)

##

        class SetupViewStep2(nextcord.ui.View):
            def __init__(self, data=None):
                super().__init__()
                self.data = data or {}

            @nextcord.ui.select(
                placeholder="Select role count channel...",
                min_values=1,
                max_values=1,
                options=voice_channels
            )
            async def select_role_count(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['rolecount_channel'] = int(select.values[0])
                await i.response.send_message(f"Selected role count channel: {self.data['rolecount_channel']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select membercount channel...",
                min_values=1,
                max_values=1,
                options=voice_channels
            )
            async def select_member_count(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['membercount_channel'] = int(select.values[0])
                await i.response.send_message(f"Selected member count channel: {self.data['membercount_channel']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select unverified channel...",
                min_values=1,
                max_values=1,
                options=voice_channels
            )
            async def select_unverified(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['unverified_channel'] = int(select.values[0])
                await i.response.send_message(f"Selected unverified channel: {self.data['unverified_channel']}", ephemeral=True)


            @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.green)
            async def next(self, button: nextcord.ui.Button, i: nextcord.Interaction):
                await i.response.send_message("Next step", view=SetupViewStep3(self.data), ephemeral=True)



##

        class SetupViewStep3(nextcord.ui.View):
            def __init__(self, data=None):
                super().__init__()
                self.data = data or {}

            @nextcord.ui.select(
                placeholder="Select verify role...",
                min_values=1,
                max_values=1,
                options=roles
            )
            async def select_verify_role(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['verify_role'] = int(select.values[0])
                await i.response.send_message(f"Selected verify role: {self.data['verify_role']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select staff role...",
                min_values=1,
                max_values=1,
                options=roles
            )
            async def select_staff_role(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['staffrole_id'] = int(select.values[0])
                await i.response.send_message(f"Selected staff role: {self.data['staffrole_id']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select ticket support role...",
                min_values=1,
                max_values=1,
                options=roles
            )
            async def select_ticket_support(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['ticketsupport_role_id'] = int(select.values[0])
                await i.response.send_message(f"Selected ticket support role: {self.data['ticketsupport_role_id']}", ephemeral=True)
        

            @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.green)
            async def next(self, button: nextcord.ui.Button, i: nextcord.Interaction):
                await i.response.send_message("Next step", view=SetupViewStep4(self.data), ephemeral=True)

        class SetupViewStep4(nextcord.ui.View):
            def __init__(self, data=None):
                super().__init__()
                self.data = data or {}

            @nextcord.ui.select(
                placeholder="Select birthday channel...",
                min_values=1,
                max_values=1,
                options=channels
            )
            async def select_birthday_channel(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['birthday_channel_id'] = int(select.values[0])
                await i.response.send_message(f"Selected birthday channel: {self.data['birthday_channel_id']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select modlogs channel...",
                min_values=1,
                max_values=1,
                options=channels
            )
            async def select_modlogs(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['modlogs'] = int(select.values[0])
                await i.response.send_message(f"Selected modlogs channel: {self.data['modlogs']}", ephemeral=True)

            @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.green)
            async def next(self, button: nextcord.ui.Button, i: nextcord.Interaction):
                await i.response.send_message("Next step", view=SetupViewStep5(self.data), ephemeral=True)

        class SetupViewStep5(nextcord.ui.View):
            def __init__(self, data=None):
                super().__init__()
                self.data = data or {}

            @nextcord.ui.select(
                placeholder="Select ticket logs channel...",
                min_values=1,
                max_values=1,
                options=channels
            )
            async def select_ticket_logs(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['ticketlogs'] = int(select.values[0])
                await i.response.send_message(f"Selected ticket logs channel: {self.data['ticketlogs']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select server logs channel...",
                min_values=1,
                max_values=1,
                options=channels
            )
            async def select_server_logs(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['serverlogs'] = int(select.values[0])
                await i.response.send_message(f"Selected server logs channel: {self.data['serverlogs']}", ephemeral=True)

            @nextcord.ui.select(
                placeholder="Select support category...",
                min_values=1,
                max_values=1,
                options=categories  
            )
            async def select_support_category(self, select: nextcord.ui.Select, i: nextcord.Interaction):
                self.data['supportcategory'] = int(select.values[0])
                await i.response.send_message(f"Selected support category: {self.data['supportcategory']}", ephemeral=True)

            @nextcord.ui.button(label="Submit", style=nextcord.ButtonStyle.success)
            async def submit(self, button: nextcord.ui.Button, i: nextcord.Interaction):
                guild = i.guild
                cursor.execute("""
                    INSERT INTO guildinfo (
                        guild_id, guild_name, modlogs, welcome_channel_id, join_role_id, leave_channel_id, 
                        membercount_channel, rolecount_channel, unverified_channel, staffrole_id, 
                        ticketsupport_role_id, birthday_channel_id, verify_role, ticketlogs, serverlogs, 
                        supportcategory
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(guild_id) DO UPDATE SET
                        guild_name=excluded.guild_name,
                        modlogs=excluded.modlogs,
                        welcome_channel_id=excluded.welcome_channel_id,
                        join_role_id=excluded.join_role_id,
                        leave_channel_id=excluded.leave_channel_id,
                        membercount_channel=excluded.membercount_channel,
                        rolecount_channel=excluded.rolecount_channel,
                        unverified_channel=excluded.unverified_channel,
                        staffrole_id=excluded.staffrole_id,
                        ticketsupport_role_id=excluded.ticketsupport_role_id,
                        birthday_channel_id=excluded.birthday_channel_id,
                        verify_role=excluded.verify_role,
                        ticketlogs=excluded.ticketlogs,
                        serverlogs=excluded.serverlogs,
                        supportcategory=excluded.supportcategory
                """, (
                    guild.id, guild.name, self.data.get('modlogs'), self.data.get('welcome_channel_id'), self.data.get('join_role_id'), self.data.get('leave_channel_id'),
                    self.data.get('membercount_channel'), self.data.get('rolecount_channel'), self.data.get('unverified_channel'),
                    self.data.get('staffrole_id'), self.data.get('ticketsupport_role_id'), self.data.get('birthday_channel_id'), self.data.get('verify_role'),
                    self.data.get('ticketlogs'), self.data.get('serverlogs'), self.data.get('supportcategory')
                ))
                database.commit()
                await i.response.send_message("Setup complete! Your channels will now be active with logs, redo the setup command if you want to change channels!", ephemeral=True)

        view = SetupViewStep1()
        await i.response.send_message(f"Note that some channels might be irrelevant for you, then keep the options blank.\n" f"Do '/setup_help' if you need guidance about the setup\n\n" f"Please select the channels and roles for setup:", view=view, ephemeral=True)


def setup(bot: commands.Bot):
    print("Setup Cog Registered")
    bot.add_cog(Setup(bot))