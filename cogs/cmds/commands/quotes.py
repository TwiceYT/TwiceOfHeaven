import nextcord
from nextcord.ext import commands, application_checks
import api
import requests
import json

intents = nextcord.Intents.all()


class Quotes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="quotes",
        description="Generate a random quote!",
        guild_ids=[api.GuildID]
    )
    async def quote(self, i: nextcord.Interaction):
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)

        embed = nextcord.Embed(
            title="Get inspired",
            description='"'+json_data[0]['q'] + '"' "   ~~ " + json_data[0]['a'],
            color=nextcord.Color.brand_red()
        )
        embed.timestamp = i.created_at 
        embed.set_footer(text="Generated from Zenquote.io")
        await i.response.send_message(embed=embed)


def setup(bot: commands.Bot):
    print("quotes Cog Registered")
    bot.add_cog(Quotes(bot))