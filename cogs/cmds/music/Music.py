import nextcord
from nextcord.ext import commands
import yt_dlp as youtube_dl
from datetime import datetime
import api

class MusicQueue:
    def __init__(self):
        self.queues = {}
        self.current_songs = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    def add_to_queue(self, guild_id, song):
        self.get_queue(guild_id).append(song)

    def clear_queue(self, guild_id):
        self.queues[guild_id] = []

    def set_current_song(self, guild_id, song):
        self.current_songs[guild_id] = song

    def get_current_song(self, guild_id):
        return self.current_songs.get(guild_id)

    def shuffle_queue(self, guild_id):
        from random import shuffle
        queue = self.get_queue(guild_id)
        shuffle(queue)

# Initialize the MusicQueue
music_queue = MusicQueue()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False

    @nextcord.slash_command(name="play", description="Play a song from YouTube.")
    async def play(self, interaction: nextcord.Interaction, url: str):
        await interaction.response.defer()

        if interaction.user.voice is None:
            await self.safe_send_message(interaction, "You need to be in a voice channel to use this command.")
            return

        if interaction.guild.voice_client is None:
            await interaction.user.voice.channel.connect()

        if "spotify.com" in url:
            await self.safe_send_message(interaction, "Please use a YouTube link instead of a Spotify link.")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'default_search': 'ytsearch',
            'noplaylist': True,
            'ignoreerrors': True,
            'extractaudio': True,
            'skip_download': True,
            'simulate': True,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
        }

        try:
            search_query = url if ("youtu.be" in url or "youtube.com" in url) else url

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                print("Extracted Info:", info)
                
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                elif 'url' in info:
                    entry = info
                else:
                    await self.safe_send_message(interaction, "No results found.")
                    return

                song = {
                    'url': entry['url'],
                    'title': entry['title'],
                    'requester': interaction.user
                }

                music_queue.add_to_queue(interaction.guild.id, song)

                if not self.is_playing:
                    await self.play_next(interaction)

                await self.safe_send_message(interaction, f"Added to queue: {song['title']}")
        except Exception as e:
            await self.safe_send_message(interaction, f"An error occurred: {str(e)}")
            print(f"Error details: {e}")

    @nextcord.slash_command(name="skip", description="Skip the currently playing song.")
    async def skip(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await self.play_next(interaction)
            await self.safe_send_message(interaction, "Skipped the current song.")
        else:
            await self.safe_send_message(interaction, "No song is currently playing.")

    @nextcord.slash_command(name="pause", description="Pause the currently playing song.")
    async def pause(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await self.safe_send_message(interaction, "Paused the song.")
        else:
            await self.safe_send_message(interaction, "No song is currently playing.")

    @nextcord.slash_command(name="resume", description="Resume the paused song.")
    async def resume(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await self.safe_send_message(interaction, "Resumed the song.")
        else:
            await self.safe_send_message(interaction, "No song is currently paused.")

    @nextcord.slash_command(name="queue", description="Show the current song queue.")
    async def queue(self, interaction: nextcord.Interaction):
        queue = music_queue.get_queue(interaction.guild.id)
        if queue:
            message = "Current queue:\n" + "\n".join(f"{i + 1}. {song['title']}" for i, song in enumerate(queue))
            embed = nextcord.Embed(
                title="Music Queue",
                description=message,
                color=nextcord.Color.gold()
            )
            await self.safe_send_message(interaction, "", embed=embed)
        else:
            await self.safe_send_message(interaction, "The queue is currently empty.")


    @nextcord.slash_command(name="disconnect", description="Disconnects the bot and clears the current queue.", guild_ids=[api.GuildID])
    async def disconnect(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            music_queue.clear_queue(interaction.guild.id)
            await self.safe_send_message(interaction, "Bot disconnected and cleared the queue.")
        else:
            await self.safe_send_message(interaction, "Bot was not connected to a voice channel.")

    @nextcord.slash_command(name="clear", description="Clear the music queue.")
    async def clear(self, interaction: nextcord.Interaction):
        music_queue.clear_queue(interaction.guild.id)
        await self.safe_send_message(interaction, "The queue has been cleared!")

    @nextcord.slash_command(name="shuffle", description="Shuffle the music queue.", )
    async def shuffle(self, interaction: nextcord.Interaction):
        music_queue.shuffle_queue(interaction.guild.id)
        await self.safe_send_message(interaction, "The queue has been shuffled!")

    async def play_next(self, interaction: nextcord.Interaction):
        if len(music_queue.get_queue(interaction.guild.id)) > 0:
            song = music_queue.get_queue(interaction.guild.id).pop(0)
            music_queue.set_current_song(interaction.guild.id, song)
            self.is_playing = True

            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn -b:a 320k -ar 48000',
            }

            interaction.guild.voice_client.stop()
            interaction.guild.voice_client.play(
                nextcord.FFmpegPCMAudio(executable="ffmpeg", source=song['url'], **FFMPEG_OPTIONS),
                after=lambda e: self.bot.loop.create_task(self.play_next(interaction))
            )
            await self.safe_send_message(interaction, f"Now playing: {song['title']}")
        else:
            self.is_playing = False
            music_queue.clear_queue(interaction.guild.id)
            await self.safe_send_message(interaction, "The queue is empty.")

    async def safe_send_message(self, interaction: nextcord.Interaction, message: str, embed=None):
        try:
            if embed is None:
                if interaction.response.is_done():
                    await interaction.followup.send(message)
                else:
                    await interaction.response.send_message(message)
            else:
                if interaction.response.is_done():
                    await interaction.followup.send(message, embed=embed)
                else:
                    await interaction.response.send_message(message, embed=embed)
        except nextcord.errors.NotFound as e:
            print(f"Failed to send message: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
