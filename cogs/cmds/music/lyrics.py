import re
import nextcord
from nextcord.ext import commands
import lyricsgenius as lg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='config/config.env')

# Load Genius API token
genius_token = os.getenv("GENIUSTOKEN")
if not genius_token:
    raise ValueError("GENIUSTOKEN is missing from the environment variables.")
GENIUS_API = lg.Genius(genius_token, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])

# Define the Lyrics cog
class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="lyrics", description="Fetch the lyrics of a song")
    async def lyrics(self, interaction: nextcord.Interaction, *, song_name: str):
        # Acknowledge the interaction immediately
        await interaction.response.defer()

        # Search for the song lyrics using Genius API
        song = GENIUS_API.search_song(song_name)

        if song:
            lyrics = song.lyrics

            # Clean and format lyrics
            header_pattern = r'\[.*?\]'
            lyric_parts = re.split(header_pattern, lyrics)
            headers = re.findall(header_pattern, lyrics)
            headers = [header.strip('[]') for header in headers]

            cleaned_lyrics = []
            for part in lyric_parts[1:]:
                part = part.strip()
                part = re.sub(r'\d*Embed$', '', part).strip()
                if part:
                    cleaned_lyrics.append(part)

            # Combine all lyrics parts into a single formatted string
            full_lyrics = ""
            for header, part in zip(headers, cleaned_lyrics):
                full_lyrics += f"**{header}**\n{part}\n\n"

            # Ensure the lyrics fit within Discord's message limit
            if len(full_lyrics) > 4096:
                full_lyrics = full_lyrics[:4093] + "..."  # Truncate and add an ellipsis

            # Create and send an embed with the lyrics
            embed = nextcord.Embed(
                title=f"Lyrics for {song_name}",
                description=full_lyrics,
                color=0x1DB954  # Spotify green
            )
            await interaction.followup.send(embed=embed)
        else:
            # Send a message if no lyrics are found
            await interaction.followup.send(content="Lyrics not found. Please check the song name and try again.")

# Setup function to load the cog
def setup(bot: commands.Bot):
    bot.add_cog(Lyrics(bot))
