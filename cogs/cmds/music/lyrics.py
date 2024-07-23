import re
import nextcord
from nextcord.ext import commands
import lyricsgenius as lg
import api

GENIUSTOKEN = 'your_genius_api_token_here'

class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="lyrics", description="Fetch the lyrics of a song", guild_ids=[api.GuildID])
    async def lyrics(self, interaction: nextcord.Interaction, *, song_name: str):
        # Acknowledge the interaction immediately with a deferred response
        await interaction.response.defer()

        # Perform the long-running task
        genius = lg.Genius(GENIUSTOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])
        song = genius.search_song(song_name)

        if song:
            lyrics = song.lyrics
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

            # Combine all lyrics parts into a single string
            full_lyrics = ""
            for header, part in zip(headers, cleaned_lyrics):
                full_lyrics += f"**{header}**\n{part}\n\n"

            # Create an embed with the full lyrics
            embed = nextcord.Embed(title=f"Lyrics for {song_name}", description=full_lyrics[:4096], color=0x1DB954)  # Limit to 4096 characters

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(content="Lyrics not found.")

def setup(bot: commands.Bot):
    bot.add_cog(Lyrics(bot))
