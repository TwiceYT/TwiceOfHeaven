from pydub import AudioSegment
import pydub
import nextcord
from nextcord.ext import commands
import pytube
import os
import api

# Manually set ffmpeg and ffprobe paths
pydub.AudioSegment.converter = r"C:\PATH_Programs\ffmpeg.exe"
pydub.AudioSegment.ffprobe = r"C:\PATH_Programs\ffprobe.exe"

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class Mp3Conv(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="mp3",
        description="Convert any YouTube link to an MP3 file",
        guild_ids=[api.GuildID]
    )
    async def convert(self, i: nextcord.Interaction, url: str):
        await i.response.send_message("Starting download... Large files can take a while...", ephemeral=True)
        try:
            # Download YouTube video as audio
            yt = pytube.YouTube(url)
            video = yt.streams.filter(only_audio=True).first()
            if not video:
                await i.followup.send("No audio streams available for this video.")
                return

            output_path = video.download()
            base, ext = os.path.splitext(output_path)
            mp3_path = base + '.mp3'

            # Convert to MP3
            audio = AudioSegment.from_file(output_path)
            audio.export(mp3_path, format="mp3")

            if os.path.exists(mp3_path):
                await i.followup.send("Download complete. Uploading MP3 file!", ephemeral=True)
                await i.followup.send("Here is your downloaded Mp3!", file=nextcord.File(mp3_path))
            else:
                await i.followup.send("An error occurred: MP3 file not found.")
        except Exception as e:
            await i.followup.send(f"An error occurred: {e}")
        finally:
            # Clean up files
            if os.path.exists(output_path):
                os.remove(output_path)
            if os.path.exists(mp3_path):
                os.remove(mp3_path)

def setup(bot: commands.Bot):
    print("mp3 Cog Registered")
    bot.add_cog(Mp3Conv(bot))