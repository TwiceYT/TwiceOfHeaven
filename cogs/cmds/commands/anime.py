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
TENOR_API_KEY = os.getenv("TenorAPI")  # Your Tenor API key
CLIENT_KEY = "Discord bot"  # Your client key

# Bot setup
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

class Anime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="kiss", description="Search for GIFs using Tenor API", guild_ids=[api.GuildID])
    async def kiss(self, i: nextcord.Interaction, member: nextcord.Member):
        # Make the API request to Tenor
        search_term="Anime Fast Kiss" 
        ckey = CLIENT_KEY
        apikey= TENOR_API_KEY

        response = requests.get(
                f"https://tenor.googleapis.com/v2/search?q={search_term}&key={apikey}&client_key={ckey}&limit=50"
            )
            
        if response.status_code == 200:
            data = json.loads(response.content)
            gifs = [result.get('media_formats', {}).get('gif', {}).get('url') for result in data.get('results', []) if result.get('media_formats', {}).get('gif', {}).get('url')]
            
            if gifs:
                # Select a random GIF URL from the list
                random_gif = random.choice(gifs)

                Embed = nextcord.Embed(
                    title=f"{i.user.display_name} kiss {member.name}!",  # Custom title similar to the example
                    color=nextcord.Color.blue()
                )
                # Add the GIF as the image of the embed
                Embed.set_image(url=random_gif)
                # Optionally, set the user's avatar as the thumbnail
                Embed.set_author(name="", icon_url=i.user.avatar.url)
                await i.response.send_message(embed=Embed)
            else:
                await i.response.send_message(f"No GIFs found for '{search_term}'")
        else:
            await i.response.send_message(f"Error fetching GIFs: {response.status_code}")

def setup(bot: commands.Bot):
    print("Anime Cog Registered")
    bot.add_cog(Anime(bot))

