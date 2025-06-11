import nextcord
from nextcord.ext import commands
import yt_dlp
import os
import api

# Set up intents and the bot
intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


DOWNLOAD_FOLDER = 'F:\pogrammering\Bot\Python\TwiceOfHeaven\Extra\downloadmp3s' 

# Ensure the directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

class Mp3Conv(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="mp3",
        description="Convert any YouTube link to an MP3 file",
        guild_ids=[api.GuildID]
    )
    async def convert(self, i: nextcord.Interaction, yturl: str):
        await i.response.send_message("Starting download... Large files can take a while... Please be patient!",)
        output_path = None
        try:
            # Set up yt-dlp options to download only the single video, ignoring playlists
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # Save the file in the download folder
                'noplaylist': True,  # This ensures only the video in the URL is downloaded
            }

            # Download and convert to MP3
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(yturl, download=True)  # Ensure it downloads
                if info_dict and "title" in info_dict:
                    output_path = os.path.join(DOWNLOAD_FOLDER, f"{info_dict['title']}.mp3")  # Manually create expected MP3 path

                    if os.path.exists(output_path):
                        await i.followup.send("Download complete. Uploading MP3 file!", ephemeral=True)
                        await i.followup.send("Here is your downloaded MP3!", file=nextcord.File(output_path))
                    else:
                        await i.followup.send("An error occurred: MP3 file not found.")
                else:
                    await i.followup.send("An error occurred: Could not retrieve video information.")

        except Exception as e:
            await i.followup.send(f"An error occurred: {e}")
        finally:
            # Clean up files
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception as cleanup_error:
                    print(f"Error cleaning up video file: {cleanup_error}")

            mp3_path = output_path.rsplit('.', 1)[0] + '.mp3'
            if mp3_path and os.path.exists(mp3_path):
                try:
                    os.remove(mp3_path)
                except Exception as cleanup_error:
                    print(f"Error cleaning up MP3 file: {cleanup_error}")

def setup(bot: commands.Bot):
    print("mp3 Cog Registered")
    bot.add_cog(Mp3Conv(bot))
