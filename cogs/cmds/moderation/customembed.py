import nextcord
from nextcord.ext import commands, application_checks
import webcolors
import api

class CustomEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @application_checks.has_permissions(manage_messages=True)
    @nextcord.slash_command(
        name="custom_embed",
        description="Create a custom embed.",
        guild_ids=[api.GuildID]
    )
    async def custom_embed(self, i: nextcord.Interaction, channel: nextcord.abc.GuildChannel):
        modal = CustomEmbedModal(channel.id)  # Pass the channel ID to the modal
        await i.response.send_modal(modal)

class CustomEmbedModal(nextcord.ui.Modal):
    def __init__(self, channel_id: int):
        super().__init__("Custom Embed", custom_id="custom_embed_modal", timeout=60.0)
        self.channel_id = channel_id  # Store the channel ID
        self.embed_title = nextcord.ui.TextInput(label="Embed Title", placeholder="Enter the title of the embed here.", required=True)
        self.embed_description = nextcord.ui.TextInput(label="Embed Description", placeholder="Enter the description of the embed here.", required=False, max_length=2048, min_length=1, style=nextcord.TextInputStyle.paragraph)
        self.embed_color = nextcord.ui.TextInput(label="Embed Color", placeholder="Enter the color of the embed here. (e.g., blue)", required=False)
        self.embed_color.default = "gold"  # Set the default value here
        self.add_item(self.embed_title)
        self.add_item(self.embed_description)
        self.add_item(self.embed_color)

        self.embed = nextcord.Embed()

    async def callback(self, interaction: nextcord.Interaction):
        self.embed.title = self.embed_title.value
        self.embed.description = self.embed_description.value

        try:
            color_rgb = webcolors.name_to_rgb(self.embed_color.value)
            self.embed.color = nextcord.Colour.from_rgb(color_rgb[0], color_rgb[1], color_rgb[2])
            
            channel = interaction.guild.get_channel(self.channel_id)
            if channel:
                await channel.send(embed=self.embed)
            else:
                await interaction.response.send_message("Invalid channel. Please try again.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Invalid color name. Please enter a valid color name.", ephemeral=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            await interaction.response.send_message("An error occurred while processing your request. Please try again later.", ephemeral=True)

def setup(bot):
    bot.add_cog(CustomEmbed(bot))

