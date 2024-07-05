import nextcord
from nextcord.ext import commands
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv
import os
import api

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        now = datetime.utcnow()

        if before.channel != after.channel:
            guild_id = member.guild.id
            
            if after.channel is not None:  # User joined a voice channel
                formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("INSERT OR IGNORE INTO voicestat VALUES (?, ?, ?, ?, ?)", (guild_id, member.id, member.name, formatted_now, 0))
                cursor.execute("UPDATE voicestat SET last_joined = ? WHERE guild_id = ? AND user_id = ?", (formatted_now, guild_id, member.id))
                database.commit()

            if before.channel is not None:  # User left a voice channel
                cursor.execute("SELECT last_joined FROM voicestat WHERE guild_id = ? AND user_id=?", (guild_id, member.id))
                result = cursor.fetchone()

                if result:
                    # Truncate milliseconds before parsing
                    join_time_str = result[0].split('.')[0]
                    join_time = datetime.strptime(join_time_str, "%Y-%m-%d %H:%M:%S")
                    total_time = now - join_time

                    # Update total time in the database
                    cursor.execute("UPDATE voicestat SET total = total + ? WHERE guild_id = ? AND user_id=?", (int(total_time.total_seconds()), guild_id, member.id))
                    database.commit()



    @nextcord.slash_command(
        name="voice",
        description="Fetch how long a user has been in voice channels in total",
        guild_ids=[api.GuildID]
    )
    async def voice(self, i: nextcord.Interaction, member: nextcord.Member):
        cursor.execute("SELECT total FROM voicestat WHERE user_id=? AND guild_id = ?", (member.id, i.guild.id,))
        result = cursor.fetchone()

        if result:
            total_seconds = result[0]
            total_time = timedelta(seconds=total_seconds)
            embed = nextcord.Embed(
                title="Voice Stats",
                description=f"User {member.name}'s total voice channel time",
            )
            embed.add_field(name="Total:", value=str(total_time), inline=False)
        else:
            embed = nextcord.Embed(
                title="Voice Stats",
                description=f"User {member.name} has not joined any voice channels",
            )

        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.avatar.url)
        await i.response.send_message(embed=embed)

def setup(bot: commands.Bot):
    print("Voice Cog Registered")
    bot.add_cog(Voice(bot))