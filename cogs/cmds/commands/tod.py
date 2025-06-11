import nextcord
from nextcord.ext import commands
import requests
import json

intents = nextcord.Intents.all()

class Tod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_and_send_question(self, interaction: nextcord.Interaction, endpoint: str, title: str, color: nextcord.Color):
        try:
            response = requests.get(f"https://api.truthordarebot.xyz/v1/{endpoint}")
            response.raise_for_status()
            json_data = response.json()

            if 'question' in json_data:
                embed = nextcord.Embed(
                    title=title,
                    description=f'"{json_data["question"]}"',
                    color=color
                )
                embed.timestamp = interaction.created_at
                embed.set_footer(text="Generated from truthordarebot.xyz")

                view = TodBtn(self)
                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.response.send_message("Error: Missing 'question' key in API response.")
        except requests.RequestException as e:
            print(f"Error fetching {title.lower()}: {e}")
            await interaction.response.send_message(f"Error fetching {title.lower()}. Please try again later.")

    @nextcord.slash_command(
        name="tod",
        description="Start TOD"
    )
    async def tod(self, i: nextcord.Interaction):
        embed = nextcord.Embed(
            title="Start TOD Journey here!",
            description="Click on the buttons below to start using the TOD feature!",
        )
        view = TodBtn(self)
        await i.response.send_message(embed=embed, view=view)

class TodBtn(nextcord.ui.View):
    def __init__(self, cog: Tod):
        super().__init__(timeout=None)
        self.cog = cog

    @nextcord.ui.button(label="Truth", style=nextcord.ButtonStyle.green, custom_id="truth")
    async def truth(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.fetch_and_send_question(interaction, "truth", "Truth", nextcord.Color.dark_blue())

    @nextcord.ui.button(label="Dare", style=nextcord.ButtonStyle.danger, custom_id="dare")
    async def dare(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.fetch_and_send_question(interaction, "dare", "Dare", nextcord.Color.dark_red())

    @nextcord.ui.button(label="Would You Rather", style=nextcord.ButtonStyle.primary, custom_id="wyr")
    async def wyr(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.fetch_and_send_question(interaction, "wyr", "Would You Rather", nextcord.Color.green())

    @nextcord.ui.button(label="Never Have I Ever", style=nextcord.ButtonStyle.secondary, custom_id="never")
    async def never(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.fetch_and_send_question(interaction, "nhie", "Never Have I Ever", nextcord.Color.gold())

    @nextcord.ui.button(label="Paranoia", style=nextcord.ButtonStyle.blurple, custom_id="paranoia")
    async def paranoia(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.fetch_and_send_question(interaction, "paranoia", "Paranoia", nextcord.Color.dark_purple())

class PersistentViewBtn(commands.Cog):
    def __init__(self, bot: commands.Bot, tod_cog: Tod):
        self.bot = bot
        self.tod_cog = tod_cog
        self.setup_done = False

    async def setup_hook(self) -> None:
        if not self.setup_done:
            self.bot.add_view(TodBtn(self.tod_cog))
            self.setup_done = True

    @commands.Cog.listener()
    async def on_ready(self):
        await self.setup_hook()


def setup(bot: commands.Bot):
    print("TOD Cog Registered")
    tod_cog = Tod(bot)
    bot.add_cog(tod_cog)
    bot.add_cog(PersistentViewBtn(bot, tod_cog))
