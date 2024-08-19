import nextcord
from nextcord.ext import commands
from nextcord.ext import application_checks

class OnError(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, error: nextcord.ApplicationError):
        if isinstance(error, application_checks.ApplicationMissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            await interaction.response.send_message(f"You do not have the required permissions to run this command. Missing permissions: `{missing_permissions}`" ,ephemeral=True)

        elif isinstance(error, application_checks.ApplicationBotMissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            await interaction.response.send_message(f"I do not have the required permissions to run this command. Missing permissions: `{missing_permissions}`", ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred: {error}. Please use /report-bug command to notify the developer about this error!")


def setup(bot: commands.Bot):
    print("On_Error Cog Registered")
    bot.add_cog(OnError(bot))