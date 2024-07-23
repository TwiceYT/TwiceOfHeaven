import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import lyricsgenius as lg
import re
import api

load_dotenv()
GENIUSTOKEN = os.getenv('GENIUSTOKEN')

class LyricsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="lyrics",
        description="Fetch the lyrics of a song",
        guild_ids=[api.GuildID]
    )
    async def lyrics(self, i: nextcord.Interaction, *, song_name: str):
        genius = lg.Genius(GENIUSTOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])

        lyrics = None
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

            for header, part in zip(headers, cleaned_lyrics):
                await i.response.send_message(f"**{header}**\n```{part}```")
                print(header)
                print(part, "\n")
        else:
            await i.response.send_message("Could not find lyrics.")

def setup(bot):
    bot.add_cog(LyricsCommand(bot))