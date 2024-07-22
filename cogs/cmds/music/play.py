import nextcord
from nextcord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from datetime import datetime
import api

# Setup your bot and intents
intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Music Queue class to manage the song queue
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

# Initialize the MusicQueue
music_queue = MusicQueue()

# Music commands cog
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.last_played_time = datetime.utcnow()

    @nextcord.slash_command(name="play", description="Play a song from YouTube.", guild_ids=[api.GuildID])
    async def play(self, interaction: nextcord.Interaction, url: str):
        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to use this command.")
            return

        if interaction.guild.voice_client is None:
            await interaction.user.voice.channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'default_search': 'ytsearch',
            'noplaylist': False,
            'ignoreerrors': True,
            'extractaudio': True,
            'skip_download': True,
            'simulate': True,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                entry = info['entries'][0]
            else:
                entry = info

            song = {
                'url': entry['url'],
                'title': entry['title'],
                'requester': interaction.user
            }

            music_queue.add_to_queue(interaction.guild.id, song)

            if not self.is_playing:
                await self.play_next(interaction)

            await interaction.response.send_message(f"Added to queue: {song['title']}")

    @nextcord.slash_command(name="skip", description="Skip the currently playing song.", guild_ids=[api.GuildID])
    async def skip(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await self.play_next(interaction)
            await interaction.response.send_message("Skipped the current song.")
        else:
            await interaction.response.send_message("No song is currently playing.")

    @nextcord.slash_command(name="pause", description="Pause the currently playing song.", guild_ids=[api.GuildID])
    async def pause(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("Paused the song.")
        else:
            await interaction.response.send_message("No song is currently playing.")

    @nextcord.slash_command(name="resume", description="Resume the paused song.", guild_ids=[api.GuildID])
    async def resume(self, interaction: nextcord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("Resumed the song.")
        else:
            await interaction.response.send_message("No song is currently paused.")

    @nextcord.slash_command(name="queue", description="Show the current song queue.", guild_ids=[api.GuildID])
    async def queue(self, interaction: nextcord.Interaction):
        queue = music_queue.get_queue(interaction.guild.id)
        if queue:
            message = "Current queue:\n" + "\n".join(f"{i + 1}. {song['title']}" for i, song in enumerate(queue))
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message("The queue is currently empty.")

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
            await interaction.response.send_message(f"Now playing: {song['title']}")
        else:
            self.is_playing = False
            music_queue.clear_queue(interaction.guild.id)
            await interaction.response.send_message("The queue is empty.")

def setup(bot: commands.Bot):
    print("Music Cog Registered")
    bot.add_cog(Music(bot))
