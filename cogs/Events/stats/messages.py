import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import api as api
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return  # Ignore messages sent by the bot itself

        if not message.guild:
            return  # Ignore messages sent in DMs

        guild_id = message.guild.id
        user_id = message.author.id
        username = message.author.name
        timestamp = datetime.utcnow()

        # Insert each message into the messages table
        cursor.execute("""
            INSERT INTO messages(user_id, user, timestamp, guild_id) VALUES (?, ?, ?, ?)
        """, (user_id, username, timestamp, guild_id))
        database.commit()

        # Update msgstats table
        cursor.execute("""
            SELECT msg FROM msgstats WHERE user_id = ? AND guild_id = ?
        """, (user_id, guild_id))
        result = cursor.fetchone()

        if result is None:
            # Insert new record if not exists
            cursor.execute("""
                INSERT INTO msgstats(user_id, user, msg, last_message_timestamp, guild_id) VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, 1, timestamp, guild_id))
        else:
            # Update existing record
            msgs = result[0] if result[0] is not None else 0
            msgs += 1
            cursor.execute("""
                UPDATE msgstats SET msg = ?, last_message_timestamp = ? WHERE user_id = ? AND guild_id = ?
            """, (msgs, timestamp, user_id, guild_id))

        database.commit()

        # Update economy table
        cursor.execute("""
            SELECT bank FROM economy WHERE user_id = ? AND guild_id = ?
        """, (user_id, guild_id))
        result = cursor.fetchone()

        if result is None:
            # Insert new record if not exists
            cursor.execute("""
                INSERT INTO economy(user_id, user, bank, guild_id) VALUES (?, ?, ?, ?)
            """, (user_id, username, 1, guild_id))
        else:
            # Update existing record
            bank = result[0] if result[0] is not None else 0
            bank += 1
            cursor.execute("""
                UPDATE economy SET bank = ? WHERE user_id = ? AND guild_id = ?
            """, (bank, user_id, guild_id))

        database.commit()

    @nextcord.slash_command(
        name="messages",
        description="See the amount of messages a user has sent!",
        guild_ids=[api.GuildID]
    )
    async def messages(self, i: nextcord.Interaction, member: nextcord.Member):
        cursor.execute(f"SELECT msg FROM msgstats WHERE user_id = ? AND guild_id = ?", (member.id, i.guild_id))
        result = cursor.fetchone()
        if result is None: 
            cursor.execute("""
                INSERT INTO msgstats(user_id, user, msg, guild_id) VALUES (?, ?, ?, ?)
            """, (member.id, member.name, 0, i.guild_id))
            database.commit()
            msg = 0
        else:
            msg = result[0]

        embed = nextcord.Embed(
            title="Message Stats",
            description=f"User {member.mention} has sent {msg} messages!",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.avatar.url)
        await i.response.send_message(embed=embed)

    @nextcord.slash_command(
        name="messages7days",
        description="See the amount of messages a user has sent in the past 7 days!",
        guild_ids=[api.GuildID]
    )
    async def messages7days(self, i: nextcord.Interaction, member: nextcord.Member):
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        cursor.execute("""
            SELECT COUNT(*) FROM messages WHERE user_id = ? AND timestamp >= ? AND guild_id = ?
        """, (member.id, seven_days_ago, i.guild_id))
        result = cursor.fetchone()

        msg_count = result[0]

        embed = nextcord.Embed(
            title="Message Stats (Past 7 Days)",
            description=f"User {member.mention} has sent {msg_count} messages in the past 7 days!",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.avatar.url)
        await i.response.send_message(embed=embed)

def setup(bot: commands.Bot):
    print("MessageStats Cog Registered")
    bot.add_cog(Messages(bot))
