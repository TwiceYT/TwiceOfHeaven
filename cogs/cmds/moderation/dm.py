import nextcord
from nextcord.ext import commands, application_checks
import api as api

intents = nextcord.Intents.all()


class DM(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

#
##
###
#### EMBED DM COMMAND
###
##
#

    @application_checks.has_guild_permissions(administrator=True)
    @nextcord.slash_command(
    name="dm_embed",
    description="Send a message to a user",
    guild_ids=[api.GuildID]
    )
    async def embeddm(self, i: nextcord.Interaction, user: nextcord.Member, *, field1:str=None ,title="", embed_color: int = 0x3498db):
        try:
            print("Message a user!")

            embed = nextcord.Embed(
                title=title, 
                description="",
                color=embed_color
            )
            embed.add_field(name="", value=field1, inline=False)
            await user.send(embed=embed)

            # Send a confirmation message in the current channel
            await i.response.send_message("Message is sent to the user!", ephemeral=True)
        except nextcord.Forbidden:
            await i.response.send_message("You don't have the necessary permissions to ban that user.")


#
##
###
#### Normal DM COMMAND
###
##
#


    @application_checks.has_guild_permissions(administrator=True)
    @nextcord.slash_command(
    name="dm",
    description="Send a message to a user",
    guild_ids=[api.GuildID]
    )
    async def dm(self, i: nextcord.Interaction, user: nextcord.Member, *, message:str=None ):
        try:
            await user.send(message)
            await i.response.send_message("Message is sent to the user!", ephemeral=True)
        except nextcord.Forbidden:
                    await i.response.send_message("You don't have the necessary permissions to ban that user.")


def setup(bot: commands.Bot):
    print("DM Cog Registered")
    bot.add_cog(DM(bot))