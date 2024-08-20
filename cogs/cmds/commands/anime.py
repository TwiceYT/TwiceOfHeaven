import nextcord
from nextcord.ext import commands
import requests
import os
from dotenv import load_dotenv
import json
import requests
import api
import random

# Load environment variables
load_dotenv(dotenv_path='config/config.env')


# Bot setup
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

class Anime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_random_gif(self, search_term: str):
            """
            Fetch a random GIF based on the search term using Tenor API.
            """
            # Define API key and client key here
            TENOR_API_KEY = os.getenv("TenorAPI")
            CLIENT_KEY = "Discord bot"

            response = requests.get(
                f"https://tenor.googleapis.com/v2/search?q={search_term}&key={TENOR_API_KEY}&client_key={CLIENT_KEY}&limit=100"
            )

            if response.status_code == 200:
                data = json.loads(response.content)
                gifs = [result.get('media_formats', {}).get('gif', {}).get('url') for result in data.get('results', []) if result.get('media_formats', {}).get('gif', {}).get('url')]
                
                if gifs:
                    return random.choice(gifs)
                else:
                    return None
            else:
                return None

    @nextcord.slash_command(name="kiss", description="Search for kiss GIFs using Tenor API", guild_ids=[api.GuildID])
    async def kiss(self, i: nextcord.Interaction, member: nextcord.Member):
        # Define the search term for the kiss command
        search_term = "Anime Romantic Kiss"

        # Fetch a random GIF using the helper function
        gif_url = await self.fetch_random_gif(search_term)

        # Create and send the embed based on the result
        if gif_url:
            embed = nextcord.Embed(
                title=f"{i.user.display_name} kisses {member.name}!",  # Custom title
                color=nextcord.Color.blue()
            )
            embed.set_image(url=gif_url)
            embed.set_author(name="", icon_url=i.user.avatar.url)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(f"No GIFs found for '{search_term}'")



    @nextcord.slash_command(name="hug", description="Search for hug GIFs using Tenor API", guild_ids=[api.GuildID])
    async def hug(self, i: nextcord.Interaction, member: nextcord.Member):
        # Define the search term for the hug command
        search_term = "Anime Hug"

        # Fetch a random GIF using the helper function
        gif_url = await self.fetch_random_gif(search_term)

        # Create and send the embed based on the result
        if gif_url:
            embed = nextcord.Embed(
                title=f"{i.user.display_name} hugs {member.name}!",  # Custom title
                color=nextcord.Color.blue()
            )
            embed.set_image(url=gif_url)
            embed.set_author(name="", icon_url=i.user.avatar.url)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(f"No GIFs found for '{search_term}'")


    @nextcord.slash_command(name="slap", description="Search for slap GIFs using Tenor API", guild_ids=[api.GuildID])
    async def slap(self, i: nextcord.Interaction, member: nextcord.Member):
        # Define the search term for the hug command
        search_term = "Anime slap"

        # Fetch a random GIF using the helper function
        gif_url = await self.fetch_random_gif(search_term)

        # Create and send the embed based on the result
        if gif_url:
            embed = nextcord.Embed(
                title=f"{i.user.display_name} slaps {member.name}!",  # Custom title
                color=nextcord.Color.blue()
            )
            embed.set_image(url=gif_url)
            embed.set_author(name="", icon_url=i.user.avatar.url)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(f"No GIFs found for '{search_term}'")


    @nextcord.slash_command(name="pat", description="Search for pat GIFs using Tenor API", guild_ids=[api.GuildID])
    async def pat(self, i: nextcord.Interaction, member: nextcord.Member):
        # Define the search term for the hug command
        search_term = "Anime pat"

        # Fetch a random GIF using the helper function
        gif_url = await self.fetch_random_gif(search_term)

        # Create and send the embed based on the result
        if gif_url:
            embed = nextcord.Embed(
                title=f"{i.user.display_name} pats {member.name}!",  # Custom title
                color=nextcord.Color.blue()
            )
            embed.set_image(url=gif_url)
            embed.set_author(name="", icon_url=i.user.avatar.url)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(f"No GIFs found for '{search_term}'")


    @nextcord.slash_command(name="cuddle", description="Search for cuddle GIFs using Tenor API", guild_ids=[api.GuildID])
    async def cuddle(self, i: nextcord.Interaction, member: nextcord.Member):
        # Define the search term for the hug command
        search_term = "Anime Cuddle"

        # Fetch a random GIF using the helper function
        gif_url = await self.fetch_random_gif(search_term)

        # Create and send the embed based on the result
        if gif_url:
            embed = nextcord.Embed(
                title=f"{i.user.display_name} cuddles with {member.name}!",  # Custom title
                color=nextcord.Color.blue()
            )
            embed.set_image(url=gif_url)
            embed.set_author(name="", icon_url=i.user.avatar.url)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(f"No GIFs found for '{search_term}'")

    @nextcord.slash_command(name="kill", description="Search for kill GIFs using Tenor API", guild_ids=[api.GuildID])
    async def kill(self, i: nextcord.Interaction, member: nextcord.Member):
        # Define the search term for the hug command
        search_term = "Anime Kill"

        # Fetch a random GIF using the helper function
        gif_url = await self.fetch_random_gif(search_term)

        # Create and send the embed based on the result
        if gif_url:
            embed = nextcord.Embed(
                title=f"{i.user.display_name} killed {member.name}!",  # Custom title
                color=nextcord.Color.blue()
            )
            embed.set_image(url=gif_url)
            embed.set_author(name="", icon_url=i.user.avatar.url)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(f"No GIFs found for '{search_term}'")

    @nextcord.slash_command(name="manipulate", description="Search for manipulate GIFs using Tenor API", guild_ids=[api.GuildID])
    async def manipulate(self, i: nextcord.Interaction, member: nextcord.Member):
        # Define the search term for the hug command
        search_term = "Anime Manipulation"

        # Fetch a random GIF using the helper function
        gif_url = await self.fetch_random_gif(search_term)

        # Create and send the embed based on the result
        if gif_url:
            embed = nextcord.Embed(
                title=f"{i.user.display_name} maniplated {member.name}!",  # Custom title
                color=nextcord.Color.blue()
            )
            embed.set_image(url=gif_url)
            embed.set_author(name="", icon_url=i.user.avatar.url)
            await i.response.send_message(embed=embed)
        else:
            await i.response.send_message(f"No GIFs found for '{search_term}'")

            
        
def setup(bot: commands.Bot):
    print("Anime Cog Registered")
    bot.add_cog(Anime(bot))

