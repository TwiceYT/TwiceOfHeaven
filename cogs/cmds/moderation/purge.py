import nextcord, asyncio
from nextcord.ext import commands, application_checks
import api
import sqlite3
import os
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")

intents = nextcord.Intents.all()

def get_purgelog_channel(i: nextcord.Interaction):
    with sqlite3.connect(DBFile) as database:
        cursor = database.cursor()
        cursor.execute('SELECT modlogs FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
        purgelog = cursor.fetchone()
        if purgelog:
            return purgelog[0]
        else:
            i.response.send_message("You need to set up your modlogs using /setup", ephemeral=True)
            return None

class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @application_checks.has_guild_permissions(manage_messages=True)
    @nextcord.slash_command(
        name="purge",
        description="Purge a specified amount of messages",
        guild_ids=[api.GuildID]
    )
    async def purge(self, i: nextcord.Interaction, amount: int = nextcord.SlashOption(name="amount", description="The amount of messages to purge.", required=True)):
        await i.response.defer()

        # Fetch and log purged messages
        purged_messages = await i.channel.purge(limit=amount+1)

        # Retrieve the purgelog channel
        purgelog = get_purgelog_channel(i)
        if purgelog is None:
            return  

        log_channel = i.guild.get_channel(purgelog)
        if log_channel:
            # Create a transcript of purged messages
            transcript = "Purged Messages Transcript:\n\n"
            for message in purged_messages:
                author = message.author
                content = message.content or "[No content]"
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                transcript += f"Author: {author}\nContent: {content}\nTimestamp: {timestamp}\n\n"

            # Ensure the subdirectory exists
            subdirectory = "transcripts_purge"
            if not os.path.exists(subdirectory):
                os.makedirs(subdirectory)

            # Save the transcript to a file in the subdirectory
            transcript_file_path = os.path.join(subdirectory, f"purge_transcript_{i.channel.id}.txt")
            with open(transcript_file_path, 'w') as file:
                file.write(transcript)

            # Send the transcript file
            await log_channel.send(file=nextcord.File(transcript_file_path, filename=f"purge_transcript_{i.channel.id}.txt"))

            # Optionally, delete the file after sending
            os.remove(transcript_file_path)

        # Send the Purge Embed
        await asyncio.sleep(2)
        embed = nextcord.Embed(
            title="Purged Messages",
            description=f"Purged {amount} messages from this channel.",
            color=nextcord.Color.green()
        )
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.avatar.url)
        await i.channel.send(embed=embed)

def setup(bot: commands.Bot):
    print("Purge Cog Registered")
    bot.add_cog(Purge(bot))
